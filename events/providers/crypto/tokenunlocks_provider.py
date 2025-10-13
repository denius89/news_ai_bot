"""
TokenUnlocks Provider for token unlock schedules.

Fetches token unlock events from TokenUnlocks.app.
"""

import logging
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
        self.base_url = "https://token.unlocks.app/api"

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
                self.session = aiohttp.ClientSession()

            # Fetch upcoming unlocks
            url = f"{self.base_url}/unlocks"
            params = {
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"TokenUnlocks API error: {response.status}")
                    return []

                data = await response.json()
                unlocks = data.get("unlocks", [])

                events = []
                for unlock in unlocks:
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
