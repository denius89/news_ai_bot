#!/usr/bin/env python3
"""
Fix user_notifications table schema to use UUID instead of BIGINT.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def fix_schema():
    """Fix user_notifications table schema."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking current user_notifications table...")

        # Drop and recreate table with correct schema
        try:
            print("🗑️  Dropping existing user_notifications table...")
            supabase.rpc(
                'exec_sql', {'sql': 'DROP TABLE IF EXISTS user_notifications CASCADE;'}
            ).execute()
            print("✅ Dropped existing table")
        except Exception as e:
            print(f"⚠️  Error dropping table: {e}")

        print("🔧 Creating user_notifications table with correct schema...")

        # Create table with UUID reference
        try:
            supabase.rpc(
                'exec_sql',
                {
                    'sql': '''
                CREATE TABLE user_notifications (
                  id           BIGSERIAL PRIMARY KEY,
                  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                  title        TEXT NOT NULL,
                  text         TEXT NOT NULL,
                  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                  read         BOOLEAN NOT NULL DEFAULT FALSE
                );
                '''
                },
            ).execute()
            print("✅ Created user_notifications table with UUID reference")
        except Exception as e:
            print(f"❌ Could not create table: {e}")
            return False

        # Create index
        try:
            supabase.rpc(
                'exec_sql',
                {
                    'sql': '''
                CREATE INDEX idx_user_notifications_user_read_created
                  ON user_notifications (user_id, read, created_at DESC);
                '''
                },
            ).execute()
            print("✅ Created index")
        except Exception as e:
            print(f"⚠️  Could not create index: {e}")

        print("📝 Adding test data...")

        # Add test data using first user
        try:
            users_  # result = supabase.table('users').select('id').limit(1).execute()
            if users_result.data:
                user_id = users_result.data[0]['id']
                print(f"Using user_id: {user_id}")

                test_notifications = [
                    {
                        'user_id': user_id,
                        'title': 'Новый дайджест готов!',
                        'text': 'Ваш утренний дайджест с последними новостями готов к прочтению.',
                        'read': False,
                    },
                    {
                        'user_id': user_id,
                        'title': 'Важное событие',
                        'text': 'Сегодня в 15:00 ожидается важное экономическое событие в США.',
                        'read': True,
                    },
                ]

                # result = supabase.table('user_notifications').insert(test_notifications).execute()
                print(f"✅ Added {len(test_notifications)} test notifications")

                # Verify data
                verify_  # result = supabase.table('user_notifications').select('*').execute()
                print(f"✅ Verification: {len(verify_result.data)} notifications in table")
                for notification in verify_result.data:
                    print(f"  - {notification['title']} (read: {notification['read']})")

            else:
                print("⚠️  No users found, skipping test data")

        except Exception as e:
            print(f"⚠️  Could not add test data: {e}")

        print("✅ Schema fix completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Fixing user_notifications schema...")
    print("=" * 50)

    success = fix_schema()

    print("=" * 50)
    if success:
        print("✅ Schema fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Schema fix failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
