#!/usr/bin/env python3
"""
Quick test for Auto-Learning Filter functionality.

This script tests the auto-learning system with synthetic data.
"""

from ai_modules.metrics import get_metrics
from ai_modules.auto_rule_manager import get_auto_rule_manager
from ai_modules.rejection_analyzer import get_rejection_analyzer
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def create_sample_rejected_log():
    """Create sample rejected.log for testing."""
    from datetime import datetime, timezone, timedelta

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Create sample rejected entries
    sample_data = [
        {
            "category": "crypto",
            "source": "cryptoblog.fake.io",
            "reason": "pre_filter",
            "title": "Bitcoin giveaway scam - click here to claim",
        },
        {
            "category": "crypto",
            "source": "earnmoney.today",
            "reason": "pre_filter",
            "title": "Make money with cryptocurrency trading signals",
        },
        {
            "category": "crypto",
            "source": "spamcrypto.com",
            "reason": "pre_filter",
            "title": "Free Bitcoin giveaway - click here now",
        },
        {
            "category": "tech",
            "source": "spamtech.blog",
            "reason": "pre_filter",
            "title": "Sponsored: Best antivirus software 2025",
        },
        {
            "category": "tech",
            "source": "fake-tech.com",
            "reason": "pre_filter",
            "title": "Click here to download free software",
        },
        {
            "category": "sports",
            "source": "sportsfake.news",
            "reason": "pre_filter",
            "title": "Click here to watch live sports streams",
        },
        {
            "category": "sports",
            "source": "spam-sports.io",
            "reason": "pre_filter",
            "title": "Free sports streaming - click here",
        },
    ]

    # Generate multiple entries for statistical significance
    base_time = datetime.now(timezone.utc)
    rejected_log_path = Path("logs/rejected.log")

    with open(rejected_log_path, "w", encoding="utf-8") as f:
        for i in range(50):  # Generate 50 entries
            for data in sample_data:
                entry_time = base_time.replace(hour=i % 24, minute=i % 60)
                timestamp = entry_time.isoformat()
                category = data["category"]
                source = data["source"]
                reason = data["reason"]
                title = data["title"]

                log_line = (
                    f'[{timestamp}] REJECTED: reason={reason} category={category} source={source} title="{title}"'
                )
                f.write(log_line + "\n")

    print(f"Created sample rejected.log with {len(sample_data) * 50} entries")
    return len(sample_data) * 50


def test_auto_learning_system():
    """Test the complete auto-learning system."""
    print("🧠 Testing Auto-Learning Filter System")
    print("=" * 60)

    # Create sample data if needed
    rejected_log_path = Path("logs/rejected.log")
    if not rejected_log_path.exists():
        print("📝 Creating sample rejected.log...")
        sample_count = create_sample_rejected_log()
        print(f"✅ Created {sample_count} sample entries")
        print()

    try:
        # Initialize components
        print("🔍 Step 1: Initializing components...")
        analyzer = get_rejection_analyzer()
        rule_manager = get_auto_rule_manager()
        metrics = get_metrics()

        print(f"   Analyzer enabled: {analyzer.is_enabled()}")
        print(f"   Rule manager enabled: {rule_manager.is_enabled()}")
        print()

        # Perform analysis
        print("📊 Step 2: Analyzing rejected news items...")
        analysis = analyzer.analyze_rejections()

        if analysis["total_rejected_items"] == 0:
            print("⚠️ No rejected items found for analysis")
            return False

        print(f"✅ Analyzed {analysis['total_rejected_items']} rejected items")
        print(f"   Analysis period: {analysis['analysis_period_days']} days")

        # Display top categories
        print("\n📈 Top rejected categories:")
        for category, count in list(analysis["top_rejected_categories"].items())[:3]:
            print(f"   {category}: {count}")

        # Display top sources
        print("\n🌐 Top rejected sources:")
        for source, count in list(analysis["top_rejected_sources"].items())[:3]:
            print(f"   {source}: {count}")

        # Display top words
        print("\n📝 Top rejected words:")
        for word, count in list(analysis["top_rejected_words"].items())[:5]:
            print(f"   {word}: {count}")

        # Display recommendations
        recommendations = analysis["recommendations"]
        print(f"\n💡 Recommendations:")
        print(f"   Add stop markers: {len(recommendations['add_stop_markers'])}")
        print(f"   Source blacklist: {len(recommendations['source_blacklist'])}")
        print(f"   Rule adjustments: {len(recommendations['rule_adjustments'])}")

        if recommendations["add_stop_markers"]:
            print("\n📝 Stop markers to add:")
            for rec in recommendations["add_stop_markers"][:5]:
                print(
                    f"   '{rec['word']}' (confidence: {rec['confidence']:.2f}, count: {rec['count']})")

        if recommendations["source_blacklist"]:
            print("\n🚫 Sources to blacklist:")
            for rec in recommendations["source_blacklist"][:3]:
                print(
                    f"   '{rec['source']}' (confidence: {rec['confidence']:.2f}, count: {rec['count']})")

        print()

        # Apply recommendations
        print("🔧 Step 3: Applying auto-learning recommendations...")
        result = rule_manager.apply_recommendations(analysis)

        if result.get("success"):
            changes = result.get("changes", {})
            print(f"✅ Auto-learning completed successfully!")
            print(f"   Rules added: {changes.get('rules_added', 0)}")
            print(f"   Rules removed: {changes.get('rules_removed', 0)}")
            print(f"   Backups created: {changes.get('backups_created', 0)}")

            if result.get("backup_path"):
                print(f"   Backup saved: {result['backup_path']}")
        else:
            print(f"❌ Auto-learning failed: {result.get('error', 'Unknown error')}")
            return False

        print()

        # Check updated rules
        print("📋 Step 4: Checking updated rules...")
        active_rules_count = rule_manager.get_active_auto_rules_count()
        print(f"   Active auto rules: {active_rules_count}")

        # Update metrics
        metrics.update_auto_rules_active_count(active_rules_count)
        metrics.update_auto_learn_last_success(result["timestamp"])

        # Display final metrics
        print("\n📈 Final Auto-Learning Metrics:")
        metrics_summary = metrics.get_metrics_summary()
        print(f"   Total runs: {metrics_summary['auto_learn_runs_total']}")
        print(f"   Rules added: {metrics_summary['auto_rules_added_total']}")
        print(f"   Rules removed: {metrics_summary['auto_rules_removed_total']}")
        print(f"   Active rules: {metrics_summary['auto_rules_active_total']}")
        print(f"   Last success: {metrics_summary['auto_learn_last_success_timestamp']}")

        print()
        print("✅ Auto-learning system test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_analysis_only_mode():
    """Test analysis-only mode (without applying changes)."""
    print("\n🔍 Testing Analysis-Only Mode")
    print("-" * 40)

    try:
        # Temporarily disable auto-learning
        import os

        original_env = os.environ.get("AUTO_LEARN_ENABLED")
        os.environ["AUTO_LEARN_ENABLED"] = "false"

        analyzer = get_rejection_analyzer()
        analysis = analyzer.analyze_rejections()

        print(f"✅ Analysis completed: {analysis['total_rejected_items']} items")
        print(
            f"   Recommendations: {len(analysis['recommendations']['add_stop_markers'])} stop markers")

        # Restore environment
        if original_env is not None:
            os.environ["AUTO_LEARN_ENABLED"] = original_env
        else:
            os.environ.pop("AUTO_LEARN_ENABLED", None)

        return True

    except Exception as e:
        print(f"❌ Analysis-only test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Test full system
        success1 = test_auto_learning_system()

        # Test analysis-only mode
        success2 = test_analysis_only_mode()

        if success1 and success2:
            print("\n🎉 All auto-learning tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
