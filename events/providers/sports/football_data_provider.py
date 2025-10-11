"""
Football-Data.org Provider for football matches.

Fetches football matches from Football-Data.org API.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("football_data_provider")


class FootballDataProvider(BaseEventProvider):
    """
    Provider for Football-Data.org matches.

    Features:
    - Fetches football matches from major leagues
    - Requires API key
    - Tracks matches, tournaments, and results
    """

    def __init__(self):
        """Initialize Football-Data provider."""
        super().__init__("football_data", "sports")
        self.base_url = "https://api.football-data.org/v4"
        self.api_key = os.getenv("FOOTBALL_DATA_TOKEN")

        if not self.api_key:
            logger.warning("FOOTBALL_DATA_TOKEN not set, provider will be disabled")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from Football-Data.org.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        if not self.api_key:
            logger.warning("Football-Data provider disabled: no API key")
            return []

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={"X-Auth-Token": self.api_key}
                )

            # Fetch matches
            url = f"{self.base_url}/matches"
            params = {
                "dateFrom": start_date.strftime("%Y-%m-%d"),
                "dateTo": end_date.strftime("%Y-%m-%d"),
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Football-Data API error: {response.status}")
                    return []

                data = await response.json()
                matches = data.get("matches", [])

                events = []
                for match in matches:
                    event = self._parse_match(match)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                logger.info(f"Fetched {len(events)} events from Football-Data")
                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching Football-Data events: {e}")
            return []

    def _parse_match(self, match: Dict) -> Dict:
        """
        Parse match to standard format.

        Args:
            match: Raw match data from API

        Returns:
            Parsed event dictionary
        """
        try:
            home_team = match.get("homeTeam", {}).get("name", "")
            away_team = match.get("awayTeam", {}).get("name", "")

            if not home_team or not away_team:
                return None

            title = f"{home_team} vs {away_team}"

            # Parse match date
            utc_date_str = match.get("utcDate")
            if not utc_date_str:
                return None

            starts_at = datetime.fromisoformat(utc_date_str.replace("Z", "+00:00"))

            # Determine importance based on competition
            competition = match.get("competition", {})
            competition_name = competition.get("name", "")
            importance = self._calculate_importance(competition_name)

            # Determine subcategory
            subcategory = self._determine_subcategory(competition_name)

            # Get match status
            status = match.get("status", "SCHEDULED")

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": subcategory,
                "importance": importance,
                "description": f"{competition_name} - {status}",
                "link": f"https://www.football-data.org/matches/{match.get('id')}",
                "location": match.get("venue", ""),
                "metadata": {
                    "match_id": match.get("id"),
                    "competition": competition_name,
                    "home_team": home_team,
                    "away_team": away_team,
                    "status": status,
                    "matchday": match.get("matchday"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing match: {e}")
            return None

    def _calculate_importance(self, competition_name: str) -> float:
        """Calculate importance based on competition."""
        competition_lower = competition_name.lower()

        if any(word in competition_lower for word in ["champions league", "world cup"]):
            return 0.9
        elif any(
            word in competition_lower
            for word in ["premier league", "la liga", "bundesliga", "serie a"]
        ):
            return 0.8
        elif "europa" in competition_lower:
            return 0.7
        else:
            return 0.6

    def _determine_subcategory(self, competition_name: str) -> str:
        """Determine subcategory based on competition."""
        competition_lower = competition_name.lower()

        if "champions league" in competition_lower:
            return "champions_league"
        elif "world cup" in competition_lower:
            return "world_cup"
        elif "premier league" in competition_lower:
            return "premier_league"
        elif "europa" in competition_lower:
            return "europa_league"
        else:
            return "football"

