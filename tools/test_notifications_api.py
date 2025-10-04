#!/usr/bin/env python3
"""
Test notifications API directly.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from database.db_models import get_user_notifications, get_user_by_telegram

# Add project root to Python path
project_root = Path(__file__).parent.parent


def test_notifications():
    """Test notifications functions directly."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Testing notifications functions...")

        # Test 1: Get user by telegram_id
        print("\n1. Testing get_user_by_telegram...")
        user_data = get_user_by_telegram(123456789)
        if user_data:
            print(f"✅ Found user: {user_data}")
            user_id = user_data['id']
        else:
            print("❌ User not found")
            return False

        # Test 2: Get notifications directly from database
        print("\n2. Testing direct database query...")
        try:
            result = (
                supabase.table('user_notifications').select('*').eq('user_id', user_id).execute()
            )
            print(f"✅ Direct query result: {len(result.data)} notifications")
            for notification in result.data:
                print(f"  - {notification['title']} (read: {notification['read']})")
        except Exception as e:
            print(f"❌ Direct query error: {e}")

        # Test 3: Get notifications using our function
        print("\n3. Testing get_user_notifications function...")
        notifications = get_user_notifications(user_id=user_id, limit=10)
        print(f"✅ Function result: {len(notifications)} notifications")
        for notification in notifications:
            print(f"  - {notification['title']} (read: {notification['read']})")

        # Test 4: Test with telegram_id
        print("\n4. Testing get_user_notifications with telegram_id...")
        user_data_2 = get_user_by_telegram(123456789)
        if user_data_2:
            notifications_2 = get_user_notifications(user_id=user_data_2['id'], limit=10)
            print(f"✅ Function with telegram_id result: {len(notifications_2)} notifications")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Testing notifications API...")
    print("=" * 50)

    success = test_notifications()

    print("=" * 50)
    if success:
        print("✅ Test completed!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
