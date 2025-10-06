"""
Event Context Engine for PulseAI.

This module provides AI-powered context generation for events,
explaining their significance and connecting them to current trends.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ai_modules.metrics import get_metrics

logger = logging.getLogger("event_context")


@dataclass
class EventContext:
    """Represents AI-generated context for an event."""
    event_id: int
    context: str
    related_trends: List[str]
    significance_explanation: str
    market_impact: str
    confidence: float
    generated_at: datetime


class EventContextEngine:
    """
    AI-powered event context generator.
    
    Features:
    - Explains event significance in human terms
    - Connects events to current trends
    - Provides market impact analysis
    - Generates confidence scores
    """
    
    def __init__(self):
        """Initialize event context engine."""
        self.metrics = get_metrics()
        
        # Context templates by category
        self.context_templates = {
            'crypto': {
                'upgrade': "Ключевое обновление сети, улучшающее {specifics}.",
                'launch': "Запуск нового {specifics}, расширяющего экосистему.",
                'listing': "Добавление {specifics} на крупные биржи.",
                'regulation': "Регулятивные изменения, влияющие на {specifics}.",
                'partnership': "Стратегическое партнерство для {specifics}."
            },
            'markets': {
                'rate_decision': "Решение центрального банка по {specifics} ставкам.",
                'economic_data': "Важный экономический показатель {specifics}.",
                'policy_change': "Изменение политики, влияющее на {specifics}.",
                'earnings': "Квартальные результаты {specifics} компаний."
            },
            'sports': {
                'championship': "Финальный матч {specifics} сезона.",
                'tournament': "Крупный турнир {specifics} уровня.",
                'transfer': "Трансферное окно {specifics}.",
                'record': "Попытка установить {specifics} рекорд."
            },
            'tech': {
                'release': "Релиз нового {specifics} продукта.",
                'conference': "Технологическая конференция {specifics}.",
                'breakthrough': "Прорыв в области {specifics}.",
                'acquisition': "Поглощение {specifics} компаний."
            },
            'world': {
                'election': "Важные выборы {specifics}.",
                'summit': "Международный саммит {specifics}.",
                'policy': "Изменение политики {specifics}.",
                'crisis': "Развитие ситуации {specifics}."
            }
        }
        
        # Trend keywords by category
        self.trend_keywords = {
            'crypto': ['DeFi', 'NFT', 'Web3', 'Institutional adoption', 'Regulation', 'Scalability'],
            'markets': ['Inflation', 'Interest rates', 'Economic recovery', 'Central bank policy', 'Market volatility'],
            'sports': ['Digital transformation', 'Fan engagement', 'Data analytics', 'Esports growth', 'Sustainability'],
            'tech': ['AI advancement', 'Cloud computing', 'Cybersecurity', 'IoT expansion', 'Quantum computing'],
            'world': ['Geopolitical shifts', 'Climate action', 'Digital governance', 'Economic recovery', 'Social change']
        }
        
        logger.info("EventContextEngine initialized")
    
    async def generate_event_context(self, event: Dict[str, Any]) -> EventContext:
        """
        Generate AI context for an event.
        
        Args:
            event: Event dictionary with title, category, description, etc.
            
        Returns:
            EventContext with generated context and analysis
        """
        try:
            event_id = event.get('id', 0)
            title = event.get('title', '')
            category = event.get('category', 'unknown')
            description = event.get('description', '')
            importance = event.get('importance', 0.5)
            
            logger.debug(f"Generating context for event: {title}")
            
            # Generate context based on event type
            context = await self._generate_context_text(title, category, description, importance)
            
            # Identify related trends
            related_trends = self._identify_related_trends(title, category, description)
            
            # Generate significance explanation
            significance = self._generate_significance_explanation(title, category, importance)
            
            # Assess market impact
            market_impact = self._assess_market_impact(title, category, importance)
            
            # Calculate confidence
            confidence = self._calculate_confidence(title, description, importance)
            
            # Create context object
            event_context = EventContext(
                event_id=event_id,
                context=context,
                related_trends=related_trends,
                significance_explanation=significance,
                market_impact=market_impact,
                confidence=confidence,
                generated_at=datetime.now(timezone.utc)
            )
            
            # Update metrics
            self.metrics.increment_event_context_generated_total()
            
            logger.info(f"Generated context for event {event_id}: confidence={confidence:.2f}")
            
            return event_context
            
        except Exception as e:
            logger.error(f"Error generating event context: {e}")
            
            # Return fallback context
            return EventContext(
                event_id=event.get('id', 0),
                context="Событие требует дополнительного анализа.",
                related_trends=[],
                significance_explanation="Значимость события оценивается.",
                market_impact="Влияние на рынки анализируется.",
                confidence=0.3,
                generated_at=datetime.now(timezone.utc)
            )
    
    async def _generate_context_text(
        self, 
        title: str, 
        category: str, 
        description: str, 
        importance: float
    ) -> str:
        """Generate contextual text for the event."""
        try:
            # Determine event type from title
            event_type = self._classify_event_type(title, category)
            
            # Get template for this event type
            templates = self.context_templates.get(category, {})
            template = templates.get(event_type, "Важное событие в области {specifics}.")
            
            # Extract specifics from title/description
            specifics = self._extract_specifics(title, description, category)
            
            # Generate context using template
            context = template.format(specifics=specifics)
            
            # Add importance modifier
            if importance >= 0.8:
                context = f"Критически важное событие: {context.lower()}"
            elif importance >= 0.6:
                context = f"Значимое событие: {context.lower()}"
            
            return context.capitalize()
            
        except Exception as e:
            logger.error(f"Error generating context text: {e}")
            return "Событие требует дополнительного анализа контекста."
    
    def _classify_event_type(self, title: str, category: str) -> str:
        """Classify the type of event based on title and category."""
        title_lower = title.lower()
        
        # Category-specific classification
        if category == 'crypto':
            if any(word in title_lower for word in ['upgrade', 'merge', 'fork', 'update']):
                return 'upgrade'
            elif any(word in title_lower for word in ['launch', 'release', 'deploy']):
                return 'launch'
            elif any(word in title_lower for word in ['listing', 'exchange', 'trading']):
                return 'listing'
            elif any(word in title_lower for word in ['regulation', 'law', 'ban', 'approval']):
                return 'regulation'
            elif any(word in title_lower for word in ['partnership', 'collaboration', 'integration']):
                return 'partnership'
        
        elif category == 'markets':
            if any(word in title_lower for word in ['rate', 'interest', 'fomc', 'ecb', 'boe']):
                return 'rate_decision'
            elif any(word in title_lower for word in ['cpi', 'gdp', 'nfp', 'inflation', 'employment']):
                return 'economic_data'
            elif any(word in title_lower for word in ['policy', 'stimulus', 'quantitative']):
                return 'policy_change'
            elif any(word in title_lower for word in ['earnings', 'revenue', 'profit']):
                return 'earnings'
        
        elif category == 'sports':
            if any(word in title_lower for word in ['championship', 'final', 'cup']):
                return 'championship'
            elif any(word in title_lower for word in ['tournament', 'competition']):
                return 'tournament'
            elif any(word in title_lower for word in ['transfer', 'signing', 'contract']):
                return 'transfer'
            elif any(word in title_lower for word in ['record', 'milestone', 'achievement']):
                return 'record'
        
        elif category == 'tech':
            if any(word in title_lower for word in ['release', 'launch', 'announce']):
                return 'release'
            elif any(word in title_lower for word in ['conference', 'summit', 'event']):
                return 'conference'
            elif any(word in title_lower for word in ['breakthrough', 'innovation', 'discovery']):
                return 'breakthrough'
            elif any(word in title_lower for word in ['acquisition', 'merger', 'buyout']):
                return 'acquisition'
        
        elif category == 'world':
            if any(word in title_lower for word in ['election', 'vote', 'candidate']):
                return 'election'
            elif any(word in title_lower for word in ['summit', 'meeting', 'conference']):
                return 'summit'
            elif any(word in title_lower for word in ['policy', 'law', 'regulation']):
                return 'policy'
            elif any(word in title_lower for word in ['crisis', 'emergency', 'situation']):
                return 'crisis'
        
        return 'general'
    
    def _extract_specifics(self, title: str, description: str, category: str) -> str:
        """Extract specific details from title and description."""
        text = f"{title} {description}".lower()
        
        # Extract key terms based on category
        if category == 'crypto':
            if 'ethereum' in text:
                return 'Ethereum сети'
            elif 'bitcoin' in text:
                return 'Bitcoin экосистемы'
            elif 'defi' in text:
                return 'DeFi протоколов'
            elif 'nft' in text:
                return 'NFT рынка'
            else:
                return 'блокчейн технологий'
        
        elif category == 'markets':
            if 'fomc' in text or 'federal' in text:
                return 'Федеральной резервной системы США'
            elif 'ecb' in text or 'european' in text:
                return 'Европейского центрального банка'
            elif 'cpi' in text:
                return 'потребительских цен'
            elif 'gdp' in text:
                return 'валового внутреннего продукта'
            else:
                return 'финансовых рынков'
        
        elif category == 'sports':
            if 'football' in text or 'soccer' in text:
                return 'футбола'
            elif 'basketball' in text:
                return 'баскетбола'
            elif 'tennis' in text:
                return 'тенниса'
            elif 'olympics' in text:
                return 'Олимпийских игр'
            else:
                return 'спорта'
        
        elif category == 'tech':
            if 'ai' in text or 'artificial' in text:
                return 'искусственного интеллекта'
            elif 'cloud' in text:
                return 'облачных технологий'
            elif 'security' in text or 'cyber' in text:
                return 'кибербезопасности'
            elif 'quantum' in text:
                return 'квантовых вычислений'
            else:
                return 'технологий'
        
        elif category == 'world':
            if 'climate' in text or 'environment' in text:
                return 'климатических изменений'
            elif 'trade' in text or 'economic' in text:
                return 'международной торговли'
            elif 'security' in text or 'defense' in text:
                return 'международной безопасности'
            else:
                return 'международных отношений'
        
        return 'отрасли'
    
    def _identify_related_trends(self, title: str, category: str, description: str) -> List[str]:
        """Identify related trends based on event content."""
        text = f"{title} {description}".lower()
        trends = []
        
        # Get category-specific trends
        category_trends = self.trend_keywords.get(category, [])
        
        # Match trends based on content
        for trend in category_trends:
            if any(keyword.lower() in text for keyword in trend.split()):
                trends.append(trend)
        
        # Limit to 3 most relevant trends
        return trends[:3]
    
    def _generate_significance_explanation(
        self, 
        title: str, 
        category: str, 
        importance: float
    ) -> str:
        """Generate explanation of event significance."""
        if importance >= 0.9:
            return "Событие критически важно и может кардинально изменить ситуацию в отрасли."
        elif importance >= 0.8:
            return "Высокозначимое событие с потенциально серьезными последствиями."
        elif importance >= 0.7:
            return "Важное событие, которое может повлиять на развитие отрасли."
        elif importance >= 0.6:
            return "Значимое событие, заслуживающее внимания."
        else:
            return "Событие средней важности в контексте текущих трендов."
    
    def _assess_market_impact(self, title: str, category: str, importance: float) -> str:
        """Assess potential market impact of the event."""
        if category == 'crypto':
            if importance >= 0.8:
                return "Может вызвать значительные движения на криптовалютных рынках."
            elif importance >= 0.6:
                return "Потенциально повлияет на настроения инвесторов в криптосекторе."
            else:
                return "Ограниченное влияние на криптовалютные рынки."
        
        elif category == 'markets':
            if importance >= 0.8:
                return "Может вызвать волатильность на финансовых рынках."
            elif importance >= 0.6:
                return "Потенциально повлияет на рыночные настроения."
            else:
                return "Умеренное влияние на финансовые рынки."
        
        elif category == 'sports':
            return "Влияет на спортивную индустрию и связанные с ней рынки."
        
        elif category == 'tech':
            return "Может повлиять на технологический сектор и связанные акции."
        
        elif category == 'world':
            return "Потенциально влияет на глобальные рынки и валюты."
        
        return "Влияние на рынки оценивается."
    
    def _calculate_confidence(
        self, 
        title: str, 
        description: str, 
        importance: float
    ) -> float:
        """Calculate confidence score for the generated context."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for longer, more detailed titles
        if len(title.split()) >= 5:
            confidence += 0.1
        
        # Higher confidence for events with descriptions
        if description and len(description) > 50:
            confidence += 0.2
        
        # Higher confidence for high-importance events
        if importance >= 0.8:
            confidence += 0.1
        elif importance >= 0.6:
            confidence += 0.05
        
        # Adjust based on title clarity
        if any(word in title.lower() for word in ['upgrade', 'launch', 'meeting', 'decision']):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))


# Global context engine instance
_context_engine_instance: Optional[EventContextEngine] = None


def get_event_context_engine() -> EventContextEngine:
    """Get global event context engine instance."""
    global _context_engine_instance
    if _context_engine_instance is None:
        _context_engine_instance = EventContextEngine()
    return _context_engine_instance


async def generate_event_context(event: Dict[str, Any]) -> EventContext:
    """
    Convenience function to generate context for an event.
    
    Args:
        event: Event dictionary
        
    Returns:
        EventContext with generated analysis
    """
    engine = get_event_context_engine()
    return await engine.generate_event_context(event)
