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

            # CoinGecko /events и /coins/list/new deprecated
            # Используем /search/trending для трендовых монет (стабильный API v3)
            url = f"{self.base_url}/search/trending"

            # Apply rate limit (Free tier: 10 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"CoinGecko API error: {response.status}")
                    return []

                # Trending endpoint возвращает: {"coins": [...], "nfts": [...], "categories": [...]}
                data = await response.json()
                trending_coins = data.get("coins", [])

                # Создаем события из трендовых монет
                events = []
                from datetime import timezone

                now = datetime.now(timezone.utc)

                for item in trending_coins[:15]:  # Топ 15 трендовых монет
                    coin = item.get("item", {})
                    # Создаем событие "Trending Crypto"
                    event = {
                        "title": coin.get("name", "Unknown"),
                        "description": f"Trending cryptocurrency #{len(events)+1} on CoinGecko",
                        "event_type": "trending",
                        "coins": [coin.get("symbol", "")],
                        "coin_id": coin.get("id", ""),
                        "market_cap_rank": coin.get("market_cap_rank"),
                        "activated_at": now.isoformat(),
                    }
                    events.append(event)

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
        Поддерживает как старый формат (events), так и новый (listings).

        Args:
            event: Raw event from CoinGecko API

        Returns:
            Parsed event dictionary
        """
        try:
            # Trending формат
            if "event_type" in event and event["event_type"] == "trending":
                symbol = event.get("coins", [""])[0]
                rank = len(event.get("description", "").split("#")) - 1  # Извлекаем ранг из описания
                title = f"🔥 {event.get('title', 'Unknown')} ({symbol.upper()}) - Trending #{rank}"

                # Парсим дату
                activated_at = event.get("activated_at")
                if not activated_at:
                    from datetime import timezone

                    activated_at = datetime.now(timezone.utc).isoformat()

                try:
                    starts_at = datetime.fromisoformat(activated_at.replace("Z", "+00:00"))
                except Exception:
                    from datetime import timezone

                    starts_at = datetime.now(timezone.utc)

                coin_id = event.get("coin_id", "")
                market_cap_rank = event.get("market_cap_rank")

                description = event.get("description", "")
                if market_cap_rank:
                    description += f" | Market Cap Rank: #{market_cap_rank}"

                return {
                    "title": title,
                    "starts_at": starts_at,
                    "ends_at": starts_at,
                    "description": description,
                    "event_type": "trending",
                    "importance": 0.75,  # Трендовые монеты важны
                    "subcategory": "trending",
                    "group_name": "Trending Crypto",
                    "coins": event.get("coins", []),
                    "link": f"https://www.coingecko.com/en/coins/{coin_id}" if coin_id else "",
                }

            # Старый формат (listings) - для обратной совместимости
            if "activated_at" in event and "event_type" not in event:
                title = f"{event.get('title', 'Unknown')} ({event.get('symbol', '').upper()}) - New Listing"

                activated_at = event.get("activated_at")
                if not activated_at:
                    return None

                try:
                    starts_at = datetime.fromisoformat(activated_at.replace("Z", "+00:00"))
                except Exception:
                    from datetime import timezone

                    starts_at = datetime.now(timezone.utc)

                return {
                    "title": title,
                    "starts_at": starts_at,
                    "ends_at": starts_at,
                    "description": event.get("description") or f"New {event.get('title')} listing on CoinGecko",
                    "event_type": "listing",
                    "importance": 0.7,
                    "subcategory": "listing",
                    "group_name": event.get("title", "Crypto"),
                    "coins": [event.get("symbol", "")],
                    "link": f"https://www.coingecko.com/en/coins/{event.get('id', '')}",
                }

            # Старый формат (events) - для обратной совместимости
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
