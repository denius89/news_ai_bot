"""
Liquipedia Provider for esports events.

Fetches esports tournament information from Liquipedia via MediaWiki API.
"""

import logging
import re
import ssl
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp
import certifi

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("liquipedia_provider")


class LiquipediaProvider(BaseEventProvider):
    """
    Provider for Liquipedia esports events.

    Features:
    - Fetches tournament data from Liquipedia wikis
    - Supports major esports: Dota 2, CS:GO, LoL, Valorant
    - Uses MediaWiki API
    - No API key required
    """

    # Liquipedia wikis by game
    WIKIS = {
        "dota2": "dota2.liquipedia.net",
        "csgo": "counterstrike.liquipedia.net",
        "lol": "lol.liquipedia.net",
        "valorant": "valorant.liquipedia.net",
        "starcraft": "liquipedia.net/starcraft2",
    }

    def __init__(self):
        """Initialize Liquipedia provider."""
        super().__init__("liquipedia", "sports")
        self.user_agent = "PulseAI/1.0 (https://pulseai.com; contact@pulseai.com)"

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch esports events from Liquipedia.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                # Создаем SSL context для устранения connection errors
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                self.session = aiohttp.ClientSession(headers={"User-Agent": self.user_agent}, connector=connector)

            all_events = []

            # Fetch from each game wiki
            for game, wiki_url in self.WIKIS.items():
                try:
                    events = await self._fetch_game_tournaments(game, wiki_url, start_date, end_date)
                    all_events.extend(events)
                except Exception as e:
                    logger.error(f"Error fetching {game} from Liquipedia: {e}")
                    continue

            logger.info(f"Fetched {len(all_events)} events from Liquipedia")
            return all_events

        except Exception as e:
            logger.error(f"Error fetching Liquipedia events: {e}")
            return []

    async def _fetch_game_tournaments(
        self, game: str, wiki_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Fetch tournaments for a specific game.

        Uses MediaWiki API to get upcoming tournaments page.

        Args:
            game: Game identifier
            wiki_url: Liquipedia wiki URL
            start_date: Start date
            end_date: End date

        Returns:
            List of tournament events
        """
        try:
            # MediaWiki API endpoint
            api_url = f"https://{wiki_url}/api.php"

            # Get page content for upcoming tournaments
            # Most Liquipedia wikis have a "Portal:Tournaments" or "Liquipedia:Upcoming_and_ongoing_tournaments" page
            params = {
                "action": "parse",
                "page": "Liquipedia:Upcoming_and_ongoing_tournaments",
                "format": "json",
                "prop": "wikitext",
            }

            # Apply rate limit (action=parse: 1 req/30sec = 2 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(api_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Liquipedia API error for {game}: {response.status}")
                    return []

                data = await response.json()

                # Extract wikitext
                wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")

                if not wikitext:
                    logger.warning(f"No wikitext found for {game}")
                    return []

                # Parse tournaments from wikitext
                events = self._parse_wikitext(wikitext, game)

                # Filter by date range
                filtered_events = []
                for event in events:
                    if event and "starts_at" in event:
                        if start_date <= event["starts_at"] <= end_date:
                            filtered_events.append(event)

                logger.info(f"Parsed {len(filtered_events)} {game} tournaments from Liquipedia")
                return filtered_events

        except Exception as e:
            logger.error(f"Error fetching {game} tournaments: {e}")
            return []

    def _parse_wikitext(self, wikitext: str, game: str) -> List[Dict]:
        """
        Parse tournaments from MediaWiki wikitext.

        Note: This is a simple regex-based parser.
        For production, consider using mwparserfromhell library.

        Args:
            wikitext: MediaWiki wikitext content
            game: Game identifier

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Simple pattern to extract tournament templates
            # Format: {{Tournament|name=...|start=...|prize=...}}
            tournament_pattern = r"\{\{Tournament\|([^}]+)\}\}"
            matches = re.finditer(tournament_pattern, wikitext, re.IGNORECASE)

            for match in matches:
                template_content = match.group(1)

                # Extract parameters
                params = {}
                for param in template_content.split("|"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key.strip()] = value.strip()

                # Create event from parameters
                event = self._create_event_from_params(params, game)
                if event:
                    events.append(event)

        except Exception as e:
            logger.error(f"Error parsing wikitext for {game}: {e}")

        return events

    def _create_event_from_params(self, params: Dict, game: str) -> Dict:
        """Create event dictionary from template parameters."""
        try:
            name = params.get("name") or params.get("tournament")
            if not name:
                return None

            # Parse date (various formats in Liquipedia)
            date_str = params.get("start") or params.get("sdate")
            if not date_str:
                # Default to upcoming month
                starts_at = datetime.now(timezone.utc).replace(day=1)
            else:
                starts_at = self._parse_liquipedia_date(date_str)

            if not starts_at:
                return None

            # Subcategory from game
            subcategory_map = {
                "dota2": "dota2",
                "csgo": "csgo",
                "lol": "lol",
                "valorant": "valorant",
                "starcraft": "starcraft",
            }
            subcategory = subcategory_map.get(game, "esports_general")

            # Importance from prize pool
            prize = params.get("prize") or params.get("prizepool") or ""
            importance = self._calculate_importance_from_prize(prize)

            return {
                "title": name,
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": subcategory,
                "importance": importance,
                "description": f"{game.upper()} Tournament",
                "link": f"https://{self.WIKIS.get(game, 'liquipedia.net')}/wiki/{name.replace(' ', '_')}",
                "location": "Online",
                "organizer": name or f"{game.upper()} Organizers",
                "group_name": name,
                "metadata": {
                    "game": game,
                    "prize_pool": prize,
                    "tier": params.get("tier", ""),
                },
            }

        except Exception as e:
            logger.error(f"Error creating event from params: {e}")
            return None

    def _parse_liquipedia_date(self, date_str: str) -> datetime:
        """Parse various Liquipedia date formats."""
        try:
            # Try common formats
            formats = [
                "%Y-%m-%d",  # 2025-10-15
                "%B %d, %Y",  # October 15, 2025
                "%b %d, %Y",  # Oct 15, 2025
                "%d %B %Y",  # 15 October 2025
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

            # Default fallback
            logger.warning(f"Could not parse Liquipedia date: {date_str}")
            return None

        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return None

    def _calculate_importance_from_prize(self, prize_str: str) -> float:
        """Calculate importance from prize pool string."""
        try:
            # Extract numbers from prize string (e.g., "$1,000,000" -> 1000000)
            numbers = re.findall(r"[\d,]+", prize_str.replace(",", ""))
            if not numbers:
                return 0.5

            amount = int(numbers[0])

            # Importance based on prize pool
            if amount >= 1000000:  # $1M+
                return 0.9
            elif amount >= 500000:  # $500K+
                return 0.8
            elif amount >= 100000:  # $100K+
                return 0.7
            elif amount >= 50000:  # $50K+
                return 0.6
            else:
                return 0.5

        except Exception:
            return 0.5
