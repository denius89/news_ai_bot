"""
ESPN Provider for sports events.

Fetches real sports events from ESPN API.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("espn_provider")


class ESPNProvider(BaseEventProvider):
    """
    Provider for ESPN sports events.

    Features:
    - Fetches NBA, WNBA, NHL, Tennis, MLB events
    - No API key required (public API)
    - Real-time scores and schedules
    """

    def __init__(self):
        """Initialize ESPN provider."""
        super().__init__("espn", "sports")
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports"

        # Sports endpoints
        self.sports = {
            "basketball/nba": "basketball",
            "basketball/wnba": "basketball",
            "basketball/mens-college-basketball": "basketball",
            "hockey/nhl": "hockey",
            "tennis/atp": "tennis",
            "tennis/wta": "tennis",
            "baseball/mlb": "baseball",
        }

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from ESPN.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            all_events = []

            # Fetch scoreboard for each sport
            for sport_path, subcategory in self.sports.items():
                sport_events = await self._fetch_sport_scoreboard(sport_path, subcategory, start_date, end_date)
                all_events.extend(sport_events)

            logger.info(f"Fetched {len(all_events)} events from ESPN ({len(self.sports)} sports)")
            return all_events

        except Exception as e:
            logger.error(f"Error fetching ESPN events: {e}")
            return []

    async def _fetch_sport_scoreboard(
        self, sport_path: str, subcategory: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Fetch scoreboard for a specific sport.

        Args:
            sport_path: Sport path (e.g. 'basketball/nba')
            subcategory: Event subcategory
            start_date: Start date
            end_date: End date

        Returns:
            List of parsed events
        """
        try:
            # ESPN scoreboard API endpoint
            url = f"{self.base_url}/{sport_path}/scoreboard"

            # Можем запросить конкретную дату
            # Пробуем несколько дат в диапазоне
            max_days = min(7, (end_date.date() - start_date.date()).days + 1)
            events = []

            for day_offset in range(max_days):
                fetch_date = start_date.date() + timedelta(days=day_offset)
                params = {"dates": fetch_date.strftime("%Y%m%d")}

                # Apply rate limit
                await self.rate_limiter.acquire()

                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        continue

                    data = await response.json()

                    # Парсим события из scoreboard
                    scoreboard_events = data.get("events", [])

                    for event in scoreboard_events:
                        parsed = self._parse_event(event, sport_path, subcategory)
                        if parsed:
                            normalized = self.normalize_event(parsed)
                            if normalized:
                                events.append(normalized)

            return events

        except Exception as e:
            logger.error(f"Error fetching {sport_path}: {e}")
            return []

    def _parse_event(self, event: Dict, sport_path: str, subcategory: str) -> Dict:
        """
        Parse ESPN event to standard format.

        Args:
            event: Raw event from ESPN API
            sport_path: Sport path
            subcategory: Subcategory

        Returns:
            Parsed event dictionary
        """
        try:
            # Get event name
            name = event.get("name", "")
            short_name = event.get("shortName", name)

            if not short_name:
                return None

            # Get teams/competitors
            competitions = event.get("competitions", [{}])
            if not competitions:
                return None

            competition = competitions[0]
            competitors = competition.get("competitors", [])

            # Получаем названия команд
            if len(competitors) >= 2:
                home = competitors[0].get("team", {}).get("displayName", "")
                away = competitors[1].get("team", {}).get("displayName", "")
                title = f"{home} vs {away}"
            else:
                title = short_name

            # Parse date
            date_str = event.get("date")
            if not date_str:
                return None

            starts_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # Get league/competition name
            league = competition.get("venue", {}).get("fullName", "")
            if not league:
                league = event.get("league", {}).get("name", "")

            # Determine importance
            importance = self._calculate_importance(competition, event)

            # Get status
            status = competition.get("status", {})
            status_type = status.get("type", {}).get("name", "scheduled")

            # Description
            description = f"{title}"
            if league:
                description += f" - {league}"
            if status_type == "in_progress":
                description += " (Live)"

            # Extract sport name for group_name
            sport_name = self._extract_sport_name(sport_path)

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": subcategory,
                "importance": importance,
                "description": description[:500],
                "link": event.get("link", ""),
                "location": competition.get("venue", {}).get("fullName", ""),
                "organizer": league or sport_name,
                "group_name": league or sport_name,
                "metadata": {
                    "sport": sport_path,
                    "status": status_type,
                    "league": league,
                    "season": competition.get("season", {}).get("year"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing ESPN event: {e}")
            return None

    def _extract_sport_name(self, sport_path: str) -> str:
        """Extract readable sport name from path."""
        parts = sport_path.split("/")
        if len(parts) >= 2:
            sport = parts[1].upper()
            return {
                "nba": "NBA",
                "wnba": "WNBA",
                "nhl": "NHL",
                "mlb": "MLB",
                "atp": "ATP Tennis",
                "wta": "WTA Tennis",
            }.get(sport.lower(), sport)
        return "Sports"

    def _calculate_importance(self, competition: Dict, event: Dict) -> float:
        """Calculate importance based on competition and event data."""
        # Check if playoff game
        season = competition.get("season", {})
        season_type = season.get("type", 0)

        # Playoffs/Postseason
        if season_type == 3:
            return 0.9

        # Championship
        if "championship" in event.get("name", "").lower():
            return 0.85

        # Finals
        if "final" in event.get("name", "").lower():
            return 0.85

        # Regular season
        return 0.6
