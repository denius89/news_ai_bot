#!/usr/bin/env python3
"""
Create user_notifications table and add test data.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_table_and_data():
    """Create table and add test data."""
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
            print("✅ user_notifications table exists")
            if result.data:
                print(f"Found {len(result.data)} existing notifications")
                return True
        except Exception as e:
            print(f"❌ Table doesn't exist or error: {e}")

        print("📋 Please create the table manually in Supabase SQL Editor:")
        print("=" * 60)
        print("""
-- Create user_notifications table
CREATE TABLE user_notifications (
  id           BIGSERIAL PRIMARY KEY,
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  text         TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  read         BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create index
CREATE INDEX idx_user_notifications_user_read_created
  ON user_notifications (user_id, read, created_at DESC);
        """)
        print("=" * 60)
        print("After creating the table, run this script again to add test data.")

        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def add_test_data():
    """Add test data to existing table."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Getting first user...")

        # Get first user
        users_result = supabase.table('users').select('id').limit(1).execute()
        if not users_result.data:
            print("❌ No users found")
            return False
            
        user_id = users_result.data[0]['id']
        print(f"✅ Using user_id: {user_id}")

        print("📝 Adding test notifications...")

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
            },
            {
                'user_id': user_id,
                'title': 'Bitcoin обновил максимум',
                'text': 'Криптовалюта Bitcoin достигла нового исторического максимума.',
                'read': False
            }
        ]

        try:
            result = supabase.table('user_notifications').insert(test_notifications).execute()
            if result.data:
                print(f"✅ Added {len(result.data)} test notifications")
                
                # Show added notifications
                for notification in result.data:
                    print(f"  - {notification['title']} (read: {notification['read']})")
                    
                return True
            else:
                print("❌ Failed to add notifications")
                return False
                
        except Exception as e:
            print(f"❌ Error adding notifications: {e}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Setting up user_notifications table...")
    print("=" * 50)

    # First try to add test data
    success = add_test_data()
    
    if not success:
        print("\n🔧 Table setup required...")
        create_table_and_data()

    print("=" * 50)
    if success:
        print("✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Setup failed! Please create table manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()
