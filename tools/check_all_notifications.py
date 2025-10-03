#!/usr/bin/env python3
"""
Check all notifications in database.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_all_notifications():
    """Check all notifications."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking all notifications in database...")

        # Get all notifications
        try:
            result = supabase.table('user_notifications').select('*').execute()
            print(f"✅ Found {len(result.data)} notifications")

            if result.data:
                for notification in result.data:
                    print(f"  - ID: {notification['id']}")
                    print(f"    User ID: {notification['user_id']}")
                    print(f"    Title: {notification['title']}")
                    print(f"    Read: {notification['read']}")
                    print(f"    Category: {notification.get('category', 'N/A')}")
                    print()
            else:
                print("❌ No notifications found")

        except Exception as e:
            print(f"❌ Error getting notifications: {e}")

        # Check which user the notifications belong to
        print("\n🔍 Checking notification ownership...")
        try:
            result = supabase.table('user_notifications').select('user_id').execute()
            if result.data:
                user_ids = set(notification['user_id'] for notification in result.data)
                print(f"✅ Notifications belong to users: {user_ids}")

                # Check if these users exist
                for user_id in user_ids:
                    user_result = (
                        supabase.table('users').select('telegram_id').eq('id', user_id).execute()
                    )
                    if user_result.data:
                        telegram_id = user_result.data[0]['telegram_id']
                        print(f"  - User {user_id} has telegram_id: {telegram_id}")
                    else:
                        print(f"  - User {user_id} not found in users table")

        except Exception as e:
            print(f"❌ Error checking ownership: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Checking all notifications...")
    print("=" * 50)

    success = check_all_notifications()

    print("=" * 50)
    if success:
        print("✅ Check completed!")
        sys.exit(0)
    else:
        print("❌ Check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
