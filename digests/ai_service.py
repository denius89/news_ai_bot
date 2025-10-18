"""
AI Digest Service - centralized AI-powered digest generation.

This module contains the main DigestAIService class that handles:
- News digest generation with AI analysis
- Fallback to simple format when OpenAI API is not available
- Date formatting and news limiting (max 8 items)
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from models.news import NewsItem
from utils.text.formatters import format_date
from utils.ai.ai_client import ask_async
from digests.prompts import get_prompt_for_category, PROMPTS as LEGACY_PROMPTS

try:
    from digests.prompts_v2 import build_prompt, STYLE_CARDS, CATEGORY_CARDS

    PROMPTS_V2_AVAILABLE = True
except ImportError:
    PROMPTS_V2_AVAILABLE = False

try:
    from digests.multistage_generator import generate_multistage_digest

    MULTISTAGE_AVAILABLE = True
except ImportError:
    MULTISTAGE_AVAILABLE = False

try:
    from digests.rag_system import get_rag_context

    RAG_SYSTEM_AVAILABLE = True
except ImportError:
    RAG_SYSTEM_AVAILABLE = False

try:
    from digests.personalization import PersonalizedDigestGenerator

    PERSONALIZATION_AVAILABLE = True
except ImportError:
    PERSONALIZATION_AVAILABLE = False

try:
    from ai_modules.personas import select_persona_for_context
    from ai_modules.news_graph import StoryContextManager
    from ai_modules.feedback_loop import FeedbackAnalyzer

    SUPER_JOURNALIST_V3_AVAILABLE = True
except ImportError:
    SUPER_JOURNALIST_V3_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DigestConfig:
    """Configuration for digest generation."""

    max_items: int = 8
    include_fallback: bool = True
    style: str = "analytical"
    use_multistage: bool = False  # Enable multi-stage generation with Chain-of-Thought
    use_rag: bool = True  # Enable RAG system with high-quality examples
    use_personalization: bool = True  # Enable personalization based on user profile
    use_events: bool = True  # Enable events fetching from database
    user_id: Optional[str] = None  # User ID for personalization
    audience: str = "general"  # Target audience type

    # Super Journalist v3 features
    use_personas: bool = False  # Enable automatic persona selection
    use_story_memory: bool = False  # Enable historical context from news graph
    use_feedback_loop: bool = False  # Enable feedback-based improvements


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
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            return bool(api_key)
        except Exception:
            return False

    def _get_max_tokens_for_length(self, length: str) -> int:
        """Calculate max_tokens based on length parameter."""
        if length == "short":
            return 500  # ~300 words
        elif length == "medium":
            return 1000  # ~600 words
        elif length == "long":
            return 2000  # ~1000 words
        else:
            return 1000  # default

    async def build_digest(
        self,
        news_items: List[NewsItem],
        style: str = "analytical",
        category: str = "all",
        length: str = "medium",
        subcategory: Optional[str] = None,
    ) -> str:
        """
        Build AI-powered digest from news items.

        Args:
            news_items: List of NewsItem objects
            style: Digest style (analytical, business, meme)
            category: News category (crypto, sports, markets, tech, world)
            length: Text length (short, medium, long)

        Returns:
            Formatted digest string
        """
        if not news_items:
            return self._build_empty_digest()

        # Limit to max_items
        limited_news = news_items[: self.config.max_items]

        if self._openai_available:
            # Don't catch exceptions, let them propagate (including timeout)
            return await self._llm_summarize(limited_news, style, category, length, subcategory)
        else:
            logger.info("OpenAI API not available, using fallback digest")
            return self._build_fallback_digest(limited_news)

    async def _llm_summarize(
        self,
        news_items: List[NewsItem],
        style: str,
        category: str = "world",
        length: str = "medium",
        subcategory: Optional[str] = None,
    ) -> str:
        """
        Generate AI-powered summary using OpenAI.

        Args:
            news_items: List of news items to summarize
            style: Summary style
            category: News category for context
            length: Text length (short, medium, long)

        Returns:
            AI-generated digest text
        """
        # Prepare news data for AI
        news_data = []
        for item in news_items:
            news_data.append(
                {
                    "title": item.title,
                    "content": item.content or "",
                    "published_at": item.published_at_fmt if item.published_at else "Unknown",
                    "source": item.source or "Unknown",
                    "credibility": item.credibility or 0.0,
                    "importance": item.importance or 0.0,
                    "subcategory": item.subcategory,  # Добавляем подкатегорию
                }
            )

        # Определить наиболее частую подкатегорию из новостей
        subcategory = None
        if news_data:
            from collections import Counter

            subcats = [item.get("subcategory") for item in news_data if item.get("subcategory")]
            if subcats:
                subcategory = Counter(subcats).most_common(1)[0][0]

        # Получить события с учетом подкатегории
        events = await self._fetch_relevant_events(news_items, category, subcategory)

        # Try multi-stage generation if enabled and available
        if self.config.use_multistage and MULTISTAGE_AVAILABLE:
            try:
                logger.info("Using multi-stage generation with Chain-of-Thought")
                result = await generate_multistage_digest(
                    news_items=news_items,
                    category=category,
                    subcategory=subcategory,
                    style=style,
                    events=events,
                    use_reasoning=True,
                    use_rag=self.config.use_rag,
                )

                logger.info(
                    f"Multi-stage generation completed: {result['stats']['word_count']} words, {result['stats']['generation_time_sec']:.2f}s"
                )
                return result["text"]

            except Exception as e:
                logger.warning(f"Multi-stage generation failed, falling back to standard: {e}")

        # Create prompt based on style and category
        prompt = await self._create_prompt(news_data, events, style, category, length, subcategory, news_items)
        logger.info(f"Created prompt length: {len(prompt)}")
        logger.info(f"News data count: {len(news_data)}")

        # Calculate max_tokens and timeout based on length
        max_tokens = self._get_max_tokens_for_length(length)
        timeout_seconds = 30.0 if length == "long" else 15.0  # Longer timeout for long digests
        logger.info(f"Using max_tokens={max_tokens}, timeout={timeout_seconds}s for length={length}")

        # Call OpenAI API with timeout
        import asyncio

        try:
            response = await asyncio.wait_for(
                ask_async(prompt=prompt, style=style, max_tokens=max_tokens), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"OpenAI API timeout after {timeout_seconds} seconds for length={length}")
            raise  # Re-raise the timeout error instead of using fallback

        logger.info(f"AI response length: {len(response) if response else 0}")
        logger.info(f"AI response preview: {response[:200] if response else 'EMPTY'}")

        # Process response - check if it's JSON and convert to HTML
        if response:
            # Import JSON formatter
            from digests.json_formatter import format_json_digest_to_html, clean_json_from_text

            # Check if response is JSON
            if response.strip().startswith("{") and response.strip().endswith("}"):
                logger.info("Converting JSON response to HTML")
                response = format_json_digest_to_html(response)
            else:
                # Clean any JSON blocks from text
                response = clean_json_from_text(response)

            # Clean HTML containers if AI generated them despite instructions
            import re

            # Remove HTML document structure
            response = re.sub(r"<!DOCTYPE[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"<html[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"</html>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"<head[^>]*>.*?</head>", "", response, flags=re.DOTALL | re.IGNORECASE)
            response = re.sub(r"<body[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"</body>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"<style[^>]*>.*?</style>", "", response, flags=re.DOTALL | re.IGNORECASE)
            # Remove problematic containers
            response = re.sub(r"<div[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"</div>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"<p[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"</p>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"<span[^>]*>", "", response, flags=re.IGNORECASE)
            response = re.sub(r"</span>", "", response, flags=re.IGNORECASE)
            response = response.strip()

        # Don't add fallback section - let AI handle it naturally

        return response

    async def _fetch_relevant_events(
        self, news_items: List[NewsItem], category: str, subcategory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить релевантные события из БД."""
        try:
            # Проверка настроек
            if not self.config.use_events:
                logger.info("Events disabled by config")
                return []

            # Импорт сервиса событий
            from database.events_service import get_events_service

            events_service = get_events_service()

            # Определяем период
            from datetime import timezone
            import time

            now = datetime.now(timezone.utc)
            start = now - timedelta(hours=12)
            end = now + timedelta(days=2)

            # ✅ ЧИТАЕМ ИЗ БД (быстро!)
            start_time = time.time()
            all_events = await events_service.get_events_by_date_range(
                from_date=start, to_date=end, category=category  # Фильтруем сразу
            )
            elapsed = time.time() - start_time

            logger.info(f"⏱️ Events from DB: {len(all_events)} events " f"in {elapsed*1000:.0f}ms for {category}")

            if not all_events:
                logger.info("No events found in database for period")
                return []

            # Фильтр по подкатегории
            if subcategory:
                all_events = [e for e in all_events if e.subcategory == subcategory]
                logger.info(f"After subcategory filter: {len(all_events)}")

            # Фильтр по важности
            relevant = [e for e in all_events if e.importance > 0.65]

            # Сортировка и топ-4
            relevant.sort(key=lambda x: x.importance, reverse=True)

            # Формируем результат
            result = []
            for e in relevant[:4]:
                result.append(
                    {
                        "title": e.title,
                        "date": e.starts_at.strftime("%d.%m.%Y"),
                        "description": e.description or "",
                        "importance": e.importance,
                        "subcategory": e.subcategory,
                    }
                )

            return result

        except Exception as e:
            logger.warning(f"Failed to fetch events: {e}")
            return []  # Graceful degradation

    async def _create_prompt(
        self,
        news_data: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        style: str,
        category: str = "world",
        length: str = "medium",
        subcategory: Optional[str] = None,
        news_items: Optional[List[NewsItem]] = None,
    ) -> str:
        """Create AI prompt based on news data, style, category, events, and RAG examples."""

        # ОПТИМИЗАЦИЯ: ограничиваем размер новостного текста для ускорения
        news_text = "\n\n".join(
            [
                (
                    f"{item['title'][:150]}...\n"  # Ограничиваем заголовок
                    f"{item['published_at']} | {item['source']}\n"
                    f"Достоверность: {item['credibility']:.1f} | Важность: {item['importance']:.1f}\n"
                    f"{item['content'][:150]}..."  # Сокращаем с 200 до 150 символов
                    if item["content"]
                    else "Описание недоступно"
                )
                for item in news_data[:6]  # Максимум 6 новостей вместо всех
            ]
        )

        # Добавляем RAG контекст если включен
        rag_context = ""
        if self.config.use_rag and RAG_SYSTEM_AVAILABLE and news_items:
            try:
                rag_context = get_rag_context(
                    category=category,
                    subcategory=subcategory,
                    style=style,
                    news_items=news_items,
                    max_samples=3,  # Возвращаем к 3 для качества, но с кэшированием это быстро
                )
                if rag_context:
                    # Разумное ограничение RAG контекста для баланса скорости/качества
                    if len(rag_context) > 3000:  # Увеличиваем с 2000 до 3000 для качества
                        rag_context = rag_context[:3000] + "..."
                    news_text = rag_context + "\n\n" + news_text
                    logger.info(f"Added RAG context: {len(rag_context)} characters")
            except Exception as e:
                logger.warning(f"Failed to add RAG context: {e}")

        # Добавляем персонализацию если включена (упрощенная версия для скорости)
        personalization_context = ""
        personalized_style = style
        personalized_tone = "neutral"
        personalized_audience = self.config.audience

        if self.config.use_personalization and PERSONALIZATION_AVAILABLE:
            try:
                # УМНАЯ ПЕРСОНАЛИЗАЦИЯ: без создания объектов, но с сохранением качества
                if self.config.audience in ["pro", "expert"]:
                    # Профессионалы получают более аналитический подход
                    if style not in ["analytical", "business", "technical"]:
                        personalized_style = "analytical"
                    else:
                        personalized_style = style
                    personalized_tone = "formal"
                    personalization_context = "Используй профессиональную терминологию и глубокий анализ."
                elif self.config.audience in ["beginner", "casual"]:
                    # Новички получают более простой подход
                    if style not in ["casual", "magazine"]:
                        personalized_style = "casual"
                    else:
                        personalized_style = style
                    personalized_tone = "friendly"
                    personalization_context = "Объясняй сложные термины простыми словами."
                else:  # general
                    personalized_style = style
                    personalized_tone = "neutral"
                    personalization_context = "Используй сбалансированный стиль для широкой аудитории."

                logger.info(f"Enhanced personalization - audience: {self.config.audience}, style: {personalized_style}")

            except Exception as e:
                logger.warning(f"Failed to add personalization, using defaults: {e}")
                personalized_style = style
                personalization_context = ""

        # Проверяем и исправляем стиль если нужно
        if personalized_style not in STYLE_CARDS:
            logger.warning(f"Invalid personalized_style '{personalized_style}', falling back to '{style}'")
            logger.warning(f"Available styles: {list(STYLE_CARDS.keys())}")
            personalized_style = style

        # Дополнительная проверка: если и оригинальный стиль не найден, используем analytical
        if personalized_style not in STYLE_CARDS:
            logger.warning(f"Original style '{style}' also not found in STYLE_CARDS, using 'analytical' as fallback")
            personalized_style = "analytical"

        logger.info(
            f"Style check: original='{style}', personalized='{personalized_style}', valid={personalized_style in STYLE_CARDS}"
        )

        # Добавляем исторический контекст если включена функция story memory
        story_context = ""
        if self.config.use_story_memory and SUPER_JOURNALIST_V3_AVAILABLE and news_items:
            try:
                from database.db_models import supabase

                if supabase:
                    context_manager = StoryContextManager(supabase)
                    story_context = context_manager.get_historical_context_for_digest(
                        news_items=[
                            {
                                "id": item.get("id"),
                                "title": item.get("title", ""),
                                "content": item.get("content", ""),
                                "importance": item.get("importance", 0.5),
                                "category": category,
                            }
                            for item in news_items
                        ],
                        category=category,
                        lookback_days=30,
                    )
                    if story_context:
                        news_text = story_context + "\n\n" + news_text
                        logger.info(f"Added historical context: {len(story_context)} characters")
            except Exception as e:
                logger.warning(f"Failed to add story context: {e}")

        # Используем новую систему prompts_v2 если доступна и стиль поддерживается
        if PROMPTS_V2_AVAILABLE and personalized_style in STYLE_CARDS and category in CATEGORY_CARDS:
            logger.info(f"Using prompts_v2 for style: {style}, category: {category}, subcategory: {subcategory}")

            # Добавляем события к news_text если есть
            if events:
                events_text = "\n\n📅 ПРЕДСТОЯЩИЕ СОБЫТИЯ:\n" + "\n".join(
                    [
                        (
                            f"• {e['title']} ({e['date']}) — важность: {e['importance']:.1f}"
                            f"\n  Подкатегория: {e['subcategory']}"
                            f"\n  {e['description']}"
                            if e["description"]
                            else ""
                        )
                        for e in events
                    ]
                )
                news_text += events_text + "\n\nЕсли события связаны с новостями, упомяни это естественно.\n"

            # Добавляем персонализацию к контексту новостей
            if personalization_context:
                news_text += f"\n\n🎯 ПЕРСОНАЛИЗИРОВАННЫЕ ТРЕБОВАНИЯ:\n{personalization_context}\n"

            # Создаем payload для новой системы
            input_payload = {
                "category": category,
                "style_profile": personalized_style,  # Используем персонализированный стиль
                "tone": personalized_tone,  # Используем персонализированный тон
                "length": length,  # Используем переданный параметр длины
                "audience": personalized_audience,  # Используем персонализированную аудиторию
                "news_text": news_text,
                "min_importance": 0.6,
                "min_credibility": 0.7,
            }

            # Вычисляем параметры для автоматического выбора персоны
            urgency = 0.5  # Default
            complexity = 0.5  # Default
            if news_data:
                avg_importance = sum(item.get("importance", 0.5) for item in news_data) / len(news_data)
                urgency = min(avg_importance, 1.0)  # Use importance as urgency proxy
                complexity = 0.8 if len(news_data) > 5 else 0.4  # More news = more complex

            try:
                # Используем новую функцию с поддержкой персон и подкатегорий
                if self.config.use_personas and SUPER_JOURNALIST_V3_AVAILABLE:
                    from digests.prompts_v2 import build_prompt_with_persona

                    system_prompt, user_prompt = build_prompt_with_persona(
                        input_payload,
                        persona_id=None,  # Auto-select
                        subcategory=subcategory,
                        urgency=urgency,
                        complexity=complexity,
                        news_count=len(news_data),
                        avg_importance=avg_importance if news_data else 0.5,
                    )
                else:
                    # Используем функцию с поддержкой подкатегорий без персон
                    from digests.prompts_v2 import build_prompt_with_subcategory

                    system_prompt, user_prompt = build_prompt_with_subcategory(input_payload, subcategory)

                final_prompt = f"{system_prompt}\n\n{user_prompt}"

                # ОПТИМИЗАЦИЯ: ограничиваем размер нового промпта
                if len(final_prompt) > 8000:
                    logger.warning(f"Prompts_v2 prompt too large ({len(final_prompt)} chars), truncating")
                    final_prompt = final_prompt[:8000] + "\n\n[Текст обрезан для ускорения]"

                logger.info(f"Prompts_v2 final size: {len(final_prompt)} characters")
                return final_prompt
            except ImportError:
                # Fallback на старую функцию
                system_prompt, user_prompt = build_prompt(input_payload)
                final_prompt = f"{system_prompt}\n\n{user_prompt}"
                if len(final_prompt) > 8000:
                    final_prompt = final_prompt[:8000] + "\n\n[Текст обрезан для ускорения]"
                return final_prompt
            except Exception as e:
                logger.warning(f"Failed to use prompts_v2, falling back to legacy: {e}")

        # Fallback к старой системе
        logger.info(f"Using legacy prompts for style: {personalized_style}, category: {category}")

        # Добавляем события к news_text если есть (для legacy системы тоже)
        if events:
            events_text = "\n\n📅 ПРЕДСТОЯЩИЕ СОБЫТИЯ:\n" + "\n".join(
                [f"• {e['title']} ({e['date']})" for e in events[:3]]  # Ограничиваем для legacy
            )
            news_text += events_text

        # Проверяем, поддерживает ли legacy система этот стиль
        fallback_style = personalized_style
        if personalized_style not in LEGACY_PROMPTS:
            logger.warning(f"Legacy system doesn't support style '{personalized_style}', falling back to 'analytical'")
            fallback_style = "analytical"

        formatted_prompt = get_prompt_for_category(fallback_style, category)

        # Создаем блок ссылок
        links_block = "\n".join([f"- {item['source']}: {item.get('link', 'No link')}" for item in news_data])

        # Форматируем финальный промт с данными
        final_prompt = formatted_prompt.replace("{text_block}", news_text).replace("{links_block}", links_block)

        # ОПТИМИЗАЦИЯ: ограничиваем финальный размер промпта для ускорения
        if len(final_prompt) > 8000:  # Ограничиваем общий размер промпта
            logger.warning(f"Prompt too large ({len(final_prompt)} chars), truncating to 8000")
            final_prompt = final_prompt[:8000] + "\n\n[Текст обрезан для ускорения]"

        logger.info(f"Final prompt size: {len(final_prompt)} characters")
        return final_prompt

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
async def generate_ai_digest(news_items: List[NewsItem], style: str = "analytical", max_items: int = 8) -> str:
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
