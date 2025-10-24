"""
Module: parsers.content_quality
Purpose: Content Quality Assessment and Scoring
Location: parsers/content_quality.py

Description:
    Система оценки качества контента новостей с поддержкой:
    - Language detection
    - HTML cleaning
    - Content length validation
    - Paywall detection
    - Quality scoring

Author: PulseAI Team
Last Updated: January 2025
"""

import re
import logging
from typing import Dict, Optional, Tuple
import bleach
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


class ContentQualityScorer:
    """
    Система оценки качества контента новостей
    """

    def __init__(self):
        # Paywall detection patterns
        self.paywall_patterns = [
            r"subscribe.*to.*continue",
            r"paywall",
            r"premium.*content",
            r"free.*articles.*remaining",
            r"sign.*up.*to.*read",
            r"subscribe.*for.*unlimited",
            r"limited.*time.*offer",
            r"exclusive.*content",
        ]

        # Language whitelist from config
        self.supported_languages = ["en", "ru", "uk", "pl"]

        # Quality thresholds
        self.min_content_length = 100
        self.min_title_length = 10

        # HTML cleaning settings
        self.allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "b",
            "i",
            "u",
            "a",
            "blockquote",
            "ul",
            "ol",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]
        self.allowed_attributes = {"a": ["href"]}

    def clean_html_content(self, content: str) -> str:
        """
        Очистка HTML контента с сохранением структуры

        Args:
            content: HTML контент для очистки

        Returns:
            Очищенный HTML без script, style и других опасных элементов
        """
        if not content:
            return ""

        try:
            # Use bleach to clean HTML
            cleaned = bleach.clean(content, tags=self.allowed_tags, attributes=self.allowed_attributes, strip=True)
            return cleaned.strip()
        except Exception as e:
            logger.debug(f"HTML cleaning failed: {e}")
            # Fallback: strip all HTML tags
            return re.sub(r"<[^>]+>", "", content).strip()

    def detect_language(self, text: str) -> Optional[str]:
        """
        Определение языка текста

        Args:
            text: Текст для анализа

        Returns:
            Код языка (en, ru, etc.) или None если не удалось определить
        """
        if not text or len(text.strip()) < 20:
            return None

        try:
            language = detect(text)
            return language if language in self.supported_languages else None
        except LangDetectException as e:
            logger.debug(f"Language detection failed: {e}")
            return None

    def is_paywall_content(self, content: str, title: str = "") -> bool:
        """
        Детектирование paywall контента

        Args:
            content: Содержимое статьи
            title: Заголовок статьи

        Returns:
            True если контент выглядит как paywall
        """
        combined_text = f"{title} {content}".lower()

        for pattern in self.paywall_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                logger.debug(f"Paywall detected with pattern: {pattern}")
                return True

        return False

    def calculate_content_quality(self, title: str, content: str, url: str = "") -> Dict[str, any]:
        """
        Комплексная оценка качества контента

        Args:
            title: Заголовок статьи
            content: Содержимое статьи
            url: URL статьи

        Returns:
            Словарь с оценками и метаданными
        """
        result = {
            "score": 0.0,
            "language": None,
            "is_paywall": False,
            "content_length": 0,
            "title_length": 0,
            "issues": [],
        }

        if not title or not content:
            result["issues"].append("missing_title_or_content")
            return result

        # Clean HTML content
        clean_content = self.clean_html_content(content)
        clean_title = self.clean_html_content(title)

        result["content_length"] = len(clean_content.strip())
        result["title_length"] = len(clean_title.strip())

        # Check basic requirements
        if result["content_length"] < self.min_content_length:
            result["issues"].append(f'content_too_short_{result["content_length"]}')

        if result["title_length"] < self.min_title_length:
            result["issues"].append(f'title_too_short_{result["title_length"]}')

        # Language detection
        language_text = f"{clean_title} {clean_content}"
        result["language"] = self.detect_language(language_text)

        if not result["language"]:
            result["issues"].append("unsupported_language")

        # Paywall detection
        result["is_paywall"] = self.is_paywall_content(clean_content, clean_title)
        if result["is_paywall"]:
            result["issues"].append("paywall_detected")

        # Quality scoring (0.0 to 1.0)
        score = 0.0

        # Content length score (0.4 weight)
        if result["content_length"] >= 500:
            score += 0.4
        elif result["content_length"] >= self.min_content_length:
            score += 0.2

        # Title quality score (0.2 weight)
        if result["title_length"] >= 30 and result["title_length"] <= 200:
            score += 0.2
        elif result["title_length"] >= self.min_title_length:
            score += 0.1

        # Language score (0.2 weight)
        if result["language"] in self.supported_languages:
            score += 0.2

        # No paywall score (0.2 weight)
        if not result["is_paywall"]:
            score += 0.2

        result["score"] = round(score, 2)

        return result

    def should_process_content(
        self, title: str, content: str, url: str = "", min_quality: float = 0.3
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Определение стоит ли обрабатывать контент

        Args:
            title: Заголовок статьи
            content: Содержимое статьи
            url: URL статьи
            min_quality: Минимальный порог качества

        Returns:
            Кортеж (should_process, quality_info)
        """
        quality_info = self.calculate_content_quality(title, content, url)
        should_process = (
            quality_info["score"] >= min_quality
            and not quality_info["is_paywall"]
            and quality_info["language"] is not None
        )

        return should_process, quality_info
