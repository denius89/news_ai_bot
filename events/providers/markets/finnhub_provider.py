"""
Finnhub Provider for stock market events.

Fetches market events from Finnhub API.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("finnhub_provider")


class FinnhubProvider(BaseEventProvider):
    """
    Provider for Finnhub stock market events.

    Features:
    - Fetches earnings calendars
    - Fetches IPO calendars
    - Fetches economic calendars
    - Requires API key
    """

    def __init__(self):
        """Initialize Finnhub provider."""
        super().__init__("finnhub", "markets")
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = os.getenv("FINNHUB_TOKEN")

        if not self.api_key:
            logger.warning("FINNHUB_TOKEN not set, provider will be disabled")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from Finnhub.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        if not self.api_key:
            logger.warning("Finnhub provider disabled: no API key")
            return []

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            events = []

            # Fetch earnings calendar
            earnings = await self._fetch_earnings_calendar(start_date, end_date)
            events.extend(earnings)

            # Fetch IPO calendar
            ipos = await self._fetch_ipo_calendar(start_date, end_date)
            events.extend(ipos)

            # Fetch economic calendar
            economic = await self._fetch_economic_calendar(start_date, end_date)
            events.extend(economic)

            logger.info(f"Fetched {len(events)} events from Finnhub")
            return events

        except Exception as e:
            logger.error(f"Error fetching Finnhub events: {e}")
            return []

    async def _fetch_earnings_calendar(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch earnings calendar."""
        try:
            url = f"{self.base_url}/calendar/earnings"
            params = {
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "token": self.api_key,
            }

            # Apply rate limit (Free: 60 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                earnings_data = data.get("earningsCalendar", [])

                events = []
                for earning in earnings_data:
                    event = self._parse_earning(earning)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {e}")
            return []

    async def _fetch_ipo_calendar(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch IPO calendar."""
        try:
            url = f"{self.base_url}/calendar/ipo"
            params = {
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "token": self.api_key,
            }

            # Apply rate limit (Free: 60 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                ipo_data = data.get("ipoCalendar", [])

                events = []
                for ipo in ipo_data:
                    event = self._parse_ipo(ipo)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching IPO calendar: {e}")
            return []

    async def _fetch_economic_calendar(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch economic calendar."""
        try:
            url = f"{self.base_url}/calendar/economic"
            params = {
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "token": self.api_key,
            }

            # Apply rate limit (Free: 60 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                economic_data = data.get("economicCalendar", [])

                events = []
                for economic in economic_data:
                    event = self._parse_economic(economic)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []

    def _parse_earning(self, earning: Dict) -> Dict:
        """Parse earning event."""
        try:
            symbol = earning.get("symbol", "")
            if not symbol:
                return None

            date_str = earning.get("date")
            if not date_str:
                return None

            starts_at = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            return {
                "title": f"{symbol} Earnings Report",
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": "earnings",
                "importance": 0.7,
                "description": f"Quarterly earnings report for {symbol}",
                "link": f"https://finnhub.io/quote/{symbol}",
                "location": "Financial Markets",
                "organizer": symbol,
                "metadata": {
                    "symbol": symbol,
                    "eps_estimate": earning.get("epsEstimate"),
                    "revenue_estimate": earning.get("revenueEstimate"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing earning: {e}")
            return None

    def _parse_ipo(self, ipo: Dict) -> Dict:
        """Parse IPO event."""
        try:
            name = ipo.get("name", "")
            symbol = ipo.get("symbol", "")

            if not name:
                return None

            date_str = ipo.get("date")
            if not date_str:
                return None

            starts_at = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            return {
                "title": f"{name} ({symbol}) IPO",
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": "ipos",
                "importance": 0.8,
                "description": f"Initial Public Offering of {name}",
                "link": f"https://finnhub.io/quote/{symbol}",
                "location": "Stock Exchange",
                "organizer": name or symbol,
                "metadata": {
                    "symbol": symbol,
                    "name": name,
                    "price_range": ipo.get("priceRange"),
                    "shares": ipo.get("totalSharesValue"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing IPO: {e}")
            return None

    def _parse_economic(self, economic: Dict) -> Dict:
        """Parse economic event."""
        try:
            event_name = economic.get("event", "")
            if not event_name:
                return None

            date_str = economic.get("date")
            if not date_str:
                return None

            starts_at = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            # Calculate importance based on impact
            impact = economic.get("impact", "").lower()
            importance = 0.9 if impact == "high" else 0.7 if impact == "medium" else 0.5

            return {
                "title": event_name,
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": "economic_data",
                "importance": importance,
                "description": f"{event_name} - {economic.get('country', '')}",
                "link": "https://finnhub.io/calendar/economic",
                "location": economic.get("country") or "Global",
                "organizer": "Economic Bureau",
                "metadata": {
                    "country": economic.get("country"),
                    "impact": impact,
                    "unit": economic.get("unit"),
                    "estimate": economic.get("estimate"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing economic event: {e}")
            return None
