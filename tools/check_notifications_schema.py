#!/usr/bin/env python3
"""
Check user_notifications table schema.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_schema():
    """Check table schema."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking user_notifications table schema...")

        # Try to get table info by attempting different column names
        test_columns = [
            'id',
            'title',
            'text',
            'content',
            'message',
            'user_id',
            'created_at',
            'read',
        ]

        for col in test_columns:
            try:
                result = supabase.table('user_notifications').select(col).limit(1).execute()
                print(f"✅ Column '{col}' exists")
            except Exception as e:
                print(f"❌ Column '{col}' doesn't exist: {e}")

        # Try to get any data
        try:
            result = supabase.table('user_notifications').select('*').limit(1).execute()
            if result.data:
                print(f"\n📋 Current table structure:")
                print(f"Columns: {list(result.data[0].keys())}")
                print(f"Sample data: {result.data[0]}")
            else:
                print("\n📋 Table exists but is empty")
        except Exception as e:
            print(f"\n❌ Error getting table data: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Checking user_notifications schema...")
    print("=" * 50)

    success = check_schema()

    print("=" * 50)
    if success:
        print("✅ Schema check completed!")
        sys.exit(0)
    else:
        print("❌ Schema check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
