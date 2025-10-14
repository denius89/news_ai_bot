"""
CoinGecko Provider for cryptocurrency events.

Fetches crypto events from CoinGecko API.
"""

import logging
from datetime import datetime
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("coingecko_provider")


class CoinGeckoProvider(BaseEventProvider):
    """
    Provider for CoinGecko cryptocurrency events.

    Features:
    - Fetches events from CoinGecko API
    - No API key required
    - Categorizes by crypto type
    """

    def __init__(self):
        """Initialize CoinGecko provider."""
        super().__init__("coingecko", "crypto")
        self.base_url = "https://api.coingecko.com/api/v3"

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from CoinGecko.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # CoinGecko events endpoint
            url = f"{self.base_url}/events"
            params = {
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
            }

            # Apply rate limit (Free tier: 10 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"CoinGecko API error: {response.status}")
                    return []

                data = await response.json()
                events = data.get("data", [])

                normalized_events = []
                for event in events:
                    normalized = self._parse_event(event)
                    if normalized:
                        normalized_events.append(self.normalize_event(normalized))

                logger.info(f"Fetched {len(normalized_events)} events from CoinGecko")
                return [e for e in normalized_events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching CoinGecko events: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict:
        """
        Parse CoinGecko event to standard format.

        Args:
            event: Raw event from CoinGecko API

        Returns:
            Parsed event dictionary
        """
        try:
            title = event.get("title", "").strip()
            if not title:
                return None

            # Parse date
            start_date_str = event.get("start_date")
            if not start_date_str:
                return None

            starts_at = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))

            # Parse end date if available
            end_date_str = event.get("end_date")
            ends_at = None
            if end_date_str:
                ends_at = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))

            # Determine importance based on event type
            event_type = event.get("type", "").lower()
            importance = self._calculate_importance(event_type)

            # Determine subcategory
            subcategory = self._determine_subcategory(event_type)

            # Определяем группу (первая монета из списка или тип события)
            coins_list = event.get("coins", [])
            group_name = coins_list[0] if coins_list else event_type.title()

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": ends_at,
                "category": "crypto",  # Категория для группировки
                "subcategory": subcategory,
                "importance": importance,
                "description": event.get("description", ""),
                "link": event.get("website", ""),
                "location": event.get("venue") or "Global",
                "organizer": event.get("organizer") or "Community",
                "group_name": group_name,  # Монета для группировки
                "metadata": {
                    "event_type": event_type,
                    "coins": coins_list,
                },
            }

        except Exception as e:
            logger.error(f"Error parsing CoinGecko event: {e}")
            return None

    def _calculate_importance(self, event_type: str) -> float:
        """Calculate importance score based on event type."""
        importance_map = {
            "mainnet": 0.9,
            "launch": 0.85,
            "upgrade": 0.8,
            "hard fork": 0.85,
            "airdrop": 0.7,
            "listing": 0.65,
            "conference": 0.6,
            "partnership": 0.55,
            "meetup": 0.4,
        }

        for key, score in importance_map.items():
            if key in event_type:
                return score

        return 0.5

    def _determine_subcategory(self, event_type: str) -> str:
        """Determine subcategory based on event type."""
        if any(word in event_type for word in ["mainnet", "launch", "upgrade", "fork"]):
            return "protocol"
        elif any(word in event_type for word in ["airdrop", "token"]):
            return "token"
        elif any(word in event_type for word in ["listing", "exchange"]):
            return "exchange"
        elif any(word in event_type for word in ["conference", "meetup", "summit"]):
            return "conference"
        elif any(word in event_type for word in ["partnership", "collaboration"]):
            return "partnership"
        else:
            return "general"
