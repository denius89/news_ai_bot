#!/usr/bin/env python3
"""
Quick test for Smart Content Posting functionality.

This script tests the smart posting system components
including scheduler, teaser generator, and analytics.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot.services.content_scheduler import get_content_scheduler
from telegram_bot.services.post_selector import get_post_selector
from ai_modules.teaser_generator import get_teaser_generator
from ai_modules.metrics import get_metrics


def test_content_scheduler():
    """Test content scheduler functionality."""
    print("🕐 Testing Content Scheduler")
    print("-" * 40)
    
    try:
        scheduler = get_content_scheduler()
        
        print(f"Scheduler enabled: {scheduler.enabled}")
        print(f"Adaptive schedule: {scheduler.adaptive_schedule}")
        print(f"Total windows: {len(scheduler.time_windows)}")
        
        # Test time windows
        for window in scheduler.time_windows:
            print(f"  {window.name}: {window.start_hour}:00-{window.end_hour}:00 -> {window.categories}")
        
        # Test current window detection
        current_window = scheduler._get_current_window()
        if current_window:
            print(f"Current window: {current_window.name}")
            print(f"Current categories: {current_window.categories}")
        else:
            print("No current window detected")
        
        # Test schedule info
        schedule_info = scheduler.get_schedule_info()
        print(f"Schedule info: {schedule_info}")
        
        print("✅ Content scheduler test passed")
        return True
        
    except Exception as e:
        print(f"❌ Content scheduler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_post_selector():
    """Test post selector functionality."""
    print("\n⚖️ Testing Smart Post Selector")
    print("-" * 40)
    
    try:
        selector = get_post_selector()
        
        print(f"Selector enabled: {selector.enabled}")
        print(f"Max posts per cycle: {selector.max_posts_per_cycle}")
        print(f"Min importance threshold: {selector.min_importance_threshold}")
        print(f"Min credibility threshold: {selector.min_credibility_threshold}")
        
        # Test with mock digests
        mock_digests = [
            {
                'id': 1,
                'title': 'Bitcoin reaches new all-time high',
                'importance': 0.9,
                'credibility': 0.8,
                'category': 'crypto',
                'published': False,
                'status': 'ready'
            },
            {
                'id': 2,
                'title': 'Apple announces new iPhone',
                'importance': 0.7,
                'credibility': 0.9,
                'category': 'tech',
                'published': False,
                'status': 'ready'
            },
            {
                'id': 3,
                'title': 'Low quality spam news',
                'importance': 0.2,
                'credibility': 0.3,
                'category': 'unknown',
                'published': False,
                'status': 'ready'
            }
        ]
        
        # Test selection
        result = selector.select_digests(mock_digests)
        
        print(f"Selected digests: {len(result.selected_digests)}")
        print(f"Skipped count: {result.skipped_count}")
        print(f"Selection reason: {result.selection_reason}")
        print(f"Average score: {result.avg_score:.3f}")
        
        # Show selected digests
        for i, digest in enumerate(result.selected_digests, 1):
            score = selector._calculate_priority_score(digest)
            print(f"  {i}. {digest['title']} (score: {score:.3f})")
        
        # Test stats
        stats = selector.get_selection_stats()
        print(f"Selection stats: {stats}")
        
        print("✅ Post selector test passed")
        return True
        
    except Exception as e:
        print(f"❌ Post selector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_teaser_generator():
    """Test teaser generator functionality."""
    print("\n💬 Testing Teaser Generator")
    print("-" * 40)
    
    try:
        generator = get_teaser_generator()
        
        print(f"Generator enabled: {generator.enabled}")
        
        # Test category hashtags
        test_categories = ['crypto', 'tech', 'sports', 'world', 'markets']
        for category in test_categories:
            hashtags = generator._get_category_hashtags(category)
            print(f"  {category}: {hashtags}")
        
        # Test teaser generation (dry run without AI)
        generator.enabled = False  # Disable AI for testing
        
        test_digest = {
            'title': 'Ethereum 2.0 upgrade completes successfully',
            'summary': 'The long-awaited Ethereum 2.0 upgrade has been completed, bringing significant improvements to the network.',
            'category': 'crypto'
        }
        
        teaser_result = await generator.generate_teaser(
            test_digest['title'],
            test_digest['summary'],
            test_digest['category']
        )
        
        print(f"Generated teaser: {teaser_result.teaser}")
        print(f"Hashtags: {teaser_result.hashtags}")
        print(f"Confidence: {teaser_result.confidence:.3f}")
        
        # Test post formatting
        formatted_post = generator.format_teaser_post(teaser_result, test_digest)
        print(f"Formatted post length: {len(formatted_post)} characters")
        
        print("✅ Teaser generator test passed")
        return True
        
    except Exception as e:
        print(f"❌ Teaser generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_integration():
    """Test metrics integration for smart posting."""
    print("\n📊 Testing Metrics Integration")
    print("-" * 40)
    
    try:
        metrics = get_metrics()
        
        # Test new metrics methods
        metrics.increment_digests_published_today()
        metrics.update_autopublish_window_current("day")
        metrics.increment_autopublish_window_posts_total()
        metrics.increment_autopublish_skipped_out_of_window()
        metrics.update_smart_priority_avg_score(0.75)
        metrics.increment_smart_priority_skipped_total(5)
        metrics.increment_teaser_generated_total()
        metrics.update_avg_post_length_chars(450)
        metrics.update_avg_ai_confidence(0.8)
        metrics.increment_review_approved_total()
        metrics.increment_review_rejected_total()
        metrics.increment_reactions_total(25)
        metrics.update_avg_reaction_score(0.72)
        metrics.update_engagement_score_avg(0.68)
        metrics.increment_reactions_to_ai_updates_total()
        
        # Get metrics summary
        summary = metrics.get_metrics_summary()
        
        print("Smart Posting Metrics:")
        print(f"  Posts today: {summary.get('digests_published_today', 0)}")
        print(f"  Current window: {summary.get('autopublish_window_current', 'unknown')}")
        print(f"  Window posts total: {summary.get('autopublish_window_posts_total', 0)}")
        print(f"  Skipped out of window: {summary.get('autopublish_skipped_out_of_window_total', 0)}")
        print(f"  Smart priority avg score: {summary.get('smart_priority_avg_score', 0.0):.3f}")
        print(f"  Smart priority skipped: {summary.get('smart_priority_skipped_total', 0)}")
        print(f"  Teaser generated total: {summary.get('teaser_generated_total', 0)}")
        print(f"  Avg post length: {summary.get('avg_post_length_chars', 0)} chars")
        print(f"  Avg AI confidence: {summary.get('avg_ai_confidence', 0.0):.3f}")
        print(f"  Review approved: {summary.get('review_approved_total', 0)}")
        print(f"  Review rejected: {summary.get('review_rejected_total', 0)}")
        print(f"  Total reactions: {summary.get('reactions_total', 0)}")
        print(f"  Avg reaction score: {summary.get('avg_reaction_score', 0.0):.3f}")
        print(f"  Engagement score avg: {summary.get('engagement_score_avg', 0.0):.3f}")
        print(f"  Reactions to AI updates: {summary.get('reactions_to_ai_updates_total', 0)}")
        
        print("✅ Metrics integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Metrics integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_workflow():
    """Test integration workflow between components."""
    print("\n🔄 Testing Integration Workflow")
    print("-" * 40)
    
    try:
        # Initialize components
        scheduler = get_content_scheduler()
        selector = get_post_selector()
        generator = get_teaser_generator()
        
        # Mock digests
        mock_digests = [
            {
                'id': 1,
                'title': 'Bitcoin ETF approved by SEC',
                'summary': 'The SEC has approved the first Bitcoin ETF, marking a historic milestone for cryptocurrency adoption.',
                'importance': 0.95,
                'credibility': 0.9,
                'category': 'crypto',
                'published': False,
                'status': 'ready',
                'source': 'reuters.com'
            },
            {
                'id': 2,
                'title': 'Apple releases new MacBook Pro',
                'summary': 'Apple has unveiled its latest MacBook Pro with M3 chip and improved performance.',
                'importance': 0.8,
                'credibility': 0.85,
                'category': 'tech',
                'published': False,
                'status': 'ready',
                'source': 'apple.com'
            },
            {
                'id': 3,
                'title': 'Low quality spam content',
                'summary': 'This is clearly spam content with no real value.',
                'importance': 0.1,
                'credibility': 0.2,
                'category': 'unknown',
                'published': False,
                'status': 'ready',
                'source': 'spam-site.com'
            }
        ]
        
        print(f"Starting with {len(mock_digests)} digests")
        
        # Step 1: Filter by schedule
        scheduled_digests = scheduler.filter_digests_by_schedule(mock_digests)
        print(f"After schedule filtering: {len(scheduled_digests)} digests")
        
        # Step 2: Select best digests
        selection_result = selector.select_digests(scheduled_digests)
        print(f"After smart selection: {len(selection_result.selected_digests)} digests")
        print(f"Average priority score: {selection_result.avg_score:.3f}")
        
        # Step 3: Generate teasers (disabled for testing)
        generator.enabled = False
        for digest in selection_result.selected_digests:
            score = selector._calculate_priority_score(digest)
            print(f"  Selected: {digest['title']} (score: {score:.3f})")
        
        print("✅ Integration workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧠 PulseAI Smart Content Posting Test Suite")
    print("=" * 60)
    
    tests = [
        ("Content Scheduler", test_content_scheduler),
        ("Post Selector", test_post_selector),
        ("Teaser Generator", test_teaser_generator),
        ("Metrics Integration", test_metrics_integration),
        ("Integration Workflow", test_integration_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        print("\n💡 Next steps:")
        print("1. Configure smart_posting settings in ai_optimization.yaml")
        print("2. Set up admin_id for review mode")
        print("3. Run: DRY_RUN=true python tools/fetch_loop.py --auto-post --smart")
        print("4. Check analytics at /analytics/dashboard")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed!")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
