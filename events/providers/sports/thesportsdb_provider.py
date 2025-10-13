"""
TheSportsDB Provider for multi-sport events.

Fetches sports events from TheSportsDB API.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("thesportsdb_provider")


class TheSportsDBProvider(BaseEventProvider):
    """
    Provider for TheSportsDB multi-sport events.

    Features:
    - Fetches events from multiple sports
    - Free tier available
    - Tracks matches, tournaments, and results
    """

    def __init__(self):
        """Initialize TheSportsDB provider."""
        super().__init__("thesportsdb", "sports")
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3"

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from TheSportsDB.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            events = []

            # Fetch events for each day in range
            current_date = start_date.date()
            end_date_only = end_date.date()

            while current_date <= end_date_only:
                day_events = await self._fetch_events_for_date(current_date)
                events.extend(day_events)
                current_date += timedelta(days=1)

            logger.info(f"Fetched {len(events)} events from TheSportsDB")
            return events

        except Exception as e:
            logger.error(f"Error fetching TheSportsDB events: {e}")
            return []

    async def _fetch_events_for_date(self, date) -> List[Dict]:
        """Fetch events for a specific date."""
        try:
            # TheSportsDB endpoint for events by date
            url = f"{self.base_url}/eventsday.php"
            params = {
                "d": date.strftime("%Y-%m-%d"),
                "s": "Soccer",  # Can be expanded to other sports
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                events_data = data.get("events")

                if not events_data:
                    return []

                events = []
                for event in events_data:
                    parsed = self._parse_event(event)
                    if parsed:
                        normalized = self.normalize_event(parsed)
                        if normalized:
                            events.append(normalized)

                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching events for date {date}: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict:
        """
        Parse event to standard format.

        Args:
            event: Raw event data from API

        Returns:
            Parsed event dictionary
        """
        try:
            home_team = event.get("strHomeTeam", "")
            away_team = event.get("strAwayTeam", "")

            if not home_team or not away_team:
                return None

            title = f"{home_team} vs {away_team}"

            # Parse event date and time
            date_str = event.get("dateEvent")
            time_str = event.get("strTime", "00:00:00")

            if not date_str:
                return None

            # Combine date and time
            datetime_str = f"{date_str} {time_str}"

            # Handle timezone info if present
            if "+" in datetime_str:
                datetime_str = datetime_str.split("+")[0].strip()

            starts_at = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

            # Get sport and league
            sport = event.get("strSport", "Soccer")
            league = event.get("strLeague", "")

            # Calculate importance
            importance = self._calculate_importance(league)

            # Determine subcategory
            subcategory = self._determine_subcategory(sport)

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": None,
                "category": "sports",  # Категория для группировки
                "subcategory": subcategory,
                "importance": importance,
                "description": f"{league} - {sport}",
                "link": f"https://www.thesportsdb.com/event/{event.get('idEvent')}",
                "location": event.get("strVenue", ""),
                "group_name": league or sport,  # Лига или спорт для группировки
                "metadata": {
                    "event_id": event.get("idEvent"),
                    "sport": sport,
                    "league": league,
                    "home_team": home_team,
                    "away_team": away_team,
                    "season": event.get("strSeason"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None

    def _calculate_importance(self, league: str) -> float:
        """Calculate importance based on league."""
        league_lower = league.lower()

        if any(word in league_lower for word in ["champions league", "world cup", "premier league"]):
            return 0.8
        elif any(word in league_lower for word in ["la liga", "bundesliga", "serie a"]):
            return 0.75
        elif "europa" in league_lower:
            return 0.7
        else:
            return 0.6

    def _determine_subcategory(self, sport: str) -> str:
        """Determine subcategory based on sport."""
        sport_lower = sport.lower()

        if "soccer" in sport_lower or "football" in sport_lower:
            return "football"
        elif "basketball" in sport_lower:
            return "basketball"
        elif "tennis" in sport_lower:
            return "tennis"
        elif "cricket" in sport_lower:
            return "cricket"
        else:
            return "other"
