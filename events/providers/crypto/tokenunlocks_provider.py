"""
TokenUnlocks Provider for token unlock schedules.

Fetches token unlock events from TokenUnlocks.app.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("tokenunlocks_provider")


class TokenUnlocksProvider(BaseEventProvider):
    """
    Provider for token unlock schedules.

    Features:
    - Fetches token unlock events
    - No API key required
    - Tracks major token unlocks
    """

    def __init__(self):
        """Initialize TokenUnlocks provider."""
        super().__init__("tokenunlocks", "crypto")
        # Используем альтернативный публичный endpoint
        self.base_url = "https://www.tokenunlocks.app"
        self.api_key = os.getenv("TOKEN_UNLOCKS_API_KEY")  # Опционально

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from TokenUnlocks.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                self.session = aiohttp.ClientSession(headers=headers)

            # TokenUnlocks закрыл публичный API, но есть RSS альтернатива
            # Пробуем RSS endpoint (обычно публичный)
            url = f"{self.base_url}/rss"

            # Apply rate limit (conservative: 1 req/sec)
            await self.rate_limiter.acquire()

            async with self.session.get(url) as response:
                if response.status == 403:
                    logger.warning("TokenUnlocks API requires authentication - provider temporarily disabled")
                    logger.info("Добавьте TOKEN_UNLOCKS_API_KEY в .env для включения провайдера")
                    return []

                if response.status != 200:
                    logger.error(f"TokenUnlocks API error: {response.status}")
                    return []

                # Если это RSS - парсим XML
                content = await response.text()

                # Проверяем это RSS или JSON
                if content.strip().startswith("<"):
                    # RSS format - парсим через feedparser
                    import feedparser

                    feed = feedparser.parse(content)
                    unlocks = []

                    for entry in feed.entries[:50]:
                        # Извлекаем данные из RSS entry
                        unlocks.append(
                            {
                                "title": entry.get("title", ""),
                                "description": entry.get("summary", ""),
                                "link": entry.get("link", ""),
                                "pub_date": entry.get("published_parsed"),
                            }
                        )
                else:
                    # JSON format
                    data = await response.json()
                    unlocks = data.get("unlocks", [])

                events = []
                for unlock in unlocks:
                    # Проверяем формат данных (RSS или JSON)
                    if "pub_date" in unlock:  # RSS формат
                        event = self._parse_rss_entry(unlock)
                    else:  # JSON формат
                        event = self._parse_unlock(unlock)

                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                logger.info(f"Fetched {len(events)} events from TokenUnlocks")
                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching TokenUnlocks events: {e}")
            return []

    def _parse_rss_entry(self, entry: Dict) -> Dict:
        """
        Parse RSS entry to standard format.

        Args:
            entry: RSS entry data

        Returns:
            Parsed event dictionary
        """
        try:
            import time
            from datetime import timezone

            title = entry.get("title", "").strip()
            if not title:
                return None

            # Извлекаем токен из заголовка (обычно формат: "TOKEN - Unlock event")
            token_name = title.split("-")[0].strip() if "-" in title else title

            # Парсим дату публикации
            pub_date = entry.get("pub_date")
            if pub_date:
                starts_at = datetime.fromtimestamp(time.mktime(pub_date), tz=timezone.utc)
            else:
                starts_at = datetime.now(timezone.utc)

            description = entry.get("description", "")
            link = entry.get("link", "")

            return {
                "title": f"{token_name} Token Unlock",
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": "unlock",
                "importance": 0.6,
                "description": description[:500] if description else f"Token unlock event for {token_name}",
                "link": link,
                "location": "Blockchain",
                "organizer": token_name or "Token Project",
                "group_name": token_name,
                "metadata": {
                    "token_name": token_name,
                    "source": "TokenUnlocks RSS",
                },
            }
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def _parse_unlock(self, unlock: Dict) -> Dict:
        """
        Parse unlock event to standard format.

        Args:
            unlock: Raw unlock data from API

        Returns:
            Parsed event dictionary
        """
        try:
            token_name = unlock.get("token_name", "").strip()
            if not token_name:
                return None

            # Parse unlock date
            unlock_date_str = unlock.get("unlock_date")
            if not unlock_date_str:
                return None

            starts_at = datetime.fromisoformat(unlock_date_str.replace("Z", "+00:00"))

            # Calculate importance based on unlock value
            unlock_value = unlock.get("unlock_value_usd", 0)
            importance = self._calculate_importance(unlock_value)

            # Get unlock amount and percentage
            unlock_amount = unlock.get("unlock_amount", 0)
            unlock_percentage = unlock.get("unlock_percentage", 0)

            description = f"Token unlock: {unlock_amount:,.0f} tokens ({unlock_percentage:.2f}%)"
            if unlock_value > 0:
                description += f" worth ${unlock_value:,.0f}"

            return {
                "title": f"{token_name} Token Unlock",
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": "token",
                "importance": importance,
                "description": description,
                "link": unlock.get("project_url", ""),
                "location": "Blockchain",
                "organizer": token_name or "Token Project",
                "metadata": {
                    "token_name": token_name,
                    "token_symbol": unlock.get("token_symbol"),
                    "unlock_amount": unlock_amount,
                    "unlock_percentage": unlock_percentage,
                    "unlock_value_usd": unlock_value,
                },
            }

        except Exception as e:
            logger.error(f"Error parsing unlock event: {e}")
            return None

    def _calculate_importance(self, unlock_value_usd: float) -> float:
        """Calculate importance based on unlock value."""
        if unlock_value_usd >= 100_000_000:  # $100M+
            return 0.9
        elif unlock_value_usd >= 50_000_000:  # $50M+
            return 0.8
        elif unlock_value_usd >= 10_000_000:  # $10M+
            return 0.7
        elif unlock_value_usd >= 1_000_000:  # $1M+
            return 0.6
        else:
            return 0.5
