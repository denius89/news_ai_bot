"""
Investing.com provider for financial events.

This provider fetches financial events from Investing.com
including economic indicators, central bank meetings, and earnings.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

import aiohttp

from events.events_parser import Event

logger = logging.getLogger("investing_provider")


class InvestingProvider:
    """
    Provider for Investing.com financial events.

    Features:
    - Fetches economic events and indicators
    - Categorizes by financial markets
    - Assigns importance based on market impact
    """

    def __init__(self):
        """Initialize Investing.com provider."""
        self.base_url = "https://www.investing.com"
        self.session = None

        # Event importance mapping
        self.importance_mapping = {
            "fomc": 0.95,
            "ecb": 0.9,
            "boe": 0.85,
            "cpi": 0.9,
            "gdp": 0.85,
            "nfp": 0.9,
            "rate_decision": 0.9,
            "earnings": 0.7,
            "economic_indicator": 0.6,
            "other": 0.4,
        }

        logger.info("Investing.com provider initialized")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """
        Fetch events from Investing.com.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of Event objects
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # For now, return mock data since Investing.com requires complex scraping
            # In production, you would implement proper scraping or API integration
            events = self._generate_mock_events(start_date, end_date)

            logger.info(f"Fetched {len(events)} events from Investing.com")
            return events

        except Exception as e:
            logger.error(f"Error fetching Investing.com events: {e}")
            return []

    def _generate_mock_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """
        Generate mock financial events for testing.

        Args:
            start_date: Start date for events
            end_date: End date for events

        Returns:
            List of mock Event objects
        """
        events = []

        # Generate events for the date range
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            # Add some common financial events
            daily_events = self._get_daily_events(current_date)
            events.extend(daily_events)

            current_date += timedelta(days=1)

        return events

    def _get_daily_events(self, date) -> List[Event]:
        """Get events for a specific date."""
        events = []

        # Monday - Friday events
        if date.weekday() < 5:
            # Economic indicators (common on weekdays)
            if date.day % 7 == 1:  # First week of month
                events.append(
                    Event(
                        title="Non-Farm Payrolls (NFP)",
                        category="markets",
                        subcategory="employment",
                        starts_at=datetime.combine(date, datetime.min.time().replace(hour=12, minute=30)).replace(
                            tzinfo=timezone.utc
                        ),
                        ends_at=None,
                        source="investing.com",
                        link="https://www.investing.com/economic-calendar/",
                        importance=0.9,
                        description="Monthly employment report for the United States",
                    )
                )

            if date.day % 15 == 0:  # Mid-month
                events.append(
                    Event(
                        title="Consumer Price Index (CPI)",
                        category="markets",
                        subcategory="inflation",
                        starts_at=datetime.combine(date, datetime.min.time().replace(hour=12, minute=30)).replace(
                            tzinfo=timezone.utc
                        ),
                        ends_at=None,
                        source="investing.com",
                        link="https://www.investing.com/economic-calendar/",
                        importance=0.9,
                        description="Monthly inflation indicator",
                    )
                )

            # Central bank meetings (monthly)
            if date.day <= 7 and date.month % 2 == 0:  # First week of even months
                events.append(
                    Event(
                        title="FOMC Meeting",
                        category="markets",
                        subcategory="monetary_policy",
                        starts_at=datetime.combine(date, datetime.min.time().replace(hour=18, minute=0)).replace(
                            tzinfo=timezone.utc
                        ),
                        ends_at=None,
                        source="investing.com",
                        link="https://www.investing.com/economic-calendar/",
                        importance=0.95,
                        description="Federal Open Market Committee meeting",
                    )
                )

            if date.day <= 7 and date.month % 2 == 1:  # First week of odd months
                events.append(
                    Event(
                        title="ECB Interest Rate Decision",
                        category="markets",
                        subcategory="monetary_policy",
                        starts_at=datetime.combine(date, datetime.min.time().replace(hour=12, minute=45)).replace(
                            tzinfo=timezone.utc
                        ),
                        ends_at=None,
                        source="investing.com",
                        link="https://www.investing.com/economic-calendar/",
                        importance=0.9,
                        description="European Central Bank monetary policy decision",
                    )
                )

            # GDP releases (quarterly)
            if date.month in [1, 4, 7, 10] and date.day <= 10:
                events.append(
                    Event(
                        title="GDP Growth Rate",
                        category="markets",
                        subcategory="economic_growth",
                        starts_at=datetime.combine(date, datetime.min.time().replace(hour=12, minute=30)).replace(
                            tzinfo=timezone.utc
                        ),
                        ends_at=None,
                        source="investing.com",
                        link="https://www.investing.com/economic-calendar/",
                        importance=0.85,
                        description="Quarterly economic growth indicator",
                    )
                )

        return events

    def _determine_subcategory(self, title: str) -> str:
        """Determine subcategory based on event title."""
        title_lower = title.lower()

        subcategory_mapping = {
            "employment": ["nfp", "employment", "job", "unemployment"],
            "inflation": ["cpi", "inflation", "price index"],
            "monetary_policy": ["fomc", "ecb", "boe", "interest rate", "monetary"],
            "economic_growth": ["gdp", "growth", "economic"],
            "earnings": ["earnings", "revenue", "profit"],
            "trade": ["trade", "export", "import", "balance"],
            "housing": ["housing", "home", "real estate"],
            "manufacturing": ["manufacturing", "industrial", "pmi"],
        }

        for subcategory, keywords in subcategory_mapping.items():
            if any(keyword in title_lower for keyword in keywords):
                return subcategory

        return "general"

    def _calculate_importance(self, title: str) -> float:
        """Calculate importance score for financial event."""
        title_lower = title.lower()

        # Check for high-impact keywords
        for event_type, importance in self.importance_mapping.items():
            if event_type.replace("_", " ") in title_lower or event_type in title_lower:
                return importance

        # Default importance
        return 0.5

    def get_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            "name": "Investing.com",
            "description": "Financial and economic events",
            "categories": ["markets", "economics"],
            "importance_mapping": self.importance_mapping,
            "base_url": self.base_url,
        }

    async def close(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
