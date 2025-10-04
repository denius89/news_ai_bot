#!/usr/bin/env python3
"""
Check all possible columns in user_notifications table.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_all_columns():
    """Check all possible columns."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking all possible columns in user_notifications table...")

        # Try to get table info by selecting all columns
        try:
            result = supabase.table('user_notifications').select('*').limit(1).execute()
            if result.data:
                print("📋 Current table structure:")
                print(f"Columns: {list(result.data[0].keys())}")
                print(f"Sample data: {result.data[0]}")
            else:
                print("\n📋 Table exists but is empty")

                # Try to get table schema by attempting insert with minimal data
                print("\n🔍 Trying to determine required columns by test insert...")
                test_data = {
                    'user_id': 'f7d38911-4e62-4012-a9bf-2aaa03483497',
                    'title': 'Test',
                    'message': 'Test message',
                }

                try:
                    test_result = supabase.table('user_notifications').insert(test_data).execute()
                    print("✅ Test insert successful - no additional required columns")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Test insert failed: {error_msg}")

                    # Try to parse error for required columns
                    if 'null value in column' in error_msg:
                        # Extract column name from error
                        import re

                        match = re.search(r'null value in column "([^"]+)"', error_msg)
                        if match:
                            required_column = match.group(1)
                            print(f"⚠️  Required column found: {required_column}")

                            # Try with category column
                            test_data_with_category = test_data.copy()
                            test_data_with_category['category'] = 'general'

                            try:
                                supabase.table('user_notifications').insert(
                                    test_data_with_category
                                ).execute()
                                print("✅ Test insert with category successful")
                            except Exception as e2:
                                print(f"❌ Test insert with category failed: {e2}")

        except Exception as e:
            print(f"\n❌ Error getting table data: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Checking all columns in user_notifications...")
    print("=" * 50)

    success = check_all_columns()

    print("=" * 50)
    if success:
        print("✅ Column check completed!")
        sys.exit(0)
    else:
        print("❌ Column check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
