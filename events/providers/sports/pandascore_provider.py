"""
PandaScore Provider for esports events.

Fetches esports matches from PandaScore API (Dota 2, CS:GO, LoL, Valorant, etc.).
"""

import logging
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("pandascore_provider")


class PandaScoreProvider(BaseEventProvider):
    """
    Provider for PandaScore esports events.

    Supported games:
    - Dota 2
    - CS:GO / CS2
    - League of Legends
    - Valorant
    - Overwatch
    - Rainbow Six Siege
    - Rocket League
    - And more...
    """

    # Supported games mapping
    GAMES_MAP = {
        "dota-2": "dota2",
        "cs-go": "csgo",
        "lol": "lol",
        "valorant": "valorant",
        "ow": "overwatch",
        "r6siege": "r6siege",
        "rl": "rocket_league",
        "pubg": "pubg",
        "fortnite": "fortnite",
        "apex": "apex_legends",
        "cod-mw": "call_of_duty",
    }

    def __init__(self):
        """Initialize PandaScore provider."""
        super().__init__("pandascore", "sports")
        self.api_key = os.getenv("PANDASCORE_TOKEN")
        self.base_url = "https://api.pandascore.co"

        if not self.api_key:
            logger.warning("PANDASCORE_TOKEN not set, provider will be disabled")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch esports events from PandaScore.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        if not self.api_key:
            logger.warning("PandaScore provider disabled: no API key")
            return []

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {self.api_key}"})

            all_events = []

            # Fetch matches for each supported game
            for game_slug, game_id in self.GAMES_MAP.items():
                try:
                    events = await self._fetch_game_matches(game_slug, start_date, end_date)
                    all_events.extend(events)
                except Exception as e:
                    logger.error(f"Error fetching {game_slug} matches: {e}")
                    continue

            logger.info(f"Fetched {len(all_events)} events from PandaScore")
            return all_events

        except Exception as e:
            logger.error(f"Error fetching PandaScore events: {e}")
            return []

    async def _fetch_game_matches(self, game_slug: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch matches for a specific game.

        Args:
            game_slug: Game slug (e.g., 'dota-2', 'cs-go')
            start_date: Start date
            end_date: End date

        Returns:
            List of normalized events
        """
        try:
            # PandaScore upcoming matches endpoint
            url = f"{self.base_url}/{game_slug}/matches/upcoming"
            params = {
                "per_page": 50,
                "page": 1,
            }

            # Apply rate limit (1000 req/hour)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"PandaScore API error for {game_slug}: {response.status}")
                    return []

                matches = await response.json()

                if not isinstance(matches, list):
                    logger.warning(f"Unexpected response format for {game_slug}")
                    return []

                events = []
                for match in matches:
                    # Filter by date range
                    match_time_str = match.get("scheduled_at") or match.get("begin_at")
                    if not match_time_str:
                        continue

                    match_time = datetime.fromisoformat(match_time_str.replace("Z", "+00:00"))

                    if not (start_date <= match_time <= end_date):
                        continue

                    event = self._parse_match(match, game_slug)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                logger.info(f"Parsed {len(events)} {game_slug} matches")
                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching {game_slug} matches: {e}")
            return []

    def _parse_match(self, match: Dict, game_slug: str) -> Dict:
        """
        Parse PandaScore match to standard format.

        Args:
            match: Raw match data from PandaScore API
            game_slug: Game identifier

        Returns:
            Parsed event dictionary
        """
        try:
            # Get opponents
            opponents = match.get("opponents", [])
            if len(opponents) < 2:
                return None

            team1 = opponents[0].get("opponent", {}).get("name", "Unknown")
            team2 = opponents[1].get("opponent", {}).get("name", "Unknown")

            title = f"{team1} vs {team2}"

            # Parse match time
            match_time_str = match.get("scheduled_at") or match.get("begin_at")
            if not match_time_str:
                return None

            starts_at = datetime.fromisoformat(match_time_str.replace("Z", "+00:00"))

            # Get tournament/league
            league = match.get("league", {})
            tournament = match.get("serie", {})
            serie = match.get("tournament", {})

            league_name = league.get("name", "")
            tournament_name = serie.get("full_name") or tournament.get("name") or "Unknown Tournament"

            # Determine importance based on tier
            tier = league.get("tier", "").lower()
            importance = self._calculate_importance(tier, match.get("status", ""))

            # Get match format (BO1, BO3, BO5)
            number_of_games = match.get("number_of_games", 1)
            if number_of_games == 1:
                match_format = "BO1"
            elif number_of_games == 3:
                match_format = "BO3"
            elif number_of_games == 5:
                match_format = "BO5"
            else:
                match_format = f"BO{number_of_games}"

            # Subcategory from game slug
            subcategory = self.GAMES_MAP.get(game_slug, "esports_general")

            # Game display name
            game_names = {
                "dota-2": "Dota 2",
                "cs-go": "CS:GO",
                "lol": "League of Legends",
                "valorant": "Valorant",
                "ow": "Overwatch",
                "r6siege": "Rainbow Six Siege",
                "rl": "Rocket League",
                "pubg": "PUBG",
                "fortnite": "Fortnite",
                "apex": "Apex Legends",
                "cod-mw": "Call of Duty: Warzone",
            }
            game_name = game_names.get(game_slug, game_slug.upper())

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": None,
                "category": "sports",  # Esports is under sports category
                "subcategory": subcategory,
                "importance": importance,
                "description": f"{tournament_name} - {match_format}",
                "link": match.get("official_stream_url", "")
                or f"https://www.pandascore.co/{game_slug}/matches/{match.get('id')}",
                "location": "Online",
                "organizer": tournament_name or f"{game_name} League",
                "group_name": tournament_name,  # Group by tournament
                "metadata": {
                    "match_id": match.get("id"),
                    "game": game_name,
                    "team1": team1,
                    "team2": team2,
                    "tournament": tournament_name,
                    "league": league_name,
                    "format": match_format,
                    "status": match.get("status", "not_started"),
                    "number_of_games": number_of_games,
                    "stream_url": match.get("official_stream_url"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing PandaScore match: {e}")
            return None

    def _calculate_importance(self, tier: str, status: str) -> float:
        """Calculate importance based on tournament tier and match status."""
        # Tier-based importance
        if tier == "s":
            importance = 0.9  # S-tier (Majors, TI, Worlds)
        elif tier == "a":
            importance = 0.8  # A-tier
        elif tier == "b":
            importance = 0.7  # B-tier
        elif tier == "c":
            importance = 0.6  # C-tier
        else:
            importance = 0.5  # Default

        # Boost for live matches
        if status == "running":
            importance = min(importance + 0.1, 1.0)

        return importance
