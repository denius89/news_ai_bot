#!/usr/bin/env python3
"""
Self-Tuning Model Training Tool.

This tool trains and updates the local predictor models using
collected training data from the database and rejected logs.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_modules.self_tuning_collector import get_self_tuning_collector
from ai_modules.self_tuning_trainer import get_self_tuning_trainer
from ai_modules.metrics import get_metrics


def setup_logging():
    """Setup logging for the training tool."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/self_tuning.log', mode='a')
        ]
    )


def main():
    """Main function for self-tuning model training."""
    setup_logging()
    logger = logging.getLogger("train_self_tuning")
    
    print("🧩 PulseAI Self-Tuning Predictor Training")
    print("=" * 60)
    
    try:
        # Initialize components
        collector = get_self_tuning_collector()
        trainer = get_self_tuning_trainer()
        metrics = get_metrics()
        
        print("🔍 Step 1: Checking self-tuning configuration...")
        
        if not collector.is_enabled() or not trainer.is_enabled():
            print("⚠️ Self-tuning is disabled in configuration")
            return
        
        print(f"   Self-tuning enabled: {collector.is_enabled()}")
        print(f"   Auto-train enabled: {trainer.is_enabled()}")
        print(f"   Model type: {trainer.model_type}")
        print(f"   Replace threshold: {trainer.replace_threshold}")
        print()
        
        # Check if we need to train based on interval
        should_train = _should_train_now(trainer)
        if not should_train:
            print("⏰ Training not needed yet (within interval)")
            return
        
        # Collect training data
        print("📊 Step 2: Collecting training data...")
        collection_result = collector.collect_training_data()
        
        if not collection_result['success']:
            print(f"❌ Data collection failed: {collection_result.get('error', 'Unknown error')}")
            return
        
        dataset_size = collection_result['dataset_size']
        print(f"✅ Collected {dataset_size} training examples")
        
        # Display dataset statistics
        stats = collection_result.get('statistics', {})
        print(f"   Database examples: {collection_result.get('db_examples', 0)}")
        print(f"   Rejected examples: {collection_result.get('rejected_examples', 0)}")
        print(f"   Importance positive: {stats.get('importance_positive', 0)}")
        print(f"   Credibility positive: {stats.get('credibility_positive', 0)}")
        print()
        
        # Train models
        print("🤖 Step 3: Training models...")
        dataset_path = Path(collection_result['dataset_path'])
        
        training_result = trainer.train_models(dataset_path)
        
        if not training_result['success']:
            print(f"❌ Model training failed: {training_result.get('error', 'Unknown error')}")
            return
        
        print(f"✅ Model training completed successfully!")
        print(f"   Features count: {training_result.get('features_count', 0)}")
        print(f"   Train size: {training_result.get('train_size', 0)}")
        print(f"   Test size: {training_result.get('test_size', 0)}")
        print()
        
        # Display training results
        improvements = training_result.get('improvements', {})
        
        print("📈 Training Results:")
        for model_name, result in improvements.items():
            f1_score = result.get('f1_score', 0.0)
            improvement = result.get('improvement', 0.0)
            replaced = result.get('replaced', False)
            
            status = "✅ REPLACED" if replaced else "⏸️ NOT REPLACED"
            print(f"   {model_name.title()} model: F1={f1_score:.3f}, improvement={improvement:.3f} ({status})")
        
        print()
        
        # Update metrics
        print("📊 Step 4: Updating metrics...")
        metrics.update_self_tuning_last_run(training_result.get('timestamp', ''))
        metrics.update_self_tuning_dataset_size(dataset_size)
        
        # Update model version
        model_info = trainer.get_model_info()
        metrics.update_self_tuning_model_version(model_info.get('version', 0))
        
        # Display final metrics
        print("📈 Current Self-Tuning Metrics:")
        metrics_summary = metrics.get_metrics_summary()
        print(f"   Total runs: {metrics_summary['self_tuning_runs_total']}")
        print(f"   Models trained: {metrics_summary['self_tuning_models_trained_total']}")
        print(f"   Models replaced: {metrics_summary['self_tuning_models_replaced_total']}")
        print(f"   Current version: {metrics_summary['self_tuning_current_model_version']}")
        print(f"   Dataset size: {metrics_summary['self_tuning_dataset_size']}")
        print(f"   Last run: {metrics_summary['self_tuning_last_run_timestamp']}")
        
        print()
        print("🎉 Self-tuning training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in self-tuning training: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _should_train_now(trainer) -> bool:
    """
    Check if training should be performed based on interval.
    
    Args:
        trainer: SelfTuningTrainer instance
        
    Returns:
        True if training should be performed, False otherwise
    """
    try:
        from datetime import datetime, timezone, timedelta
        
        # Get last training timestamp from metadata
        metadata = trainer._load_existing_metadata()
        last_training_str = metadata.get('timestamp')
        
        if not last_training_str:
            logger.info("No previous training found, proceeding with training")
            return True
        
        # Parse last training timestamp
        last_training = datetime.fromisoformat(last_training_str.replace('Z', '+00:00'))
        
        # Calculate interval
        interval_days = trainer.config.get('self_tuning', {}).get('interval_days', 2)
        next_training = last_training + timedelta(days=interval_days)
        
        now = datetime.now(timezone.utc)
        
        if now >= next_training:
            logger.info(f"Training interval reached: {interval_days} days since last training")
            return True
        else:
            remaining = next_training - now
            logger.info(f"Training interval not reached: {remaining} remaining")
            return False
            
    except Exception as e:
        logger.warning(f"Error checking training interval: {e}, proceeding with training")
        return True


if __name__ == "__main__":
    main()
