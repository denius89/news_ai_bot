"""
CoinMarketCal provider for cryptocurrency events.

This provider fetches cryptocurrency events from CoinMarketCal API
including token launches, mainnet releases, and protocol updates.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

import aiohttp

from events.events_parser import Event

logger = logging.getLogger("coinmarketcal_provider")


class CoinMarketCalProvider:
    """
    Provider for CoinMarketCal cryptocurrency events.
    
    Features:
    - Fetches events from CoinMarketCal API
    - Categorizes by cryptocurrency type
    - Assigns importance based on event type
    """
    
    def __init__(self):
        """Initialize CoinMarketCal provider."""
        self.base_url = "https://api.coinmarketcal.com"
        self.session = None
        
        # Event type importance mapping
        self.importance_mapping = {
            'mainnet': 0.9,
            'launch': 0.8,
            'upgrade': 0.7,
            'listing': 0.6,
            'partnership': 0.5,
            'conference': 0.4,
            'other': 0.3
        }
        
        logger.info("CoinMarketCal provider initialized")
    
    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """
        Fetch events from CoinMarketCal.
        
        Args:
            start_date: Start date for fetching
            end_date: End date for fetching
            
        Returns:
            List of Event objects
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Format dates for API
            date_from = start_date.strftime('%Y-%m-%d')
            date_to = end_date.strftime('%Y-%m-%d')
            
            # API endpoint
            url = f"{self.base_url}/v1/events"
            
            # Parameters
            params = {
                'dateRangeStart': date_from,
                'dateRangeEnd': date_to,
                'page': 1,
                'max': 100,
                'showOnly': 'hot_events'  # Focus on important events
            }
            
            logger.info(f"Fetching CoinMarketCal events from {date_from} to {date_to}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    events = self._parse_api_response(data)
                    logger.info(f"Fetched {len(events)} events from CoinMarketCal")
                    return events
                else:
                    logger.error(f"CoinMarketCal API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching CoinMarketCal events: {e}")
            return []
    
    def _parse_api_response(self, data: Dict[str, Any]) -> List[Event]:
        """
        Parse API response into Event objects.
        
        Args:
            data: API response data
            
        Returns:
            List of Event objects
        """
        events = []
        
        try:
            items = data.get('body', [])
            
            for item in items:
                try:
                    event = self._parse_event_item(item)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing event item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
        
        return events
    
    def _parse_event_item(self, item: Dict[str, Any]) -> Optional[Event]:
        """
        Parse individual event item from API response.
        
        Args:
            item: Event item from API
            
        Returns:
            Event object or None if parsing fails
        """
        try:
            # Extract basic information
            title = item.get('title', '').strip()
            if not title:
                return None
            
            # Parse dates
            date_str = item.get('date_event', '')
            if not date_str:
                return None
            
            starts_at = self._parse_date(date_str)
            if not starts_at:
                return None
            
            # Determine category and subcategory
            category = 'crypto'
            subcategory = self._determine_subcategory(item)
            
            # Calculate importance
            importance = self._calculate_importance(item)
            
            # Extract additional information
            description = item.get('description', '').strip()
            source = 'coinmarketcal.com'
            link = item.get('link', '')
            
            # Create event
            event = Event(
                title=title,
                category=category,
                subcategory=subcategory,
                starts_at=starts_at,
                ends_at=None,  # CoinMarketCal doesn't provide end times
                source=source,
                link=link,
                importance=importance,
                description=description
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing event item: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from API response."""
        try:
            # CoinMarketCal typically uses YYYY-MM-DD format
            return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                # Try with time component
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None
    
    def _determine_subcategory(self, item: Dict[str, Any]) -> str:
        """Determine subcategory based on event data."""
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        
        # Check for specific cryptocurrencies
        crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc'],
            'ethereum': ['ethereum', 'eth'],
            'cardano': ['cardano', 'ada'],
            'polkadot': ['polkadot', 'dot'],
            'solana': ['solana', 'sol'],
            'chainlink': ['chainlink', 'link'],
            'uniswap': ['uniswap', 'uni'],
            'defi': ['defi', 'decentralized finance', 'yield farming'],
            'nft': ['nft', 'non-fungible token']
        }
        
        text = f"{title} {description}"
        
        for crypto, keywords in crypto_keywords.items():
            if any(keyword in text for keyword in keywords):
                return crypto
        
        return 'general'
    
    def _calculate_importance(self, item: Dict[str, Any]) -> float:
        """Calculate importance score for event."""
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        
        # Base importance
        importance = 0.5
        
        # Check for important keywords
        important_keywords = [
            'mainnet', 'launch', 'upgrade', 'hard fork', 'listing',
            'partnership', 'integration', 'release', 'announcement'
        ]
        
        for keyword in important_keywords:
            if keyword in title or keyword in description:
                importance = max(importance, self.importance_mapping.get(keyword, 0.3))
        
        # Boost for major cryptocurrencies
        major_cryptos = ['bitcoin', 'ethereum', 'cardano', 'polkadot', 'solana']
        if any(crypto in title.lower() for crypto in major_cryptos):
            importance = min(1.0, importance + 0.2)
        
        # Boost for confirmed events
        if item.get('is_confirmed', False):
            importance = min(1.0, importance + 0.1)
        
        return round(importance, 2)
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            'name': 'CoinMarketCal',
            'description': 'Cryptocurrency events and announcements',
            'categories': ['crypto'],
            'importance_mapping': self.importance_mapping,
            'base_url': self.base_url
        }
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
