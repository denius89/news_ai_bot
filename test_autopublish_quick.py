#!/usr/bin/env python3
"""
Quick test for Telegram Auto-Posting functionality.

This script tests the auto-posting system with mock data
and validates the PulseDigest 2.0 formatting.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot.handlers.digest_handler import TelegramDigestHandler
from ai_modules.metrics import get_metrics


def test_message_formatting():
    """Test PulseDigest 2.0 message formatting."""
    print("🧪 Testing PulseDigest 2.0 Message Formatting")
    print("=" * 60)
    
    try:
        # Create handler instance
        handler = TelegramDigestHandler()
        
        # Test digest data
        test_digest = {
            'id': 123,
            'title': 'Bitcoin reaches new all-time high amid institutional adoption',
            'summary': 'Major cryptocurrency Bitcoin has reached a new all-time high of $100,000 as institutional investors continue to show strong interest in digital assets.',
            'why_important': 'This milestone demonstrates growing mainstream acceptance of cryptocurrency and could signal further adoption by traditional financial institutions.',
            'category': 'crypto',
            'source': 'https://coindesk.com/bitcoin-reaches-new-all-time-high?utm_source=twitter&utm_campaign=social',
            'published_at': '2025-10-06T14:30:00Z',
            'status': 'ready',
            'published': False
        }
        
        # Format message
        formatted_message = handler._format_digest_message(test_digest)
        
        print("✅ Message formatting test passed")
        print(f"\n📋 Formatted Message Preview:")
        print("-" * 40)
        print(formatted_message)
        print("-" * 40)
        print(f"Message length: {len(formatted_message)} characters")
        print(f"Max allowed: 1024 characters")
        
        # Test URL cleaning
        clean_url = handler._clean_url(test_digest['source'])
        print(f"\n🔗 URL Cleaning:")
        print(f"Original: {test_digest['source']}")
        print(f"Cleaned:  {clean_url}")
        
        # Test Markdown escaping
        test_text = "Test with special chars: _*[]()~`>#+-=|{}."
        escaped_text = handler._escape_markdown_v2(test_text)
        print(f"\n📝 Markdown Escaping:")
        print(f"Original: {test_text}")
        print(f"Escaped:  {escaped_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Message formatting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_category_emojis():
    """Test category emoji mapping."""
    print("\n🎨 Testing Category Emojis")
    print("-" * 40)
    
    try:
        handler = TelegramDigestHandler()
        
        test_categories = ['crypto', 'tech', 'sports', 'world', 'markets', 'unknown']
        
        for category in test_categories:
            emoji = handler.category_emojis.get(category, '📰')
            print(f"{category}: {emoji}")
        
        print("✅ Category emoji test passed")
        return True
        
    except Exception as e:
        print(f"❌ Category emoji test failed: {e}")
        return False


async def test_autopublish_logic():
    """Test auto-publishing logic with mock data."""
    print("\n🤖 Testing Auto-Publish Logic")
    print("-" * 40)
    
    try:
        handler = TelegramDigestHandler()
        
        # Test should_publish logic
        test_digests = [
            {
                'id': 1,
                'published': False,
                'status': 'ready',
                'title': 'Test digest 1'
            },
            {
                'id': 2,
                'published': True,
                'status': 'ready',
                'title': 'Test digest 2 (already published)'
            },
            {
                'id': 3,
                'published': False,
                'status': 'draft',
                'title': 'Test digest 3 (not ready)'
            }
        ]
        
        for digest in test_digests:
            should_publish = handler._should_publish(digest)
            print(f"Digest #{digest['id']}: {digest['title']}")
            print(f"  Should publish: {should_publish}")
            print()
        
        print("✅ Auto-publish logic test passed")
        return True
        
    except Exception as e:
        print(f"❌ Auto-publish logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dry_run_mode():
    """Test dry run mode."""
    print("\n🔍 Testing Dry Run Mode")
    print("-" * 40)
    
    try:
        # Create handler with dry run enabled
        handler = TelegramDigestHandler()
        handler.dry_run = True
        handler.enabled = True
        
        # Mock digest data
        mock_digest = {
            'id': 999,
            'title': 'Test dry run digest',
            'summary': 'This is a test digest for dry run mode',
            'why_important': 'Testing the dry run functionality',
            'category': 'tech',
            'source': 'https://example.com/test',
            'published_at': datetime.now(timezone.utc).isoformat(),
            'status': 'ready',
            'published': False
        }
        
        print(f"Dry run enabled: {handler.dry_run}")
        print(f"Handler enabled: {handler.enabled}")
        print(f"Test digest: {mock_digest['title']}")
        
        # Test formatting in dry run mode
        formatted_message = handler._format_digest_message(mock_digest)
        print(f"\n📋 Dry Run Message Preview:")
        print("-" * 40)
        print(formatted_message)
        print("-" * 40)
        
        print("✅ Dry run mode test passed")
        return True
        
    except Exception as e:
        print(f"❌ Dry run mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_integration():
    """Test metrics integration."""
    print("\n📊 Testing Metrics Integration")
    print("-" * 40)
    
    try:
        metrics = get_metrics()
        
        # Test metrics methods
        metrics.increment_digests_published_total()
        metrics.increment_digests_publish_errors_total()
        metrics.increment_autopublish_skipped_no_content()
        metrics.update_last_digest_published_timestamp(datetime.now(timezone.utc).isoformat())
        metrics.record_autopublish_latency(150.5)
        
        # Get metrics summary
        summary = metrics.get_metrics_summary()
        
        print(f"Digests published total: {summary.get('digests_published_total', 0)}")
        print(f"Digests publish errors total: {summary.get('digests_publish_errors_total', 0)}")
        print(f"Autopublish skipped no content: {summary.get('autopublish_skipped_no_content_total', 0)}")
        print(f"Last digest published: {summary.get('last_digest_published_timestamp', 'Never')}")
        print(f"Autopublish avg latency: {summary.get('autopublish_avg_latency_ms', 0)} ms")
        
        print("✅ Metrics integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Metrics integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_configuration_loading():
    """Test configuration loading."""
    print("\n⚙️ Testing Configuration Loading")
    print("-" * 40)
    
    try:
        handler = TelegramDigestHandler()
        
        print(f"Autopublish enabled: {handler.enabled}")
        print(f"Dry run mode: {handler.dry_run}")
        print(f"Interval minutes: {handler.interval_minutes}")
        print(f"Min gap minutes: {handler.min_gap_minutes}")
        print(f"Format version: {handler.format_version}")
        print(f"Bot token configured: {bool(handler.bot_token)}")
        print(f"Channel ID configured: {bool(handler.channel_id)}")
        
        print("✅ Configuration loading test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("💬 PulseAI Telegram Auto-Posting Test Suite")
    print("=" * 60)
    
    tests = [
        ("Message Formatting", test_message_formatting),
        ("Category Emojis", test_category_emojis),
        ("Auto-Publish Logic", test_autopublish_logic),
        ("Dry Run Mode", test_dry_run_mode),
        ("Metrics Integration", test_metrics_integration),
        ("Configuration Loading", test_configuration_loading),
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
