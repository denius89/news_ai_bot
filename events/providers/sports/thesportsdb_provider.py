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

            # Список поддерживаемых видов спорта
            sports = [
                "Soccer",  # Футбол
                "Basketball",  # Баскетбол (NBA, EuroLeague, etc)
                "Ice Hockey",  # Хоккей (NHL, KHL, etc)
                "Tennis",  # Теннис (ATP, WTA)
                "Baseball",  # Бейсбол (MLB)
                "American Football",  # Американский футбол (NFL)
                "Rugby",  # Регби
                "Cricket",  # Крикет
                "Volleyball",  # Волейбол
                "Handball",  # Гандбол
            ]

            all_events = []

            # Fetch events for each sport and each day in range
            # Ограничиваем до 7 дней чтобы не делать слишком много запросов
            max_days = min(7, (end_date.date() - start_date.date()).days + 1)

            for sport in sports:
                try:
                    current_date = start_date.date()

                    for day_offset in range(max_days):
                        fetch_date = current_date + timedelta(days=day_offset)
                        day_events = await self._fetch_events_for_date(fetch_date, sport)
                        all_events.extend(day_events)
                except Exception as e:
                    logger.debug(f"Error fetching {sport}: {e}")
                    continue

            logger.info(f"Fetched {len(all_events)} events from TheSportsDB ({len(sports)} sports)")
            return all_events

        except Exception as e:
            logger.error(f"Error fetching TheSportsDB events: {e}")
            return []

    async def _fetch_events_for_date(self, date, sport: str = "Soccer") -> List[Dict]:
        """
        Fetch events for a specific date and sport.

        Args:
            date: Date to fetch events for
            sport: Sport name (Soccer, Basketball, Ice Hockey, Tennis, etc.)
        """
        try:
            # TheSportsDB endpoint for events by date
            url = f"{self.base_url}/eventsday.php"
            params = {
                "d": date.strftime("%Y-%m-%d"),
                "s": sport,
            }

            # Apply rate limit (conservative: ~100 req/hour)
            await self.rate_limiter.acquire()

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
                "location": event.get("strVenue") or "Venue TBA",
                "organizer": league or f"{sport.title()} League",
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

        if "soccer" in sport_lower:
            return "football"
        elif "basketball" in sport_lower:
            return "basketball"
        elif "hockey" in sport_lower:
            return "hockey"
        elif "tennis" in sport_lower:
            return "tennis"
        elif "baseball" in sport_lower:
            return "baseball"
        elif "american football" in sport_lower or sport_lower == "football":
            return "american_football"
        elif "rugby" in sport_lower:
            return "rugby"
        elif "cricket" in sport_lower:
            return "cricket"
        elif "volleyball" in sport_lower:
            return "volleyball"
        elif "handball" in sport_lower:
            return "handball"
        else:
            return "other"
