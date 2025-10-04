#!/usr/bin/env python3
"""
Debug user lookup functions.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_models import get_user_by_telegram


def debug_user_lookup():
    """Debug user lookup."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Debugging user lookup...")

        # Check all users in database
        print("\n1. All users in database:")
        try:
            result = supabase.table('users').select('*').execute()
            print(f"✅ Found {len(result.data)} users")
            for user in result.data:
                print(f"  - ID: {user['id']}, telegram_id: {user['telegram_id']}")
        except Exception as e:
            print(f"❌ Error getting users: {e}")

        # Test get_user_by_telegram function
        print("\n2. Testing get_user_by_telegram function...")

        # Test with different telegram_ids
        test_ids = [123456789, 123, 999999999, 888888888]

        for test_id in test_ids:
            print(f"\nTesting telegram_id: {test_id}")
            user_data = get_user_by_telegram(test_id)
            if user_data:
                print(f"✅ Found user: {user_data}")
            else:
                print("❌ User not found")

        # Test direct query
        print("\n3. Testing direct query...")
        try:
            result = supabase.table('users').select('*').eq('telegram_id', 123456789).execute()
            print(f"✅ Direct query result: {len(result.data)} users")
            for user in result.data:
                print(f"  - {user}")
        except Exception as e:
            print(f"❌ Direct query error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Debugging user lookup...")
    print("=" * 50)

    success = debug_user_lookup()

    print("=" * 50)
    if success:
        print("✅ Debug completed!")
        sys.exit(0)
    else:
        print("❌ Debug failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
