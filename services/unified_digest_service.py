"""
Unified Digest Service for PulseAI.

This service consolidates both sync and async digest generation,
eliminating code duplication and providing consistent behavior.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from repositories.news_repository import NewsRepository
from models.news import NewsItem
from utils.formatters import format_news, format_ai_fallback
from digests.ai_summary import generate_batch_summary
from database.service import get_sync_service, get_async_service

logger = logging.getLogger(__name__)


class UnifiedDigestService:
    """
    Unified service for generating digests in both sync and async modes.
    """
    
    def __init__(self, async_mode: bool = False):
        """
        Initialize unified digest service.
        
        Args:
            async_mode: Whether to use async operations
        """
        self.async_mode = async_mode
        self.sync_service = get_sync_service()
        self.async_service = get_async_service()
        
        # Initialize news repository
        if async_mode:
            self.news_repo = None  # Will be initialized async
        else:
            from database.db_models import supabase
            self.news_repo = NewsRepository(supabase)
    
    async def _init_async(self):
        """Initialize async news repository."""
        if not self.async_mode or self.news_repo is not None:
            return
        
        try:
            # Initialize async service
            await self.async_service._init_async_client()
            
            # Create async news repository
            from database.async_db_models import init_async_supabase
            async_supabase = await init_async_supabase()
            self.news_repo = NewsRepository(async_supabase)
            
        except Exception as e:
            logger.error(f"Failed to initialize async digest service: {e}")
            raise
    
    def generate_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        ai: bool = False,
        style: str = "analytical",
    ) -> str:
        """
        Generate digest (normal or AI) based on parameters.
        
        Args:
            limit: Maximum number of news items
            categories: List of categories/subcategories to filter
            category: Single category for backward compatibility
            ai: If True, generate AI digest, else normal HTML digest
            style: Style for AI generation
            
        Returns:
            Formatted digest text
        """
        try:
            # Get news items - support both new and old API
            if categories is None and category is not None:
                categories = [category]  # Backward compatibility
            
            news_items = self.news_repo.get_recent_news(limit=limit, categories=categories)
            
            if not news_items:
                if ai:
                    cat_display = categories[0] if categories else category or "all"
                    return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."
                return format_news([], limit=None, with_header=True)
            
            if ai:
                cat_display = categories[0] if categories else category or "all"
                return self.generate_ai_digest(news_items, style=style, category=cat_display)
            else:
                return format_news(news_items, limit=limit, with_header=True)
                
        except Exception as e:
            logger.error(f"Error generating digest: {e}")
            return "⚠️ Ошибка при генерации дайджеста."
    
    async def async_generate_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
        ai: bool = False,
        style: str = "analytical",
    ) -> str:
        """
        Async version of generate_digest.
        """
        await self._init_async()
        
        try:
            # Get news items - support both new and old API
            if categories is None and category is not None:
                categories = [category]  # Backward compatibility
            
            news_items = await self.news_repo.async_get_recent_news(limit=limit, categories=categories)
            
            if not news_items:
                if ai:
                    cat_display = categories[0] if categories else category or "all"
                    return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."
                return format_news([], limit=None, with_header=True)
            
            if ai:
                cat_display = categories[0] if categories else category or "all"
                return await self.async_generate_ai_digest(news_items, style=style, category=cat_display)
            else:
                return format_news(news_items, limit=limit, with_header=True)
                
        except Exception as e:
            logger.error(f"Error generating async digest: {e}")
            return "⚠️ Ошибка при генерации дайджеста."
    
    def generate_ai_digest(
        self,
        news_items: List[NewsItem],
        style: str = "analytical",
        category: str = "all"
    ) -> str:
        """
        Generate AI-enhanced digest from news items.
        
        Args:
            news_items: List of news items
            style: Style for AI generation
            category: Category name for display
            
        Returns:
            AI-generated digest text
        """
        try:
            if not news_items:
                return f"AI DIGEST (cat={category}): Сегодня новостей нет."
            
            # Generate AI summary
            ai_summary = generate_batch_summary(news_items, style=style)
            
            if ai_summary:
                return f"🤖 AI DIGEST (cat={category}):\n\n{ai_summary}"
            else:
                # Fallback to formatted news
                formatted_news = format_news(news_items, limit=None, with_header=False)
                return f"🤖 AI DIGEST (cat={category}) - Fallback:\n\n{formatted_news}"
                
        except Exception as e:
            logger.error(f"Error generating AI digest: {e}")
            return "⚠️ Ошибка при генерации AI-дайджеста."
    
    async def async_generate_ai_digest(
        self,
        news_items: List[NewsItem],
        style: str = "analytical",
        category: str = "all"
    ) -> str:
        """
        Async version of generate_ai_digest.
        """
        try:
            if not news_items:
                return f"AI DIGEST (cat={category}): Сегодня новостей нет."
            
            # Generate AI summary in thread pool
            ai_summary = await asyncio.to_thread(generate_batch_summary, news_items, style=style)
            
            if ai_summary:
                return f"🤖 AI DIGEST (cat={category}):\n\n{ai_summary}"
            else:
                # Fallback to formatted news
                formatted_news = format_news(news_items, limit=None, with_header=False)
                return f"🤖 AI DIGEST (cat={category}) - Fallback:\n\n{formatted_news}"
                
        except Exception as e:
            logger.error(f"Error generating async AI digest: {e}")
            return "⚠️ Ошибка при генерации AI-дайджеста."
    
    def build_daily_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> str:
        """
        Build daily digest (backward compatibility).
        """
        return self.generate_digest(
            limit=limit,
            categories=categories,
            category=category,
            ai=False
        )
    
    def build_ai_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
        style: str = "analytical"
    ) -> str:
        """
        Build AI digest (backward compatibility).
        """
        return self.generate_digest(
            limit=limit,
            categories=categories,
            category=category,
            ai=True,
            style=style
        )
    
    async def async_build_daily_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> str:
        """
        Async build daily digest.
        """
        return await self.async_generate_digest(
            limit=limit,
            categories=categories,
            category=category,
            ai=False
        )
    
    async def async_build_ai_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
        style: str = "analytical"
    ) -> str:
        """
        Async build AI digest.
        """
        return await self.async_generate_digest(
            limit=limit,
            categories=categories,
            category=category,
            ai=True,
            style=style
        )


# Global service instances
_sync_digest_service: Optional[UnifiedDigestService] = None
_async_digest_service: Optional[UnifiedDigestService] = None


def get_sync_digest_service() -> UnifiedDigestService:
    """Get sync digest service instance."""
    global _sync_digest_service
    if _sync_digest_service is None:
        _sync_digest_service = UnifiedDigestService(async_mode=False)
    return _sync_digest_service


def get_async_digest_service() -> UnifiedDigestService:
    """Get async digest service instance."""
    global _async_digest_service
    if _async_digest_service is None:
        _async_digest_service = UnifiedDigestService(async_mode=True)
    return _async_digest_service


# Backward compatibility functions
def build_daily_digest(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_digest_service().build_daily_digest(*args, **kwargs)


def build_ai_digest(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_digest_service().build_ai_digest(*args, **kwargs)
