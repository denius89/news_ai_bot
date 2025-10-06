#!/usr/bin/env python3
"""
Simple test for Telegram Auto-Posting functionality.

This script tests the auto-posting system with mock data
and demonstrates the PulseDigest 2.0 formatting.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot.handlers.digest_handler import TelegramDigestHandler
from ai_modules.metrics import get_metrics


async def test_autopublish_dry_run():
    """Test auto-posting in dry run mode."""
    print("🤖 Testing Auto-Posting in Dry Run Mode")
    print("=" * 60)

    try:
        # Create handler with dry run enabled
        handler = TelegramDigestHandler()
        handler.dry_run = True
        handler.enabled = True

        print(f"Handler configuration:")
        print(f"  Dry run: {handler.dry_run}")
        print(f"  Enabled: {handler.enabled}")
        print(f"  Bot token configured: {bool(handler.bot_token)}")
        print(f"  Channel ID configured: {bool(handler.channel_id)}")
        print()

        # Test message formatting
        test_digest = {
            "id": 123,
            "title": "Bitcoin reaches new all-time high amid institutional adoption",
            "summary": "Major cryptocurrency Bitcoin has reached a new all-time high of $100,000 as institutional investors continue to show strong interest in digital assets.",
            "why_important": "This milestone demonstrates growing mainstream acceptance of cryptocurrency and could signal further adoption by traditional financial institutions.",
            "category": "crypto",
            "source": "https://coindesk.com/bitcoin-reaches-new-all-time-high?utm_source=twitter&utm_campaign=social",
            "published_at": "2025-10-06T14:30:00Z",
            "status": "ready",
            "published": False,
        }

        # Format message
        formatted_message = handler._format_digest_message(test_digest)

        print("📋 Formatted Message (PulseDigest 2.0):")
        print("-" * 60)
        print(formatted_message)
        print("-" * 60)
        print(f"Message length: {len(formatted_message)} characters")
        print(f"Max allowed: 1024 characters")
        print()

        # Test URL cleaning
        clean_url = handler._clean_url(test_digest["source"])
        print("🔗 URL Cleaning:")
        print(f"Original: {test_digest['source']}")
        print(f"Cleaned:  {clean_url}")
        print()

        # Test Markdown escaping
        test_text = "Test with special chars: _*[]()~`>#+-=|{}."
        escaped_text = handler._escape_markdown_v2(test_text)
        print("📝 Markdown Escaping:")
        print(f"Original: {test_text}")
        print(f"Escaped:  {escaped_text}")
        print()

        # Test should_publish logic
        should_publish = handler._should_publish(test_digest)
        print(f"Should publish digest #{test_digest['id']}: {should_publish}")
        print()

        # Test metrics
        metrics = get_metrics()
        metrics.increment_digests_published_total()
        metrics.increment_autopublish_skipped_no_content()
        metrics.record_autopublish_latency(150.5)

        summary = metrics.get_metrics_summary()
        print("📊 Metrics Summary:")
        print(f"  Digests published total: {summary.get('digests_published_total', 0)}")
        print(f"  Autopublish skipped no content: {summary.get('autopublish_skipped_no_content_total', 0)}")
        print(f"  Autopublish avg latency: {summary.get('autopublish_avg_latency_ms', 0)} ms")
        print()

        print("✅ Dry run test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Dry run test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_message_formatting_examples():
    """Test different message formatting examples."""
    print("📝 Testing Different Message Formatting Examples")
    print("=" * 60)

    try:
        handler = TelegramDigestHandler()

        test_cases = [
            {
                "title": "Apple announces new M3 chips with advanced AI capabilities",
                "summary": "Apple has unveiled its latest M3 processor lineup featuring significant improvements in AI performance and energy efficiency.",
                "why_important": "The M3 chips represent a major leap in mobile computing power and could accelerate AI adoption in consumer devices.",
                "category": "tech",
                "source": "https://apple.com/newsroom/m3-chips-announcement?utm_source=press&utm_campaign=launch",
            },
            {
                "title": "Manchester City wins Champions League final",
                "summary": "Manchester City secured their first-ever Champions League title with a 2-1 victory over Real Madrid in the final.",
                "why_important": "This victory completes Manchester City's quest for European glory and cements their status as one of Europe's elite clubs.",
                "category": "sports",
                "source": "https://uefa.com/champions-league/final-result",
            },
            {
                "title": "Federal Reserve announces interest rate decision",
                "summary": "The Federal Reserve has decided to maintain current interest rates while signaling potential future adjustments based on economic indicators.",
                "why_important": "Interest rate decisions have significant impact on global markets, inflation, and economic growth prospects.",
                "category": "markets",
                "source": "https://federalreserve.gov/monetary-policy/decision",
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"Example {i} - {test_case['category'].upper()}:")
            print("-" * 40)

            # Format message
            formatted_message = handler._format_digest_message(
                {
                    **test_case,
                    "id": i,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "status": "ready",
                    "published": False,
                }
            )

            print(formatted_message)
            print(f"Length: {len(formatted_message)} characters")
            print()

        print("✅ Message formatting examples test completed!")
        return True

    except Exception as e:
        print(f"❌ Message formatting examples test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_category_emojis():
    """Test all category emojis."""
    print("🎨 Testing Category Emojis")
    print("=" * 60)

    try:
        handler = TelegramDigestHandler()

        categories = [
            ("crypto", "Cryptocurrency and blockchain news"),
            ("tech", "Technology and innovation updates"),
            ("sports", "Sports events and results"),
            ("world", "World news and politics"),
            ("markets", "Financial markets and economy"),
            ("unknown", "Uncategorized content"),
        ]

        for category, description in categories:
            emoji = handler.category_emojis.get(category, "📰")
            print(f"{emoji} {category}: {description}")

        print()
        print("✅ Category emojis test completed!")
        return True

    except Exception as e:
        print(f"❌ Category emojis test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("💬 PulseAI Telegram Auto-Posting Simple Test")
    print("=" * 60)

    tests = [
        ("Dry Run Mode", test_autopublish_dry_run),
        ("Message Formatting Examples", test_message_formatting_examples),
        ("Category Emojis", test_category_emojis),
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
        print("1. Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID in .env")
        print("2. Run: DRY_RUN=false python tools/fetch_loop.py --auto-post")
        print("3. Check logs/publish.log for publishing results")
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
