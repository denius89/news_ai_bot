#!/usr/bin/env python3
"""
Check users table structure and data.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_users_table():
    """Check users table structure and data."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking users table structure...")

        # Check users table
        try:
            result = supabase.table('users').select('*').limit(3).execute()
            if result.data:
                print(f"✅ Found {len(result.data)} users")
                print(f"Columns: {list(result.data[0].keys())}")
                for user in result.data:
                    print(f"  User: {user}")
            else:
                print("❌ No users found")

                # Try to create a test user
                print("🔧 Creating test user...")
                test_user = {'telegram_id': 123456789}
                create_result = supabase.table('users').insert(test_user).execute()
                if create_result.data:
                    print(f"✅ Created test user: {create_result.data[0]}")
                else:
                    print("❌ Failed to create test user")

        except Exception as e:
            print(f"❌ Error checking users table: {e}")

        print("\n🔍 Checking user_notifications table...")

        # Check user_notifications table
        try:
            result = supabase.table('user_notifications').select('*').limit(3).execute()
            if result.data:
                print(f"✅ Found {len(result.data)} notifications")
                print(f"Columns: {list(result.data[0].keys())}")
                for notification in result.data:
                    print(f"  Notification: {notification}")
            else:
                print("❌ No notifications found")
        except Exception as e:
            print(f"❌ Error checking user_notifications table: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Checking database tables...")
    print("=" * 50)

    success = check_users_table()

    print("=" * 50)
    if success:
        print("✅ Check completed!")
        sys.exit(0)
    else:
        print("❌ Check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
