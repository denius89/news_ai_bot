#!/usr/bin/env python3
"""
Apply database migration to create user_notifications table.

This script creates the user_notifications table and adds test data.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def apply_migration():
    """Apply the migration to create user_notifications table."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking if user_notifications table exists...")

        # Check if table exists
        try:
            result = supabase.table('user_notifications').select('*').limit(1).execute()
            print("✅ user_notifications table already exists")
            print(f"Current columns: {list(result.data[0].keys()) if result.data else 'No data'}")
        except Exception as e:
            print(f"Table doesn't exist yet: {e}")
            print("🔧 Creating user_notifications table...")

            # Create table
            try:
                supabase.rpc('exec_sql', {
                    'sql': '''
                    CREATE TABLE IF NOT EXISTS user_notifications (
                      id           BIGSERIAL PRIMARY KEY,
                      user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                      title        TEXT NOT NULL,
                      text         TEXT NOT NULL,
                      created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                      read         BOOLEAN NOT NULL DEFAULT FALSE
                    );
                    '''
                }).execute()
                print("✅ Created user_notifications table")
            except Exception as e:
                print(f"❌ Could not create table: {e}")
                return False

            # Create index
            try:
                supabase.rpc('exec_sql', {
                    'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_user_notifications_user_read_created
                      ON user_notifications (user_id, read, created_at DESC);
                    '''
                }).execute()
                print("✅ Created index")
            except Exception as e:
                print(f"⚠️  Could not create index: {e}")

        print("🔍 Checking for test data...")

        # Check if we have test data
        try:
            result = supabase.table('user_notifications').select('*').limit(1).execute()
            if result.data:
                print(f"✅ Found {len(result.data)} existing notifications")
            else:
                print("📝 Adding test data...")
                
                # Add test data
                try:
                    # First, check if we have a user
                    users_result = supabase.table('users').select('id').limit(1).execute()
                    if users_result.data:
                        user_id = users_result.data[0]['id']
                        
                        # Insert test notifications
                        test_notifications = [
                            {
                                'user_id': user_id,
                                'title': 'Новый дайджест готов!',
                                'text': 'Ваш утренний дайджест с последними новостями готов к прочтению.',
                                'read': False
                            },
                            {
                                'user_id': user_id,
                                'title': 'Важное событие',
                                'text': 'Сегодня в 15:00 ожидается важное экономическое событие в США.',
                                'read': True
                            }
                        ]
                        
                        result = supabase.table('user_notifications').insert(test_notifications).execute()
                        print(f"✅ Added {len(test_notifications)} test notifications")
                    else:
                        print("⚠️  No users found, skipping test data")
                        
                except Exception as e:
                    print(f"⚠️  Could not add test data: {e}")

        except Exception as e:
            print(f"Error checking test data: {e}")

        print("✅ Migration applied successfully!")
        return True

    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Applying user_notifications migration...")
    print("=" * 50)

    success = apply_migration()

    print("=" * 50)
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
