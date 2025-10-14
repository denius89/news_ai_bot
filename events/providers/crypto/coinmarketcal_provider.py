"""
CoinMarketCal Provider for cryptocurrency events.

Fetches crypto events from CoinMarketCal API.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("coinmarketcal_provider")


class CoinMarketCalProvider(BaseEventProvider):
    """
    Provider for CoinMarketCal cryptocurrency events.

    Features:
    - Fetches events from CoinMarketCal API
    - Requires API key
    - Categorizes by crypto type and event type
    """

    def __init__(self):
        """Initialize CoinMarketCal provider."""
        super().__init__("coinmarketcal", "crypto")
        self.api_key = os.getenv("COINMARKETCAL_TOKEN")
        self.base_url = "https://developers.coinmarketcal.com/v1"

        if not self.api_key:
            logger.warning("COINMARKETCAL_TOKEN not set, provider will be disabled")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from CoinMarketCal.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        if not self.api_key:
            logger.warning("CoinMarketCal provider disabled: no API key")
            return []

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers={"x-api-key": self.api_key})

            # CoinMarketCal events endpoint
            url = f"{self.base_url}/events"
            params = {
                "dateRangeStart": start_date.strftime("%d/%m/%Y"),
                "dateRangeEnd": end_date.strftime("%d/%m/%Y"),
                "max": 100,  # Max results per request
            }

            # Apply rate limit (100 req/day)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"CoinMarketCal API error: {response.status}")
                    return []

                data = await response.json()
                events_data = data.get("body", [])

                normalized_events = []
                for event in events_data:
                    normalized = self._parse_event(event)
                    if normalized:
                        normalized_event = self.normalize_event(normalized)
                        if normalized_event:
                            normalized_events.append(normalized_event)

                logger.info(f"Fetched {len(normalized_events)} events from " "CoinMarketCal")
                return [e for e in normalized_events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching CoinMarketCal events: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict:
        """
        Parse CoinMarketCal event to standard format.

        Args:
            event: Raw event from CoinMarketCal API

        Returns:
            Parsed event dictionary
        """
        try:
            title_text = event.get("title", {}).get("en", "").strip()
            if not title_text:
                return None

            # Parse date
            date_event = event.get("date_event")
            if not date_event:
                return None

            starts_at = datetime.strptime(date_event, "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc)

            # Get coins
            coins = event.get("coins", [])
            coin_names = [coin.get("name", "") for coin in coins if coin.get("name")]

            # Determine importance based on vote count and categories
            vote_count = event.get("vote_count", 0)
            categories = event.get("categories", [])
            importance = self._calculate_importance(vote_count, categories)

            # Determine subcategory
            subcategory = self._determine_subcategory(categories)

            # Build description
            description = event.get("description", {}).get("en", "")
            if coin_names:
                description = f"Coins: {', '.join(coin_names[:3])}. {description}"

            # Определяем группу (первая монета или категория)
            group_name = (
                coin_names[0] if coin_names else (categories[0].get("name", "Crypto") if categories else "Crypto")
            )

            return {
                "title": title_text,
                "starts_at": starts_at,
                "ends_at": None,
                "category": "crypto",  # Категория для группировки
                "subcategory": subcategory,
                "importance": importance,
                "description": description[:500] if description else "",
                "link": event.get("source", ""),
                "location": "Blockchain",
                "organizer": group_name or "Crypto Community",
                "group_name": group_name,  # Монета для группировки
                "metadata": {
                    "coins": coin_names,
                    "vote_count": vote_count,
                    "categories": [cat.get("name", "") for cat in categories],
                    "proof": event.get("proof", ""),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing CoinMarketCal event: {e}")
            return None

    def _calculate_importance(self, vote_count: int, categories: List[Dict]) -> float:
        """Calculate importance score based on votes and categories."""
        # Base importance from votes
        if vote_count >= 1000:
            importance = 0.9
        elif vote_count >= 500:
            importance = 0.8
        elif vote_count >= 100:
            importance = 0.7
        elif vote_count >= 50:
            importance = 0.6
        else:
            importance = 0.5

        # Boost for important categories
        category_names = [cat.get("name", "").lower() for cat in categories]
        important_categories = [
            "mainnet",
            "hard fork",
            "airdrop",
            "listing",
            "token swap",
        ]

        for cat in important_categories:
            if any(cat in name for name in category_names):
                importance = min(importance + 0.1, 1.0)
                break

        return importance

    def _determine_subcategory(self, categories: List[Dict]) -> str:
        """Determine subcategory based on categories."""
        category_names = [cat.get("name", "").lower() for cat in categories]

        if any("mainnet" in name or "launch" in name for name in category_names):
            return "protocol"
        elif any("airdrop" in name or "token" in name for name in category_names):
            return "token"
        elif any("listing" in name or "exchange" in name for name in category_names):
            return "exchange"
        elif any("conference" in name or "meetup" in name for name in category_names):
            return "conference"
        elif any("partnership" in name for name in category_names):
            return "partnership"
        elif any("defi" in name for name in category_names):
            return "defi"
        elif any("nft" in name for name in category_names):
            return "nft"
        else:
            return "general"
