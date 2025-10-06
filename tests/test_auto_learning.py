"""
Tests for Auto-Learning Filter functionality.

This module tests the rejection analyzer and auto rule manager
for the auto-learning system.
"""

import pytest
import tempfile
import json
import yaml
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from datetime import datetime, timezone, timedelta

from ai_modules.rejection_analyzer import RejectionAnalyzer
from ai_modules.auto_rule_manager import AutoRuleManager


class TestRejectionAnalyzer:
    """Test rejection analyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            'features': {'auto_learn_enabled': True},
            'rejection_analysis': {
                'top_words_limit': 10,
                'top_sources_limit': 5,
                'frequency_threshold': 0.1
            },
            'features': {'auto_learn_min_samples': 5}
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
        self.analyzer = RejectionAnalyzer(self.temp_config.name)
        
        # Create temporary rejected.log
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        self.temp_log.close()
        
        # Override log path for testing
        self.analyzer.rejected_log_path = Path(self.temp_log.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()
        Path(self.temp_log.name).unlink()
    
    def test_parse_log_line_valid(self):
        """Test parsing valid log line."""
        log_line = '[2025-01-01T10:00:00Z] REJECTED: reason=pre_filter category=crypto source=example.com title="Bitcoin price"'
        
        result = self.analyzer._parse_log_line(log_line)
        
        assert result is not None
        assert result['timestamp'] == '2025-01-01T10:00:00Z'
        assert result['reason'] == 'pre_filter'
        assert result['category'] == 'crypto'
        assert result['source'] == 'example.com'
        assert result['title'] == 'Bitcoin price'
    
    def test_parse_log_line_invalid(self):
        """Test parsing invalid log line."""
        log_line = 'Invalid log line without proper format'
        
        result = self.analyzer._parse_log_line(log_line)
        
        assert result is None
    
    def test_extract_words_from_title(self):
        """Test word extraction from title."""
        title = "Bitcoin Price Prediction - Click Here to Learn More!"
        
        words = self.analyzer._extract_words_from_title(title)
        
        expected_words = ['bitcoin', 'price', 'prediction', 'click', 'here', 'learn', 'more']
        assert set(words) == set(expected_words)
        
        # Test filtering of short words and stop words
        title_with_stops = "The Bitcoin and price prediction for you"
        words_filtered = self.analyzer._extract_words_from_title(title_with_stops)
        
        # Should filter out 'the', 'and', 'for' (stop words)
        expected_filtered = ['bitcoin', 'price', 'prediction', 'you']
        assert set(words_filtered) == set(expected_filtered)
    
    def test_analyze_rejections_empty_log(self):
        """Test analysis with empty log."""
        # Create empty log file
        with open(self.temp_log.name, 'w') as f:
            pass
        
        result = self.analyzer.analyze_rejections()
        
        assert result['total_rejected_items'] == 0
        assert result['top_rejected_categories'] == {}
        assert result['top_rejected_sources'] == {}
        assert result['recommendations']['add_stop_markers'] == []
    
    def test_analyze_rejections_insufficient_samples(self):
        """Test analysis with insufficient samples."""
        # Create log with only 2 entries (less than min_samples=5)
        with open(self.temp_log.name, 'w') as f:
            f.write('[2025-01-01T10:00:00Z] REJECTED: reason=pre_filter category=crypto source=example.com title="Bitcoin"\n')
            f.write('[2025-01-01T11:00:00Z] REJECTED: reason=pre_filter category=tech source=tech.com title="Tech news"\n')
        
        result = self.analyzer.analyze_rejections()
        
        assert result['total_rejected_items'] == 0  # Should return empty analysis
    
    def test_analyze_rejections_with_data(self):
        """Test analysis with sufficient data."""
        # Create log with 10 entries (more than min_samples=5)
        with open(self.temp_log.name, 'w') as f:
            for i in range(10):
                f.write(f'[2025-01-01T{i:02d}:00:00Z] REJECTED: reason=pre_filter category=crypto source=spam.com title="Bitcoin giveaway click here"\n')
        
        result = self.analyzer.analyze_rejections()
        
        assert result['total_rejected_items'] == 10
        assert result['top_rejected_categories']['crypto'] == 10
        assert result['top_rejected_sources']['spam.com'] == 10
        assert 'bitcoin' in result['top_rejected_words']
        assert 'giveaway' in result['top_rejected_words']
        assert 'click' in result['top_rejected_words']
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Create log with high-frequency words
        with open(self.temp_log.name, 'w') as f:
            for i in range(20):
                f.write(f'[2025-01-01T{i:02d}:00:00Z] REJECTED: reason=pre_filter category=crypto source=spam.com title="Bitcoin giveaway scam"\n')
        
        result = self.analyzer.analyze_rejections()
        
        recommendations = result['recommendations']
        
        # Should recommend adding high-frequency words as stop markers
        assert len(recommendations['add_stop_markers']) > 0
        assert any(rec['word'] == 'bitcoin' for rec in recommendations['add_stop_markers'])
        assert any(rec['word'] == 'giveaway' for rec in recommendations['add_stop_markers'])
        
        # Should have high confidence for frequent words
        bitcoin_rec = next(rec for rec in recommendations['add_stop_markers'] if rec['word'] == 'bitcoin')
        assert bitcoin_rec['confidence'] >= 0.5
    
    def test_is_enabled(self):
        """Test enabled check."""
        assert self.analyzer.is_enabled() is True
        
        # Test disabled
        self.test_config['features']['auto_learn_enabled'] = False
        yaml.dump(self.test_config, open(self.temp_config.name, 'w'))
        
        analyzer_disabled = RejectionAnalyzer(self.temp_config.name)
        assert analyzer_disabled.is_enabled() is False


class TestAutoRuleManager:
    """Test auto rule manager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            'features': {
                'auto_learn_enabled': True,
                'auto_learn_backup_enabled': True
            }
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
        # Create temporary rules file
        self.temp_rules = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_rules.close()
        
        self.rule_manager = AutoRuleManager(self.temp_config.name)
        self.rule_manager.rules_path = Path(self.temp_rules.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()
        Path(self.temp_rules.name).unlink()
    
    def test_load_and_save_rules(self):
        """Test loading and saving rules."""
        test_rules = {
            'stop_markers': ['test', 'example'],
            'auto_generated': {
                'stop_markers': []
            }
        }
        
        # Save rules
        self.rule_manager._save_rules(test_rules)
        
        # Load rules
        loaded_rules = self.rule_manager._load_rules()
        
        assert loaded_rules == test_rules
    
    def test_add_stop_markers(self):
        """Test adding stop markers."""
        rules = {
            'stop_markers': ['existing'],
            'auto_generated': {
                'stop_markers': []
            }
        }
        
        recommendations = [
            {'word': 'newword', 'confidence': 0.8, 'count': 10},
            {'word': 'existing', 'confidence': 0.9, 'count': 15}  # Should not add duplicate
        ]
        
        added_count = self.rule_manager._add_stop_markers(rules, recommendations)
        
        assert added_count == 1  # Only one new word added
        assert len(rules['auto_generated']['stop_markers']) == 1
        assert rules['auto_generated']['stop_markers'][0]['word'] == 'newword'
        assert rules['auto_generated']['stop_markers'][0]['confidence'] == 0.8
    
    def test_add_source_blacklist(self):
        """Test adding sources to blacklist."""
        rules = {
            'auto_generated': {
                'source_blacklist': []
            }
        }
        
        recommendations = [
            {'source': 'spam.com', 'confidence': 0.8, 'count': 20},
            {'source': 'good.com', 'confidence': 0.3, 'count': 5}  # Low confidence, should not add
        ]
        
        added_count = self.rule_manager._add_source_blacklist(rules, recommendations)
        
        assert added_count == 1  # Only high confidence source added
        assert len(rules['auto_generated']['source_blacklist']) == 1
        assert rules['auto_generated']['source_blacklist'][0]['source'] == 'spam.com'
    
    def test_cleanup_old_rules(self):
        """Test cleanup of old rules."""
        old_date = datetime.now(timezone.utc) - timedelta(days=35)
        recent_date = datetime.now(timezone.utc) - timedelta(days=5)
        
        rules = {
            'auto_generated': {
                'stop_markers': [
                    {
                        'word': 'old_word',
                        'created_at': old_date.isoformat(),
                        'confidence': 0.5
                    },
                    {
                        'word': 'recent_word',
                        'created_at': recent_date.isoformat(),
                        'confidence': 0.6
                    },
                    {
                        'word': 'high_conf_old',
                        'created_at': old_date.isoformat(),
                        'confidence': 0.9  # High confidence, should keep
                    }
                ]
            }
        }
        
        removed_count = self.rule_manager._cleanup_old_rules(rules)
        
        assert removed_count == 1  # Only one rule removed (old_word)
        assert len(rules['auto_generated']['stop_markers']) == 2
        remaining_words = [rule['word'] for rule in rules['auto_generated']['stop_markers']]
        assert 'recent_word' in remaining_words
        assert 'high_conf_old' in remaining_words
        assert 'old_word' not in remaining_words
    
    @patch('ai_modules.auto_rule_manager.shutil.copy2')
    def test_create_backup(self, mock_copy):
        """Test backup creation."""
        mock_copy.return_value = None
        
        backup_path = self.rule_manager._create_backup()
        
        assert backup_path is not None
        mock_copy.assert_called_once()
    
    def test_apply_recommendations_disabled(self):
        """Test applying recommendations when disabled."""
        self.test_config['features']['auto_learn_enabled'] = False
        yaml.dump(self.test_config, open(self.temp_config.name, 'w'))
        
        rule_manager_disabled = AutoRuleManager(self.temp_config.name)
        rule_manager_disabled.rules_path = Path(self.temp_rules.name)
        
        analysis = {
            'recommendations': {
                'add_stop_markers': [{'word': 'test', 'confidence': 0.8, 'count': 10}],
                'source_blacklist': []
            }
        }
        
        result = rule_manager_disabled.apply_recommendations(analysis)
        
        assert result['success'] is True
        assert result['mode'] == 'recommendations_only'
    
    def test_get_active_auto_rules_count(self):
        """Test counting active auto rules."""
        rules = {
            'auto_generated': {
                'stop_markers': [
                    {'word': 'word1'},
                    {'word': 'word2'}
                ],
                'source_blacklist': [
                    {'source': 'spam.com'}
                ]
            }
        }
        
        # Save rules and test counting
        self.rule_manager._save_rules(rules)
        
        count = self.rule_manager.get_active_auto_rules_count()
        
        assert count == 3  # 2 stop markers + 1 blacklist entry
    
    def test_is_enabled(self):
        """Test enabled check."""
        assert self.rule_manager.is_enabled() is True
        
        # Test disabled
        self.test_config['features']['auto_learn_enabled'] = False
        yaml.dump(self.test_config, open(self.temp_config.name, 'w'))
        
        rule_manager_disabled = AutoRuleManager(self.temp_config.name)
        assert rule_manager_disabled.is_enabled() is False


class TestAutoLearningIntegration:
    """Test integration between analyzer and rule manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary files
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_rules = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        
        # Write test config
        config = {
            'features': {'auto_learn_enabled': True, 'auto_learn_min_samples': 5},
            'rejection_analysis': {
                'top_words_limit': 10,
                'frequency_threshold': 0.2
            }
        }
        yaml.dump(config, self.temp_config)
        self.temp_config.close()
        
        # Write initial rules
        initial_rules = {
            'stop_markers': ['existing'],
            'auto_generated': {'stop_markers': [], 'source_blacklist': []}
        }
        yaml.dump(initial_rules, self.temp_rules)
        self.temp_rules.close()
        
        # Write sample rejected log
        with open(self.temp_log.name, 'w') as f:
            for i in range(10):
                f.write(f'[2025-01-01T{i:02d}:00:00Z] REJECTED: reason=pre_filter category=crypto source=spam.com title="Bitcoin giveaway scam click here"\n')
        
        self.temp_log.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()
        Path(self.temp_rules.name).unlink()
        Path(self.temp_log.name).unlink()
    
    def test_full_auto_learning_workflow(self):
        """Test complete auto-learning workflow."""
        # Initialize components
        analyzer = RejectionAnalyzer(self.temp_config.name)
        analyzer.rejected_log_path = Path(self.temp_log.name)
        
        rule_manager = AutoRuleManager(self.temp_config.name)
        rule_manager.rules_path = Path(self.temp_rules.name)
        
        # Perform analysis
        analysis = analyzer.analyze_rejections()
        
        assert analysis['total_rejected_items'] == 10
        assert len(analysis['recommendations']['add_stop_markers']) > 0
        
        # Apply recommendations
        result = rule_manager.apply_recommendations(analysis)
        
        assert result['success'] is True
        assert result['changes']['rules_added'] > 0
        
        # Verify rules were updated
        updated_rules = rule_manager._load_rules()
        assert len(updated_rules['auto_generated']['stop_markers']) > 0
        
        # Check that high-frequency words were added
        added_words = [rule['word'] for rule in updated_rules['auto_generated']['stop_markers']]
        assert 'bitcoin' in added_words or 'giveaway' in added_words


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
