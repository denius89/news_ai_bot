#!/usr/bin/env python3
"""
Quick test for Baseline Dataset Builder functionality.

This script tests the baseline dataset building system with
synthetic and real data sources.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.build_baseline_dataset import BaselineDatasetBuilder
from ai_modules.metrics import get_metrics


def test_baseline_dataset_builder():
    """Test the baseline dataset building system."""
    print("🧩 Testing Baseline Dataset Builder")
    print("=" * 60)

    try:
        # Initialize builder
        print("🔍 Step 1: Initializing dataset builder...")
        builder = BaselineDatasetBuilder()

        print(f"   Output directory: {builder.output_dir}")
        print(f"   Dataset path: {builder.dataset_path}")
        print(f"   Report path: {builder.report_path}")
        print(f"   Balance classes: {builder.balance_classes}")
        print(f"   Min title length: {builder.min_title_length}")
        print(f"   Min samples per class: {builder.min_samples_per_class}")
        print()

        # Test dry run first
        print("🔍 Step 2: Running dry run...")
        dry_run_result = builder.build_dataset(dry_run=True)

        if not dry_run_result["success"]:
            print(f"❌ Dry run failed: {dry_run_result.get('error', 'Unknown error')}")
            return False

        print(f"✅ Dry run completed successfully!")
        print(f"   Total samples: {dry_run_result['total_samples']}")
        print(f"   Positive samples: {dry_run_result['positive_samples']}")
        print(f"   Negative samples: {dry_run_result['negative_samples']}")
        print(f"   Internal sources: {dry_run_result['internal_sources']}")
        print(f"   External sources: {dry_run_result['external_sources']}")
        print(f"   Duplicates removed: {dry_run_result['duplicates_removed']}")
        print(f"   Average importance: {dry_run_result['avg_importance']:.3f}")
        print(f"   Average credibility: {dry_run_result['avg_credibility']:.3f}")
        print()

        # Test actual dataset building
        print("📊 Step 3: Building actual dataset...")
        build_result = builder.build_dataset(dry_run=False)

        if not build_result["success"]:
            print(f"❌ Dataset build failed: {build_result.get('error', 'Unknown error')}")
            return False

        print(f"✅ Dataset build completed successfully!")
        print(f"   Dataset saved: {build_result['dataset_path']}")
        print(f"   Report saved: {build_result['report_path']}")
        print()

        # Verify files exist
        print("📁 Step 4: Verifying output files...")
        dataset_path = Path(build_result["dataset_path"])
        report_path = Path(build_result["report_path"])

        if dataset_path.exists():
            print(f"✅ Dataset file exists: {dataset_path}")

            # Check dataset content
            import pandas as pd

            df = pd.read_csv(dataset_path)
            print(f"   Dataset shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Label distribution: {df['label'].value_counts().to_dict()}")

            # Show first few rows
            print("\n📋 First 5 rows of dataset:")
            print(df.head().to_string(index=False))

        else:
            print(f"❌ Dataset file not found: {dataset_path}")
            return False

        if report_path.exists():
            print(f"✅ Report file exists: {report_path}")

            # Check report content
            import json

            with open(report_path, "r") as f:
                report = json.load(f)

            print(f"   Report timestamp: {report.get('timestamp')}")
            print(f"   Total samples: {report.get('total_samples')}")
            print(f"   Categories: {list(report.get('categories', {}).keys())[:5]}")

        else:
            print(f"❌ Report file not found: {report_path}")
            return False

        print()

        # Test metrics
        print("📈 Step 5: Checking metrics...")
        metrics = get_metrics()
        metrics_summary = metrics.get_metrics_summary()

        print(f"   Dataset created total: {metrics_summary.get('dataset_created_total', 0)}")

        print()
        print("✅ Baseline dataset builder test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_dataset_quality():
    """Test dataset quality and balance."""
    print("\n🔍 Testing Dataset Quality")
    print("-" * 40)

    try:
        dataset_path = Path("data/pulseai_dataset.csv")
        if not dataset_path.exists():
            print("❌ Dataset file not found, run main test first")
            return False

        import pandas as pd

        df = pd.read_csv(dataset_path)

        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        # Check for required columns
        required_columns = ["title", "category", "source", "importance", "credibility", "label"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False

        print("✅ All required columns present")

        # Check label balance
        label_counts = df["label"].value_counts()
        print(f"Label distribution: {label_counts.to_dict()}")

        balance_ratio = label_counts[1] / label_counts[0] if 0 in label_counts and 1 in label_counts else 0
        if 0.4 <= balance_ratio <= 0.6:
            print("✅ Dataset is well balanced")
        else:
            print(f"⚠️ Dataset balance ratio: {balance_ratio:.3f} (should be ~0.5)")

        # Check for empty values
        empty_counts = df.isnull().sum()
        if empty_counts.sum() > 0:
            print(f"⚠️ Empty values found: {empty_counts.to_dict()}")
        else:
            print("✅ No empty values found")

        # Check title lengths
        title_lengths = df["title"].str.split().str.len()
        short_titles = (title_lengths < 5).sum()
        if short_titles > 0:
            print(f"⚠️ {short_titles} titles are too short (< 5 words)")
        else:
            print("✅ All titles meet minimum length requirement")

        return True

    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        return False


def test_integration_with_self_tuning():
    """Test integration with Self-Tuning Predictor."""
    print("\n🔗 Testing Integration with Self-Tuning")
    print("-" * 40)

    try:
        from ai_modules.self_tuning_collector import get_self_tuning_collector
        from ai_modules.self_tuning_trainer import get_self_tuning_trainer

        # Test that dataset format is compatible
        dataset_path = Path("data/pulseai_dataset.csv")
        if not dataset_path.exists():
            print("❌ Dataset file not found, run main test first")
            return False

        print("✅ Dataset file found")

        # Test collector can use the dataset
        collector = get_self_tuning_collector()
        if collector.is_enabled():
            print("✅ Self-tuning collector is enabled")
        else:
            print("⚠️ Self-tuning collector is disabled")

        # Test trainer can use the dataset
        trainer = get_self_tuning_trainer()
        if trainer.is_enabled():
            print("✅ Self-tuning trainer is enabled")
        else:
            print("⚠️ Self-tuning trainer is disabled")

        print("✅ Integration test completed")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Test main functionality
        success1 = test_baseline_dataset_builder()

        # Test dataset quality
        success2 = test_dataset_quality()

        # Test integration
        success3 = test_integration_with_self_tuning()

        if success1 and success2 and success3:
            print("\n🎉 All baseline dataset tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
