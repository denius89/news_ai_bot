#!/usr/bin/env python3
"""
Rejection Analysis Tool for Auto-Learning Filter.

This tool analyzes rejected news items and applies auto-learning
recommendations to improve prefilter rules.
"""

from ai_modules.metrics import get_metrics
from ai_modules.auto_rule_manager import get_auto_rule_manager
from ai_modules.rejection_analyzer import get_rejection_analyzer
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_logging():
    """Setup logging for the analysis tool."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("logs/auto_learn.log", mode="a")],
    )


def create_sample_rejected_log():
    """Create sample rejected.log for testing purposes."""
    import json
    from datetime import datetime, timezone, timedelta

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Create sample rejected entries
    sample_entries = []
    base_time = datetime.now(timezone.utc) - timedelta(days=7)

    # Sample rejection data
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
            "source": "reuters.com",
            "reason": "ai_below_threshold",
            "title": "Bitcoin price moves slightly in trading session",
        },
        {
            "category": "tech",
            "source": "spamtech.blog",
            "reason": "pre_filter",
            "title": "Sponsored: Best antivirus software 2025",
        },
        {
            "category": "tech",
            "source": "techcrunch.com",
            "reason": "ai_below_threshold",
            "title": "Minor bug fix released for popular app",
        },
        {
            "category": "sports",
            "source": "sportsfake.news",
            "reason": "pre_filter",
            "title": "Click here to watch live sports streams",
        },
        {
            "category": "sports",
            "source": "espn.com",
            "reason": "duplicate",
            "title": "Football match results from yesterday",
        },
        {
            "category": "world",
            "source": "worldnews.fake",
            "reason": "pre_filter",
            "title": "Breaking: You won't believe what happened",
        },
    ]

    # Generate multiple entries for each sample
    for i in range(50):  # Generate 50 entries for statistical significance
        for data in sample_data:
            entry_time = base_time + timedelta(hours=i)
            entry = {
                "timestamp": entry_time.isoformat(),
                "category": data["category"],
                "source": data["source"],
                "reason": data["reason"],
                "title": data["title"],
            }
            sample_entries.append(entry)

    # Write to rejected.log
    rejected_log_path = Path("logs/rejected.log")
    with open(rejected_log_path, "w", encoding="utf-8") as f:
        for entry in sample_entries:
            timestamp = entry["timestamp"]
            category = entry["category"]
            source = entry["source"]
            reason = entry["reason"]
            title = entry["title"]

            log_line = f'[{timestamp}] REJECTED: reason={reason} category={category} source={source} title="{title}"'
            f.write(log_line + "\n")

    print(f"Created sample rejected.log with {len(sample_entries)} entries")
    return len(sample_entries)


def main():
    """Main function for rejection analysis."""
    setup_logging()
    logger = logging.getLogger("analyze_rejections")

    print("🧠 PulseAI Auto-Learning Filter - Rejection Analysis")
    print("=" * 60)

    # Check if rejected.log exists, create sample if not
    rejected_log_path = Path("logs/rejected.log")
    if not rejected_log_path.exists():
        print("📝 Creating sample rejected.log for demonstration...")
        sample_count = create_sample_rejected_log()
        print(f"✅ Created {sample_count} sample rejection entries")
        print()

    try:
        # Initialize components
        analyzer = get_rejection_analyzer()
        rule_manager = get_auto_rule_manager()
        metrics = get_metrics()

        print("🔍 Step 1: Analyzing rejected news items...")

        # Perform analysis
        analysis = analyzer.analyze_rejections()

        if analysis["total_rejected_items"] == 0:
            print("⚠️ No rejected items found for analysis")
            return

        print(f"✅ Analyzed {analysis['total_rejected_items']} rejected items")
        print()

        # Display analysis summary
        print("📊 Analysis Results:")
        print(f"   Period: {analysis['analysis_period_days']} days")
        print(f"   Top categories: {list(analysis['top_rejected_categories'].keys())[:3]}")
        print(f"   Top sources: {list(analysis['top_rejected_sources'].keys())[:3]}")
        print(f"   Top words: {list(analysis['top_rejected_words'].keys())[:5]}")
        print()

        # Display recommendations
        recommendations = analysis["recommendations"]
        print("💡 Recommendations:")
        print(f"   Add stop markers: {len(recommendations['add_stop_markers'])}")
        print(f"   Source blacklist: {len(recommendations['source_blacklist'])}")
        print(f"   Rule adjustments: {len(recommendations['rule_adjustments'])}")
        print()

        if not recommendations["add_stop_markers"] and not recommendations["source_blacklist"]:
            print("✅ No new rules recommended at this time")
            return

        # Show specific recommendations
        if recommendations["add_stop_markers"]:
            print("📝 Stop markers to add:")
            for rec in recommendations["add_stop_markers"][:5]:
                print(
                    f"   '{rec['word']}' (confidence: {rec['confidence']:.2f}, count: {rec['count']})")
            print()

        if recommendations["source_blacklist"]:
            print("🚫 Sources to blacklist:")
            for rec in recommendations["source_blacklist"][:3]:
                print(
                    f"   '{rec['source']}' (confidence: {rec['confidence']:.2f}, count: {rec['count']})")
            print()

        # Apply recommendations
        print("🔧 Step 2: Applying auto-learning recommendations...")

        result = rule_manager.apply_recommendations(analysis)

        if result.get("success"):
            changes = result.get("changes", {})
            print(f"✅ Auto-learning completed successfully!")
            print(f"   Rules added: {changes.get('rules_added', 0)}")
            print(f"   Rules removed: {changes.get('rules_removed', 0)}")
            print(f"   Backups created: {changes.get('backups_created', 0)}")

            if result.get("backup_path"):
                print(f"   Backup saved: {result['backup_path']}")

            # Update metrics
            metrics.update_auto_rules_active_count(rule_manager.get_active_auto_rules_count())
            metrics.update_auto_learn_last_success(result["timestamp"])

        else:
            print(f"❌ Auto-learning failed: {result.get('error', 'Unknown error')}")

        print()

        # Display current metrics
        print("📈 Current Auto-Learning Metrics:")
        metrics_summary = metrics.get_metrics_summary()
        print(f"   Total runs: {metrics_summary['auto_learn_runs_total']}")
        print(f"   Rules added: {metrics_summary['auto_rules_added_total']}")
        print(f"   Rules removed: {metrics_summary['auto_rules_removed_total']}")
        print(f"   Active rules: {metrics_summary['auto_rules_active_total']}")
        print(f"   Last success: {metrics_summary['auto_learn_last_success_timestamp']}")

        print()
        print("🎉 Auto-learning analysis completed!")

    except Exception as e:
        logger.error(f"Error in rejection analysis: {e}")
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
