#!/usr/bin/env python3
"""
Test get_user_notifications function directly.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_models import get_user_notifications, get_user_by_telegram


def test_get_notifications():
    """Test get_user_notifications function."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Testing get_user_notifications function...")

        # Get user by telegram_id
        user_data = get_user_by_telegram(123)
        if not user_data:
            print("❌ User not found")
            return False

        user_id = user_data['id']
        print(f"✅ Found user: {user_id}")

        # Test direct Supabase query
        print("\n1. Testing direct Supabase query...")
        try:
            result = (
                supabase.table('user_notifications')
                .select('id, title, message, read, user_id')
                .eq('user_id', user_id)
                .order('id', desc=True)
                .limit(10)
                .execute()
            )
            print(f"✅ Direct query result: {len(result.data)} notifications")
            for notification in result.data:
                print(f"  - {notification['title']} (read: {notification['read']})")
        except Exception as e:
            print(f"❌ Direct query error: {e}")

        # Test our function
        print("\n2. Testing get_user_notifications function...")
        notifications = get_user_notifications(user_id=user_id, limit=10)
        print(f"✅ Function result: {len(notifications)} notifications")
        for notification in notifications:
            print(f"  - {notification['title']} (read: {notification['read']})")

        # Test with different user_id formats
        print("\n3. Testing with different user_id formats...")

        # Test with string UUID
        notifications_str = get_user_notifications(user_id=str(user_id), limit=10)
        print(f"✅ Function with string UUID result: {len(notifications_str)} notifications")

        # Test with int (should fail gracefully)
        try:
            notifications_int = get_user_notifications(user_id=123, limit=10)
            print(f"✅ Function with int result: {len(notifications_int)} notifications")
        except Exception as e:
            print(f"❌ Function with int error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Testing get_user_notifications function...")
    print("=" * 50)

    success = test_get_notifications()

    print("=" * 50)
    if success:
        print("✅ Test completed!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
