"""
AI Digest Service - centralized AI-powered digest generation.

This module contains the main DigestAIService class that handles:
- News digest generation with AI analysis
- Fallback to simple format when OpenAI API is not available
- Date formatting and news limiting (max 8 items)
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from models.news import NewsItem
from utils.formatters import format_date
from utils.ai_client import ask_async

logger = logging.getLogger(__name__)


@dataclass
class DigestConfig:
    """Configuration for digest generation."""
    max_items: int = 8
    include_fallback: bool = True
    style: str = "analytical"


class DigestAIService:
    """
    AI-powered digest generation service.
    
    Handles both AI-enhanced and fallback digest generation.
    """
    
    def __init__(self, config: Optional[DigestConfig] = None):
        self.config = config or DigestConfig()
        self._openai_available = self._check_openai_availability()
        
    def _check_openai_availability(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            import openai
            return bool(openai.api_key)
        except (ImportError, AttributeError):
            return False
    
    async def build_digest(
        self, 
        news_items: List[NewsItem], 
        style: str = "analytical"
    ) -> str:
        """
        Build AI-powered digest from news items.
        
        Args:
            news_items: List of NewsItem objects
            style: Digest style (analytical, business, meme)
            
        Returns:
            Formatted digest string
        """
        if not news_items:
            return self._build_empty_digest()
        
        # Limit to max_items
        limited_news = news_items[:self.config.max_items]
        
        if self._openai_available:
            try:
                return await self._llm_summarize(limited_news, style)
            except Exception as e:
                logger.warning(f"AI summarization failed, using fallback: {e}")
                return self._build_fallback_digest(limited_news)
        else:
            logger.info("OpenAI API not available, using fallback digest")
            return self._build_fallback_digest(limited_news)
    
    async def _llm_summarize(self, news_items: List[NewsItem], style: str) -> str:
        """
        Generate AI-powered summary using OpenAI.
        
        Args:
            news_items: List of news items to summarize
            style: Summary style
            
        Returns:
            AI-generated digest text
        """
        # Prepare news data for AI
        news_data = []
        for item in news_items:
            news_data.append({
                "title": item.title,
                "content": item.content or "",
                "published_at": item.published_at_fmt if item.published_at else "Unknown",
                "source": item.source or "Unknown",
                "credibility": item.credibility or 0.0,
                "importance": item.importance or 0.0
            })
        
        # Create prompt based on style
        prompt = self._create_prompt(news_data, style)
        
        # Call OpenAI API
        response = await ask_async(
            prompt=prompt,
            style=style,
            max_tokens=1000
        )
        
        # Add fallback section if not present
        if self.config.include_fallback and "<b>Почему это важно" not in response:
            response += self._get_fallback_section()
        
        return response
    
    def _create_prompt(self, news_data: List[Dict[str, Any]], style: str) -> str:
        """Create AI prompt based on news data and style."""
        
        news_text = "\n\n".join([
            f"📰 {item['title']}\n"
            f"📅 {item['published_at']} | 🔗 {item['source']}\n"
            f"📊 Достоверность: {item['credibility']:.1f} | Важность: {item['importance']:.1f}\n"
            f"📝 {item['content'][:200]}..." if item['content'] else "📝 Описание недоступно"
            for item in news_data
        ])
        
        style_instructions = {
            "analytical": "Проанализируй новости и объясни их значение для рынка",
            "business": "Сосредоточься на бизнес-аспектах и инвестиционных возможностях",
            "meme": "Пиши в легком, юмористическом стиле с эмодзи"
        }
        
        instruction = style_instructions.get(style, style_instructions["analytical"])
        
        return f"""
{instruction}

Новости:
{news_text}

Создай краткий дайджест (до 500 слов) с анализом и объяснением важности событий.
Используй HTML-разметку для форматирования.
"""
    
    def _build_fallback_digest(self, news_items: List[NewsItem]) -> str:
        """
        Build simple digest without AI when OpenAI is not available.
        
        Args:
            news_items: List of news items
            
        Returns:
            Simple formatted digest
        """
        digest_parts = ["📰 <b>Дайджест новостей</b>\n"]
        
        for i, item in enumerate(news_items, 1):
            date_str = format_date(item.published_at) if item.published_at else "—"
            credibility = f"{item.credibility:.1f}" if item.credibility else "—"
            importance = f"{item.importance:.1f}" if item.importance else "—"
            
            digest_parts.append(
                f"<b>{i}. {item.title}</b>\n"
                f"📅 {date_str} | 🔗 {item.source or 'Unknown'}\n"
                f"📊 Достоверность: {credibility} | Важность: {importance}\n"
            )
        
        # Add fallback section
        if self.config.include_fallback:
            digest_parts.append(self._get_fallback_section())
        
        return "\n".join(digest_parts)
    
    def _build_empty_digest(self) -> str:
        """Build digest for empty news list."""
        return "📰 <b>Дайджест новостей</b>\n\nСегодня новостей нет."
    
    def _get_fallback_section(self) -> str:
        """Get standard fallback section."""
        return """
<b>Почему это важно:</b>
— События влияют на рынок и инвестиции
— Важно для принятия финансовых решений
— Помогает понимать тренды и изменения
"""


# Convenience functions for backward compatibility
async def generate_ai_digest(
    news_items: List[NewsItem], 
    style: str = "analytical",
    max_items: int = 8
) -> str:
    """
    Generate AI digest from news items.
    
    Args:
        news_items: List of NewsItem objects
        style: Digest style
        max_items: Maximum number of items to include
        
    Returns:
        Generated digest text
    """
    config = DigestConfig(max_items=max_items)
    service = DigestAIService(config)
    return await service.build_digest(news_items, style)


def generate_fallback_digest(news_items: List[NewsItem], max_items: int = 8) -> str:
    """
    Generate fallback digest without AI.
    
    Args:
        news_items: List of NewsItem objects
        max_items: Maximum number of items to include
        
    Returns:
        Generated digest text
    """
    config = DigestConfig(max_items=max_items)
    service = DigestAIService(config)
    return service._build_fallback_digest(news_items[:max_items])
