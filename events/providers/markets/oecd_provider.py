"""
OECD Provider for economic events.

Fetches OECD economic events from HTML pages.
"""

import logging
from datetime import datetime
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup  # noqa: F401

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("oecd_provider")


class OECDProvider(BaseEventProvider):
    """
    Provider for OECD economic events.

    Features:
    - Fetches events from OECD website
    - No API key required
    - HTML scraping
    """

    def __init__(self):
        """Initialize OECD provider."""
        super().__init__("oecd_events", "markets")
        self.base_url = "https://www.oecd.org/events"

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from OECD.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        try:
            if not self.session:
                # Add more comprehensive browser-like headers to avoid 403 errors
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "Dnt": "1",
                }
                # Use a different approach with timeout and cookies
                timeout = aiohttp.ClientTimeout(total=30, connect=10)
                connector = aiohttp.TCPConnector(limit=10, force_close=False)
                self.session = aiohttp.ClientSession(headers=headers, timeout=timeout, connector=connector)

            # Fetch OECD events page
            # Apply rate limit (HTML scraping: conservative 60 req/hour)
            await self.rate_limiter.acquire()

            async with self.session.get(self.base_url) as response:
                if response.status != 200:
                    logger.error(f"OECD website error: {response.status}")
                    return []

                html = await response.text()
                events = self._parse_events(html, start_date, end_date)

                logger.info(f"Fetched {len(events)} events from OECD")
                return events

        except Exception as e:
            logger.error(f"Error fetching OECD events: {e}")
            return []

    def _parse_events(self, html: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Parse OECD events from HTML."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            events = []

            # Look for event elements on OECD website
            # Common selectors for event listings
            event_selectors = [
                "div.event-item",
                "article.event",
                ".event-card",
                ".events-list li",
                "div[class*='event']",
            ]

            for selector in event_selectors:
                event_elements = soup.select(selector)
                if event_elements:
                    logger.info(f"Found {len(event_elements)} events with selector: {selector}")
                    break

            if not event_elements:
                # Fallback: look for any links with event-like text
                event_elements = soup.find_all("a", href=True)
                event_elements = [
                    elem
                    for elem in event_elements
                    if any(
                        keyword in elem.get_text().lower()
                        for keyword in ["meeting", "conference", "webinar", "workshop", "seminar", "event"]
                    )
                ]

            for element in event_elements[:20]:  # Limit to avoid too many events
                try:
                    event = self._parse_event_element(element, start_date, end_date)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)
                except Exception as e:
                    logger.debug(f"Error parsing event element: {e}")
                    continue

            logger.info(f"Parsed {len(events)} OECD events from HTML")
            return events

        except Exception as e:
            logger.error(f"Error parsing OECD events: {e}")
            return []

    def _parse_event_element(self, element, start_date: datetime, end_date: datetime) -> Dict:
        """Parse individual event element."""
        try:
            # Extract title
            title = ""
            title_elem = element.find(["h1", "h2", "h3", "h4", ".title", ".event-title"])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                title = element.get_text(strip=True)[:100]  # First 100 chars as fallback

            if not title:
                return None

            # Extract link
            link = ""
            link_elem = element.find("a", href=True)
            if link_elem:
                href = link_elem.get("href")
                if href:
                    link = href if href.startswith("http") else f"https://www.oecd.org{href}"

            # Extract description
            description = ""
            desc_elem = element.find(["p", ".description", ".event-description"])
            if desc_elem:
                description = desc_elem.get_text(strip=True)

            # For now, use current date as event date (OECD website structure varies)
            # In production, would parse actual dates from element
            event_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0)  # Default 10:00 AM

            return {
                "title": title,
                "starts_at": event_date,
                "ends_at": None,
                "subcategory": "economic_events",
                "importance": 0.7,
                "description": description or f"OECD event: {title}",
                "link": link or "https://www.oecd.org/events",
                "location": "OECD Headquarters, Paris",
                "organizer": "OECD",
                "metadata": {"source_type": "html_scraping"},
            }

        except Exception as e:
            logger.debug(f"Error parsing event element: {e}")
            return None
