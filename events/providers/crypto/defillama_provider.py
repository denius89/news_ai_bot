"""
DeFi Llama Provider for DeFi protocol events.

Fetches DeFi events from DeFi Llama API.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("defillama_provider")


class DefiLlamaProvider(BaseEventProvider):
    """
    Provider for DeFi Llama protocol events.

    Features:
    - Fetches DeFi protocol events
    - No API key required
    - Tracks protocol launches, upgrades, and major changes
    """

    def __init__(self):
        """Initialize DeFi Llama provider."""
        super().__init__("defillama", "crypto")
        self.base_url = "https://api.llama.fi"

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from DeFi Llama.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Fetch protocol list
            protocols_url = f"{self.base_url}/protocols"
            async with self.session.get(protocols_url) as response:
                if response.status != 200:
                    logger.error(f"DeFi Llama API error: {response.status}")
                    return []

                protocols = await response.json()

                # Filter protocols with recent changes
                events = []
                for protocol in protocols:
                    event = self._check_protocol_for_events(protocol, start_date, end_date)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                logger.info(f"Fetched {len(events)} events from DeFi Llama")
                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching DeFi Llama events: {e}")
            return []

    def _check_protocol_for_events(self, protocol: Dict, start_date: datetime, end_date: datetime) -> Dict:
        """
        Check if protocol has events in date range.
        Создает события для:
        1. Новых запусков протоколов
        2. Значительных изменений TVL (>50% за день)

        Args:
            protocol: Protocol data from API
            start_date: Start date
            end_date: End date

        Returns:
            Event dictionary or None
        """
        try:
            # 1. Check TVL changes (большие изменения = важное событие)
            change_1d = protocol.get("change_1d")
            change_7d = protocol.get("change_7d")
            tvl = protocol.get("tvl", 0)

            # Если TVL изменился больше чем на 50% за день - это событие!
            if change_1d and abs(change_1d) > 50 and tvl > 1_000_000:  # TVL > $1M
                now = datetime.now(timezone.utc)
                change_type = "surge" if change_1d > 0 else "drop"

                # Форматируем change_7d только если он есть
                change_7d_str = f" (7d: {change_7d:+.1f}%)" if change_7d else ""

                return {
                    "title": f"🔥 {protocol.get('name')} TVL {change_type.upper()} {abs(change_1d):.1f}%",
                    "starts_at": now,
                    "ends_at": None,
                    "subcategory": "defi",
                    "importance": min(0.9, 0.6 + abs(change_1d) / 200),  # Выше изменение - важнее
                    "description": f"{protocol.get('name')} TVL changed {change_1d:+.1f}% in 24h{change_7d_str}. Current TVL: ${tvl:,.0f}",
                    "link": protocol.get("url", ""),
                    "group_name": f"DeFi TVL {change_type.title()}s",
                    "metadata": {
                        "protocol_name": protocol.get("name"),
                        "chain": protocol.get("chain"),
                        "category": protocol.get("category"),
                        "tvl": tvl,
                        "change_1d": change_1d,
                        "change_7d": change_7d,
                    },
                }

            # 2. Check if protocol was launched in date range
            launch_date = protocol.get("listedAt")
            if launch_date:
                launch_dt = datetime.fromtimestamp(launch_date, tz=timezone.utc)
                if start_date <= launch_dt <= end_date:
                    return {
                        "title": f"{protocol.get('name')} Protocol Launch",
                        "starts_at": launch_dt,
                        "ends_at": None,
                        "subcategory": "defi",
                        "importance": 0.75,
                        "description": f"Launch of {protocol.get('name')} on {protocol.get('chain', 'multiple chains')}. TVL: ${tvl:,.0f}",
                        "link": protocol.get("url", ""),
                        "group_name": "New DeFi Protocols",
                        "metadata": {
                            "protocol_name": protocol.get("name"),
                            "chain": protocol.get("chain"),
                            "category": protocol.get("category"),
                            "tvl": tvl,
                        },
                    }

            return None

        except Exception as e:
            logger.error(f"Error checking protocol for events: {e}")
            return None
