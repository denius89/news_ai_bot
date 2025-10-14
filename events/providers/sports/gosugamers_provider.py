"""
GosuGamers Provider for esports events.

Fetches esports matches from GosuGamers RSS feeds.
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from xml.etree import ElementTree

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("gosugamers_provider")


class GosugamersProvider(BaseEventProvider):
    """
    Provider for GosuGamers esports events.

    Features:
    - RSS feeds for Dota 2, CS:GO, LoL, Overwatch
    - Free, no API key required
    - Real-time match updates
    """

    # RSS feeds by game
    RSS_FEEDS = {
        "dota2": "https://www.gosugamers.net/dota2/gosubet",
        "csgo": "https://www.gosugamers.net/counterstrike/gosubet",
        "lol": "https://www.gosugamers.net/lol/gosubet",
        "overwatch": "https://www.gosugamers.net/overwatch/gosubet",
        "valorant": "https://www.gosugamers.net/valorant/gosubet",
    }

    def __init__(self):
        """Initialize GosuGamers provider."""
        super().__init__("gosugamers", "sports")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch esports events from GosuGamers.

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

            # Fetch from each RSS feed
            for game, rss_url in self.RSS_FEEDS.items():
                try:
                    events = await self._fetch_game_rss(game, rss_url, start_date, end_date)
                    all_events.extend(events)
                except Exception as e:
                    logger.error(f"Error fetching {game} from GosuGamers: {e}")
                    continue

            logger.info(f"Fetched {len(all_events)} events from GosuGamers")
            return all_events

        except Exception as e:
            logger.error(f"Error fetching GosuGamers events: {e}")
            return []

    async def _fetch_game_rss(self, game: str, rss_url: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch and parse RSS feed for a game.

        Args:
            game: Game identifier
            rss_url: RSS feed URL
            start_date: Start date
            end_date: End date

        Returns:
            List of events
        """
        try:
            # Apply rate limit (conservative: 6 req/hour for RSS)
            await self.rate_limiter.acquire()

            async with self.session.get(rss_url) as response:
                if response.status != 200:
                    logger.warning(f"GosuGamers RSS error for {game}: {response.status}")
                    return []

                rss_content = await response.text()

                # Parse XML с обработкой невалидных символов
                try:
                    root = ElementTree.fromstring(rss_content)
                except ElementTree.ParseError as e:
                    logger.warning(f"XML parse error for {game}: {e}, trying to clean...")

                    # Пробуем очистить невалидные символы
                    try:
                        import re

                        # Удаляем невалидные XML символы
                        cleaned_content = re.sub(r"[^\x09\x0A\x0D\x20-\x7F\x80-\xFF]+", "", rss_content)
                        root = ElementTree.fromstring(cleaned_content)
                        logger.info(f"Successfully parsed {game} XML after cleaning")
                    except Exception as clean_error:
                        logger.error(f"Failed to parse {game} XML even after cleaning: {clean_error}")
                        return []

                events = []

                # Parse items
                for item in root.findall(".//item"):
                    event = self._parse_rss_item(item, game)
                    if event:
                        # Filter by date
                        if start_date <= event["starts_at"] <= end_date:
                            normalized = self.normalize_event(event)
                            if normalized:
                                events.append(normalized)

                logger.info(f"Parsed {len(events)} {game} matches from GosuGamers RSS")
                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching {game} RSS: {e}")
            return []

    def _parse_rss_item(self, item: ElementTree.Element, game: str) -> Dict:
        """
        Parse RSS item to event dictionary.

        Args:
            item: XML element with match data
            game: Game identifier

        Returns:
            Event dictionary
        """
        try:
            title_elem = item.find("title")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")
            description_elem = item.find("description")

            if title_elem is None or title_elem.text is None:
                return None

            title = title_elem.text.strip()

            # Extract teams from title (usually "Team1 vs Team2" format)
            vs_match = re.search(r"(.+)\s+vs\.?\s+(.+)", title, re.IGNORECASE)
            if vs_match:
                team1 = vs_match.group(1).strip()
                team2 = vs_match.group(2).strip()
            else:
                team1 = None
                team2 = None

            # Parse date
            if pub_date_elem is not None and pub_date_elem.text:
                starts_at = self._parse_rss_date(pub_date_elem.text)
            else:
                # Default to near future if no date
                starts_at = datetime.now(timezone.utc) + timedelta(hours=1)

            # Extract tournament info from description
            description = description_elem.text if description_elem is not None else ""
            tournament_name = self._extract_tournament_name(description, game)

            # Subcategory from game
            subcategory_map = {
                "dota2": "dota2",
                "csgo": "csgo",
                "lol": "lol",
                "valorant": "valorant",
                "overwatch": "overwatch",
                "starcraft": "starcraft",
            }
            subcategory = subcategory_map.get(game, "esports_general")

            # Game display name
            game_names = {
                "dota2": "Dota 2",
                "csgo": "CS:GO",
                "lol": "League of Legends",
                "valorant": "Valorant",
                "overwatch": "Overwatch",
                "starcraft": "StarCraft II",
            }
            game_name = game_names.get(game, game.upper())

            return {
                "title": title,
                "starts_at": starts_at,
                "ends_at": None,
                "subcategory": subcategory,
                "importance": 0.6,  # Default importance for RSS events
                "description": f"{game_name} match",
                "link": link_elem.text if link_elem is not None else "",
                "location": "Online",
                "organizer": tournament_name or f"{game_name} Tournament",
                "group_name": tournament_name or game_name,
                "metadata": {
                    "game": game_name,
                    "team1": team1,
                    "team2": team2,
                    "tournament": tournament_name,
                    "source_rss": "gosugamers",
                },
            }

        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None

    def _parse_rss_date(self, date_str: str) -> datetime:
        """Parse RSS pubDate to datetime."""
        try:
            # RSS date format: "Mon, 15 Oct 2025 20:00:00 +0000"
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)

        except Exception as e:
            logger.warning(f"Could not parse RSS date '{date_str}': {e}")
            return datetime.now(timezone.utc) + timedelta(hours=1)

    def _extract_tournament_name(self, description: str, game: str) -> str:
        """Extract tournament name from description."""
        # Try to find tournament patterns
        tournament_patterns = [
            r"Tournament:\s*([^\n<]+)",
            r"League:\s*([^\n<]+)",
            r"Series:\s*([^\n<]+)",
        ]

        for pattern in tournament_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Default
        return f"{game.upper()} Tournament"
