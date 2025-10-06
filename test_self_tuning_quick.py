#!/usr/bin/env python3
"""
Quick test for Self-Tuning Predictor functionality.

This script tests the self-tuning system with synthetic data.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_modules.self_tuning_collector import get_self_tuning_collector
from ai_modules.self_tuning_trainer import get_self_tuning_trainer
from ai_modules.local_predictor import get_predictor
from ai_modules.metrics import get_metrics


def create_sample_training_data():
    """Create sample training data for testing."""
    from datetime import datetime, timezone, timedelta
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Create sample rejected entries
    sample_data = [
        {"category": "crypto", "source": "reuters.com", "reason": "ai_below_threshold", "title": "Bitcoin price rises as institutional adoption increases"},
        {"category": "crypto", "source": "bloomberg.com", "reason": "ai_below_threshold", "title": "Ethereum upgrade brings new features to blockchain"},
        {"category": "tech", "source": "techcrunch.com", "reason": "ai_below_threshold", "title": "New AI breakthrough promises faster computing"},
        {"category": "tech", "source": "wired.com", "reason": "ai_below_threshold", "title": "Cybersecurity experts warn of new threats"},
        {"category": "sports", "source": "espn.com", "reason": "ai_below_threshold", "title": "Championship game set for next weekend"},
        {"category": "sports", "source": "nfl.com", "reason": "ai_below_threshold", "title": "Player transfer creates buzz in league"},
        {"category": "world", "source": "bbc.com", "reason": "ai_below_threshold", "title": "International summit addresses climate change"},
        {"category": "world", "source": "cnn.com", "reason": "ai_below_threshold", "title": "Economic indicators show positive growth"},
    ]
    
    # Generate multiple entries for statistical significance
    base_time = datetime.now(timezone.utc)
    rejected_log_path = Path("logs/rejected.log")
    
    with open(rejected_log_path, 'w', encoding='utf-8') as f:
        for i in range(100):  # Generate 100 entries
            for data in sample_data:
                entry_time = base_time.replace(hour=i % 24, minute=i % 60)
                timestamp = entry_time.isoformat()
                category = data["category"]
                source = data["source"]
                reason = data["reason"]
                title = data["title"]
                
                log_line = f'[{timestamp}] REJECTED: reason={reason} category={category} source={source} title="{title}"'
                f.write(log_line + '\n')
    
    print(f"Created sample rejected.log with {len(sample_data) * 100} entries")
    return len(sample_data) * 100


def test_self_tuning_system():
    """Test the complete self-tuning system."""
    print("🧩 Testing Self-Tuning Predictor System")
    print("=" * 60)
    
    # Create sample data if needed
    rejected_log_path = Path("logs/rejected.log")
    if not rejected_log_path.exists():
        print("📝 Creating sample rejected.log...")
        sample_count = create_sample_training_data()
        print(f"✅ Created {sample_count} sample entries")
        print()
    
    try:
        # Initialize components
        print("🔍 Step 1: Initializing components...")
        collector = get_self_tuning_collector()
        trainer = get_self_tuning_trainer()
        predictor = get_predictor()
        metrics = get_metrics()
        
        print(f"   Collector enabled: {collector.is_enabled()}")
        print(f"   Trainer enabled: {trainer.is_enabled()}")
        print(f"   Predictor enabled: {predictor.is_enabled()}")
        print(f"   Model type: {trainer.model_type}")
        print()
        
        # Collect training data
        print("📊 Step 2: Collecting training data...")
        collection_result = collector.collect_training_data()
        
        if not collection_result['success']:
            print(f"❌ Data collection failed: {collection_result.get('error', 'Unknown error')}")
            return False
        
        dataset_size = collection_result['dataset_size']
        print(f"✅ Collected {dataset_size} training examples")
        
        # Display dataset statistics
        stats = collection_result.get('statistics', {})
        print(f"   Database examples: {collection_result.get('db_examples', 0)}")
        print(f"   Rejected examples: {collection_result.get('rejected_examples', 0)}")
        print(f"   Importance positive: {stats.get('importance_positive', 0)}")
        print(f"   Credibility positive: {stats.get('credibility_positive', 0)}")
        print(f"   Sources: {list(stats.get('sources', {}).keys())[:3]}")
        print(f"   Categories: {list(stats.get('categories', {}).keys())}")
        print()
        
        # Train models
        print("🤖 Step 3: Training models...")
        dataset_path = Path(collection_result['dataset_path'])
        
        training_result = trainer.train_models(dataset_path)
        
        if not training_result['success']:
            print(f"❌ Model training failed: {training_result.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ Model training completed successfully!")
        print(f"   Features count: {training_result.get('features_count', 0)}")
        print(f"   Train size: {training_result.get('train_size', 0)}")
        print(f"   Test size: {training_result.get('test_size', 0)}")
        print()
        
        # Display training results
        improvements = training_result.get('improvements', {})
        
        print("📈 Training Results:")
        total_improvements = 0
        for model_name, result in improvements.items():
            f1_score = result.get('f1_score', 0.0)
            improvement = result.get('improvement', 0.0)
            replaced = result.get('replaced', False)
            
            status = "✅ REPLACED" if replaced else "⏸️ NOT REPLACED"
            print(f"   {model_name.title()} model: F1={f1_score:.3f}, improvement={improvement:.3f} ({status})")
            
            if replaced:
                total_improvements += 1
        
        print()
        
        # Test prediction with trained models
        print("🔮 Step 4: Testing predictions...")
        
        # Reload models to test prediction
        trainer.load_models()
        
        # Test news items
        test_items = [
            {
                'title': 'Breaking: Major cryptocurrency exchange announces new partnership',
                'content': 'The partnership will bring new features to users and improve security.',
                'source': 'coindesk.com',
                'category': 'crypto',
                'published_at': '2025-10-06T10:00:00Z'
            },
            {
                'title': 'Click here for free Bitcoin giveaway scam',
                'content': 'Get rich quick with this amazing opportunity.',
                'source': 'spam-site.com',
                'category': 'crypto',
                'published_at': '2025-10-06T10:00:00Z'
            }
        ]
        
        for i, item in enumerate(test_items, 1):
            prediction = predictor.predict(item)
            print(f"   Test {i}: importance={prediction.importance:.3f}, credibility={prediction.credibility:.3f}, confidence={prediction.confidence:.3f}")
            print(f"          Title: {item['title'][:50]}...")
        
        print()
        
        # Update metrics
        print("📊 Step 5: Updating metrics...")
        metrics.update_self_tuning_last_run(training_result.get('timestamp', ''))
        metrics.update_self_tuning_dataset_size(dataset_size)
        
        # Update model version
        model_info = trainer.get_model_info()
        metrics.update_self_tuning_model_version(model_info.get('version', 0))
        
        # Display final metrics
        print("📈 Final Self-Tuning Metrics:")
        metrics_summary = metrics.get_metrics_summary()
        print(f"   Total runs: {metrics_summary['self_tuning_runs_total']}")
        print(f"   Models trained: {metrics_summary['self_tuning_models_trained_total']}")
        print(f"   Models replaced: {metrics_summary['self_tuning_models_replaced_total']}")
        print(f"   Current version: {metrics_summary['self_tuning_current_model_version']}")
        print(f"   Dataset size: {metrics_summary['self_tuning_dataset_size']}")
        print(f"   Last run: {metrics_summary['self_tuning_last_run_timestamp']}")
        
        print()
        print("✅ Self-tuning system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction_comparison():
    """Test prediction comparison between rule-based and ML models."""
    print("\n🔄 Testing Prediction Comparison")
    print("-" * 40)
    
    try:
        predictor = get_predictor()
        
        # Temporarily disable self-tuning to test rule-based prediction
        original_enabled = predictor.self_tuning_enabled
        predictor.self_tuning_enabled = False
        
        test_item = {
            'title': 'Breaking: Major cryptocurrency exchange announces new partnership',
            'content': 'The partnership will bring new features to users and improve security.',
            'source': 'coindesk.com',
            'category': 'crypto',
            'published_at': '2025-10-06T10:00:00Z'
        }
        
        # Rule-based prediction
        rule_prediction = predictor.predict(test_item)
        print(f"Rule-based: importance={rule_prediction.importance:.3f}, credibility={rule_prediction.credibility:.3f}")
        
        # ML model prediction (if available)
        predictor.self_tuning_enabled = original_enabled
        if predictor.self_tuning_enabled and predictor.self_tuning_trainer:
            try:
                ml_prediction = predictor.predict(test_item)
                print(f"ML model:    importance={ml_prediction.importance:.3f}, credibility={ml_prediction.credibility:.3f}")
                
                # Compare results
                importance_diff = abs(ml_prediction.importance - rule_prediction.importance)
                credibility_diff = abs(ml_prediction.credibility - rule_prediction.credibility)
                
                print(f"Difference:  importance={importance_diff:.3f}, credibility={credibility_diff:.3f}")
            except Exception as e:
                print(f"ML prediction failed: {e}")
        else:
            print("ML models not available for comparison")
        
        return True
        
    except Exception as e:
        print(f"❌ Prediction comparison failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Test full system
        success1 = test_self_tuning_system()
        
        # Test prediction comparison
        success2 = test_prediction_comparison()
        
        if success1 and success2:
            print("\n🎉 All self-tuning tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
