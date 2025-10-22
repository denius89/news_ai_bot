"""
Module: parsers.deduplication
Purpose: Advanced news deduplication using SimHash and MinHash
Location: parsers/deduplication.py

Description:
    Система дедупликации новостей с использованием:
    - SimHash для определения схожих контентов
    - MinHash для общих слов и фраз
    - URL canonicalization
    - Configurable similarity thresholds

Author: PulseAI Team
Last Updated: January 2025
"""

import hashlib
import re
import logging
from typing import Dict, List
from urllib.parse import urlparse, parse_qs, urlunparse
from datasketch import MinHash, MinHashLSH
import simhash as simhash_lib

logger = logging.getLogger(__name__)


class NewsDeduplicator:
    """
    Система дедупликации новостей с SimHash и MinHash
    """

    def __init__(self, simhash_threshold: int = 3, minhash_threshold: float = 0.8):
        """
        Инициализация дедупликатора

        Args:
            simhash_threshold: Максимальная разница в SimHash для дубликатов
            minhash_threshold: Минимальное сходство MinHash для дубликатов
        """
        self.simhash_threshold = simhash_threshold
        self.minhash_threshold = minhash_threshold

        # LSH indexes for efficient searching (MinHash only for now)
        self.minhash_lsh = MinHashLSH(threshold=minhash_threshold, num_perm=128)

        # Storage for hashes and metadata
        self.simhash_store: Dict[str, int] = {}  # Store SimHash as integer
        self.minhash_store: Dict[str, MinHash] = {}
        self.news_metadata: Dict[str, Dict] = {}

        # URL patterns to remove from comparison
        self.url_cleanup_patterns = [
            r"utm_[a-z_]+\=[^&]*",
            r"fbclid\=[^&]*",
            r"gclid\=[^&]*",
            r"ref\=[^&]*",
            r"source\=[^&]*",
        ]

    def canonicalize_url(self, url: str) -> str:
        """
        Каноникализация URL для лучшей дедупликации

        Args:
            url: Исходный URL

        Returns:
            Каноникализированный URL
        """
        if not url:
            return ""

        try:
            parsed = urlparse(url.lower().strip())

            # Remove common tracking parameters
            query_parts = []
            if parsed.query:
                query_params = parse_qs(parsed.query, keep_blank_values=False)

                # Remove tracking parameters
                clean_params = {}
                for key, values in query_params.items():
                    key_clean = key.lower()
                    should_remove = any(
                        re.match(pattern.replace("=", "="), f"{key_clean}=") for pattern in self.url_cleanup_patterns
                    )
                    if not should_remove and key_clean not in [
                        "utm_source",
                        "utm_medium",
                        "utm_campaign",
                        "fbclid",
                        "gclid",
                    ]:
                        clean_params[key] = values[0] if values else ""

                # Rebuild query string
                if clean_params:
                    query_parts = [f"{k}={v}" for k, v in clean_params.items()]

            # Normalize path (remove trailing slash, lowercase)
            path = parsed.path.rstrip("/").lower()

            # Rebuild URL
            canonical_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc.lower(),
                    path,
                    parsed.params,
                    "&".join(query_parts) if query_parts else "",
                    parsed.fragment,
                )
            )

            return canonical_url

        except Exception as e:
            logger.debug(f"URL canonicalization failed for {url}: {e}")
            return url.lower().strip()

    def extract_text_features(self, text: str) -> List[str]:
        """
        Извлечение текстовых фич для дедупликации

        Args:
            text: Исходный текст

        Returns:
            Список нормализованных фич
        """
        if not text:
            return []

        # Normalize text
        text = re.sub(r"\s+", " ", text.lower().strip())

        # Split into words and filter
        words = re.findall(r"\b[a-zа-яё]{3,}\b", text)

        # Remove common stop words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "и",
            "в",
            "на",
            "с",
            "по",
            "для",
            "из",
            "за",
            "от",
            "до",
            "под",
            "над",
        }

        features = [w for w in words if w not in stop_words and len(w) > 2]

        # Add bi-grams for better matching
        bi_grams = []
        for i in range(len(features) - 1):
            bi_gram = f"{features[i]}_{features[i+1]}"
            bi_grams.append(bi_gram)

        return features + bi_grams

    def compute_simhash(self, text: str) -> int:
        """
        Вычисление SimHash для текста

        Args:
            text: Текст для хеширования

        Returns:
            SimHash как integer
        """
        features = self.extract_text_features(text)
        return simhash_lib.Simhash(" ".join(features)).value

    def compute_minhash(self, text: str) -> MinHash:
        """
        Вычисление MinHash для текста

        Args:
            text: Текст для хеширования

        Returns:
            MinHash объект
        """
        features = self.extract_text_features(text)
        mh = MinHash(num_perm=128)

        for feature in features:
            mh.update(feature.encode("utf-8"))

        return mh

    def add_news_item(self, news_id: str, title: str, content: str, url: str = "") -> Dict[str, any]:
        """
        Добавление новости в индекс дедупликации

        Args:
            news_id: Уникальный ID новости
            title: Заголовок новости
            content: Содержимое новости
            url: URL новости

        Returns:
            Информация о найденных дубликатах
        """
        # Prepare text for analysis
        combined_text = f"{title} {content}".strip()
        canonical_url = self.canonicalize_url(url)
        url_hash = hashlib.md5(canonical_url.encode()).hexdigest() if url else ""

        # Check for exact URL duplicates first
        if url_hash and url_hash in self.news_metadata:
            existing_item = self.news_metadata[url_hash]
            return {
                "is_duplicate": True,
                "duplicate_type": "exact_url",
                "similarity_score": 1.0,
                "existing_item": existing_item,
            }

        # Compute hashes
        text_simhash = self.compute_simhash(combined_text)
        text_minhash = self.compute_minhash(combined_text)

        # Find similar items using MinHash LSH
        similar_minhash = list(self.minhash_lsh.query(text_minhash))

        # Check for high similarity matches
        best_match = None
        best_similarity = 0.0
        match_type = None

        # Check SimHash matches manually (since we don't have LSH for it)
        for existing_id, existing_simhash in self.simhash_store.items():
            if existing_id == news_id:
                continue

            # Calculate SimHash distance
            current_simhash = simhash_lib.Simhash("", f=64)
            current_simhash.value = text_simhash

            existing_simhash_obj = simhash_lib.Simhash("", f=64)
            existing_simhash_obj.value = existing_simhash

            distance = current_simhash.distance(existing_simhash_obj)
            similarity = 1.0 - (distance / 64.0)  # Normalize to 0-1

            if similarity > best_similarity and distance <= self.simhash_threshold:
                best_similarity = similarity
                best_match = existing_id
                match_type = "simhash"

        # Check MinHash matches (for similar content with different wording)
        for similar_id in similar_minhash:
            if similar_id == news_id or similar_id == best_match:
                continue

            existing_minhash = self.minhash_store.get(similar_id)
            if existing_minhash:
                similarity = text_minhash.jaccard(existing_minhash)

                if similarity > best_similarity and similarity >= self.minhash_threshold:
                    best_similarity = similarity
                    best_match = similar_id
                    match_type = "minhash"

        # Determine if this is a duplicate
        is_duplicate = (match_type == "simhash" and best_similarity >= 0.8) or (
            match_type == "minhash" and best_similarity >= self.minhash_threshold
        )

        result = {
            "is_duplicate": is_duplicate,
            "duplicate_type": match_type,
            "similarity_score": best_similarity,
            "existing_item": None,
        }

        if best_match and is_duplicate:
            result["existing_item"] = self.news_metadata.get(best_match, {})

        # Add to indexes if not a duplicate
        if not is_duplicate:
            # Store in LSH index (MinHash only)
            self.minhash_lsh.insert(news_id, text_minhash)

            # Store hashes and metadata
            self.simhash_store[news_id] = text_simhash
            self.minhash_store[news_id] = text_minhash

            metadata = {
                "id": news_id,
                "title": title,
                "content_length": len(combined_text),
                "canonical_url": canonical_url,
                "url_hash": url_hash,
            }

            self.news_metadata[news_id] = metadata
            if url_hash:
                self.news_metadata[url_hash] = metadata

        return result

    def get_stats(self) -> Dict[str, int]:
        """Получение статистики дедупликации"""
        return {
            "total_items": len(self.news_metadata),
            "simhash_items": len(self.simhash_store),
            "minhash_items": len(self.minhash_store),
        }
