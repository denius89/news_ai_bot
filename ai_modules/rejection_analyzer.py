"""
Rejection Analyzer for Auto-Learning Filter.

This module analyzes rejected news items from logs/rejected.log
to identify patterns and generate recommendations for rule updates.
"""

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml

logger = logging.getLogger("rejection_analyzer")


class RejectionAnalyzer:
    """
    Analyzes rejected news items to identify patterns for auto-learning.
    
    Reads logs/rejected.log, extracts statistics, and generates
    recommendations for improving prefilter rules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize rejection analyzer with configuration."""
        self.config = self._load_config(config_path)
        self.rejected_log_path = Path("logs/rejected.log")
        self.analysis_output_path = Path("logs/rejection_analysis.json")
        
        # Configuration parameters
        self.top_words_limit = self.config.get('rejection_analysis', {}).get('top_words_limit', 50)
        self.top_sources_limit = self.config.get('rejection_analysis', {}).get('top_sources_limit', 20)
        self.frequency_threshold = self.config.get('rejection_analysis', {}).get('frequency_threshold', 0.02)
        self.min_samples = self.config.get('features', {}).get('auto_learn_min_samples', 100)
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "prefilter_rules.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _parse_rejected_log(self) -> List[Dict]:
        """
        Parse rejected.log and extract structured data.
        
        Expected log format:
        [timestamp] REJECTED: reason=pre_filter category=crypto source=example.com title="Bitcoin price..."
        
        Returns:
            List of dictionaries with parsed rejection data
        """
        rejected_items = []
        
        if not self.rejected_log_path.exists():
            logger.warning("rejected.log not found, returning empty analysis")
            return rejected_items
        
        try:
            with open(self.rejected_log_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or not line.startswith('['):
                        continue
                    
                    try:
                        # Parse log line format
                        parsed = self._parse_log_line(line)
                        if parsed:
                            rejected_items.append(parsed)
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")
                        continue
            
            logger.info(f"Parsed {len(rejected_items)} rejected items from log")
            
        except Exception as e:
            logger.error(f"Error reading rejected.log: {e}")
        
        return rejected_items
    
    def _parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single log line to extract rejection data.
        
        Args:
            line: Log line string
            
        Returns:
            Dictionary with parsed data or None if parsing fails
        """
        try:
            # Extract timestamp
            timestamp_match = re.match(r'\[([^\]]+)\]', line)
            if not timestamp_match:
                return None
            
            timestamp = timestamp_match.group(1)
            
            # Extract key-value pairs after "REJECTED:"
            if "REJECTED:" not in line:
                return None
            
            data_part = line.split("REJECTED:", 1)[1].strip()
            
            # Parse key-value pairs
            data = {}
            for pair in data_part.split():
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    data[key] = value
            
            # Extract title from the end if present
            title_match = re.search(r'title="([^"]+)"', line)
            if title_match:
                data['title'] = title_match.group(1)
            
            data['timestamp'] = timestamp
            return data
            
        except Exception as e:
            logger.debug(f"Error parsing log line: {e}")
            return None
    
    def _extract_words_from_title(self, title: str) -> List[str]:
        """
        Extract meaningful words from news title.
        
        Args:
            title: News title string
            
        Returns:
            List of cleaned words
        """
        if not title:
            return []
        
        # Convert to lowercase and remove punctuation
        cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
        
        # Split into words and filter out short words and common stop words
        words = cleaned.split()
        
        # Common English stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter words
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in stop_words
        ]
        
        return filtered_words
    
    def analyze_rejections(self) -> Dict:
        """
        Analyze rejected news items and generate statistics.
        
        Returns:
            Dictionary with analysis results
        """
        logger.info("Starting rejection analysis...")
        
        # Parse rejected items from log
        rejected_items = self._parse_rejected_log()
        
        if len(rejected_items) < self.min_samples:
            logger.info(f"Not enough samples for analysis: {len(rejected_items)} < {self.min_samples}")
            return self._create_empty_analysis()
        
        # Initialize counters
        category_counter = Counter()
        source_counter = Counter()
        reason_counter = Counter()
        word_counter = Counter()
        source_category_counter = defaultdict(Counter)
        
        # Analyze each rejected item
        for item in rejected_items:
            category = item.get('category', 'unknown')
            source = item.get('source', 'unknown')
            reason = item.get('reason', 'unknown')
            title = item.get('title', '')
            
            # Count categories, sources, reasons
            category_counter[category] += 1
            source_counter[source] += 1
            reason_counter[reason] += 1
            source_category_counter[source][category] += 1
            
            # Extract and count words from title
            words = self._extract_words_from_title(title)
            for word in words:
                word_counter[word] += 1
        
        total_items = len(rejected_items)
        
        # Calculate statistics
        analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_rejected_items': total_items,
            'analysis_period_days': self._calculate_analysis_period(rejected_items),
            
            # Top categories by rejection count
            'top_rejected_categories': dict(category_counter.most_common(10)),
            
            # Top sources by rejection count
            'top_rejected_sources': dict(source_counter.most_common(self.top_sources_limit)),
            
            # Rejection reasons
            'rejection_reasons': dict(reason_counter.most_common()),
            
            # Top words in rejected titles
            'top_rejected_words': dict(word_counter.most_common(self.top_words_limit)),
            
            # Word frequency analysis
            'word_frequency_analysis': self._analyze_word_frequency(word_counter, total_items),
            
            # Source-category patterns
            'source_category_patterns': dict(source_category_counter),
            
            # Recommendations
            'recommendations': self._generate_recommendations(
                word_counter, source_counter, reason_counter, total_items
            )
        }
        
        # Save analysis to file
        self._save_analysis(analysis)
        
        # Log summary
        self._log_analysis_summary(analysis)
        
        return analysis
    
    def _calculate_analysis_period(self, rejected_items: List[Dict]) -> int:
        """Calculate analysis period in days."""
        if not rejected_items:
            return 0
        
        try:
            # Get earliest and latest timestamps
            timestamps = []
            for item in rejected_items:
                timestamp_str = item.get('timestamp', '')
                if timestamp_str:
                    # Try to parse timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamps.append(dt)
                    except:
                        continue
            
            if len(timestamps) < 2:
                return 1
            
            earliest = min(timestamps)
            latest = max(timestamps)
            period = (latest - earliest).days + 1
            
            return max(1, period)
            
        except Exception as e:
            logger.warning(f"Error calculating analysis period: {e}")
            return 1
    
    def _analyze_word_frequency(self, word_counter: Counter, total_items: int) -> Dict:
        """Analyze word frequency patterns."""
        frequency_analysis = {}
        
        for word, count in word_counter.most_common():
            frequency = count / total_items
            
            # Categorize words by frequency
            if frequency >= self.frequency_threshold:
                frequency_analysis[word] = {
                    'count': count,
                    'frequency': round(frequency, 4),
                    'status': 'high_frequency',
                    'recommendation': 'add_to_stop_markers'
                }
            elif frequency >= self.frequency_threshold / 2:
                frequency_analysis[word] = {
                    'count': count,
                    'frequency': round(frequency, 4),
                    'status': 'medium_frequency',
                    'recommendation': 'monitor'
                }
            else:
                frequency_analysis[word] = {
                    'count': count,
                    'frequency': round(frequency, 4),
                    'status': 'low_frequency',
                    'recommendation': 'ignore'
                }
        
        return frequency_analysis
    
    def _generate_recommendations(self, word_counter: Counter, source_counter: Counter, 
                                 reason_counter: Counter, total_items: int) -> Dict:
        """Generate recommendations based on analysis."""
        recommendations = {
            'add_stop_markers': [],
            'add_importance_markers': [],
            'source_blacklist': [],
            'rule_adjustments': []
        }
        
        # Analyze words for stop markers
        for word, count in word_counter.most_common():
            frequency = count / total_items
            if frequency >= self.frequency_threshold:
                recommendations['add_stop_markers'].append({
                    'word': word,
                    'count': count,
                    'frequency': round(frequency, 4),
                    'confidence': min(1.0, frequency * 10)  # Confidence based on frequency
                })
        
        # Analyze sources for blacklisting
        for source, count in source_counter.most_common():
            frequency = count / total_items
            if frequency >= self.frequency_threshold * 2:  # Higher threshold for sources
                recommendations['source_blacklist'].append({
                    'source': source,
                    'count': count,
                    'frequency': round(frequency, 4),
                    'confidence': min(1.0, frequency * 5)
                })
        
        # Analyze rejection reasons
        pre_filter_count = reason_counter.get('pre_filter', 0)
        if pre_filter_count > 0:
            recommendations['rule_adjustments'].append({
                'type': 'prefilter_optimization',
                'description': f'High pre_filter rejections: {pre_filter_count}',
                'suggestion': 'Review and optimize prefilter rules'
            })
        
        return recommendations
    
    def _save_analysis(self, analysis: Dict) -> None:
        """Save analysis results to JSON file."""
        try:
            # Ensure logs directory exists
            self.analysis_output_path.parent.mkdir(exist_ok=True)
            
            with open(self.analysis_output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis saved to {self.analysis_output_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
    
    def _log_analysis_summary(self, analysis: Dict) -> None:
        """Log analysis summary to console."""
        logger.info("=" * 60)
        logger.info("REJECTION ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total rejected items: {analysis['total_rejected_items']}")
        logger.info(f"Analysis period: {analysis['analysis_period_days']} days")
        
        # Top categories
        logger.info("\nTop rejected categories:")
        for category, count in list(analysis['top_rejected_categories'].items())[:5]:
            logger.info(f"  {category}: {count}")
        
        # Top sources
        logger.info("\nTop rejected sources:")
        for source, count in list(analysis['top_rejected_sources'].items())[:5]:
            logger.info(f"  {source}: {count}")
        
        # Top words
        logger.info("\nTop rejected words:")
        for word, count in list(analysis['top_rejected_words'].items())[:10]:
            logger.info(f"  {word}: {count}")
        
        # Recommendations
        recommendations = analysis['recommendations']
        logger.info(f"\nRecommendations:")
        logger.info(f"  Add stop markers: {len(recommendations['add_stop_markers'])}")
        logger.info(f"  Source blacklist: {len(recommendations['source_blacklist'])}")
        logger.info(f"  Rule adjustments: {len(recommendations['rule_adjustments'])}")
        
        logger.info("=" * 60)
    
    def _create_empty_analysis(self) -> Dict:
        """Create empty analysis when insufficient data."""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_rejected_items': 0,
            'analysis_period_days': 0,
            'top_rejected_categories': {},
            'top_rejected_sources': {},
            'rejection_reasons': {},
            'top_rejected_words': {},
            'word_frequency_analysis': {},
            'source_category_patterns': {},
            'recommendations': {
                'add_stop_markers': [],
                'add_importance_markers': [],
                'source_blacklist': [],
                'rule_adjustments': []
            }
        }
    
    def is_enabled(self) -> bool:
        """Check if auto-learning is enabled."""
        return self.config.get('features', {}).get('auto_learn_enabled', True)
    
    def get_analysis_path(self) -> Path:
        """Get path to analysis output file."""
        return self.analysis_output_path


# Global analyzer instance
_analyzer_instance: Optional[RejectionAnalyzer] = None


def get_rejection_analyzer() -> RejectionAnalyzer:
    """Get global rejection analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = RejectionAnalyzer()
    return _analyzer_instance


def analyze_rejections() -> Dict:
    """
    Convenience function to analyze rejections.
    
    Returns:
        Dictionary with analysis results
    """
    analyzer = get_rejection_analyzer()
    if not analyzer.is_enabled():
        logger.info("Auto-learning is disabled, skipping analysis")
        return analyzer._create_empty_analysis()
    
    return analyzer.analyze_rejections()
