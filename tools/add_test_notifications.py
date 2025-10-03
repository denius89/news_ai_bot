#!/usr/bin/env python3
"""
Add test notifications to user_notifications table.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def add_test_notifications():
    """Add test notifications."""
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
    print("🚀 Adding test notifications...")
    print("=" * 50)

    success = add_test_notifications()

    print("=" * 50)
    if success:
        print("✅ Test notifications added successfully!")
        sys.exit(0)
    else:
        print("❌ Failed to add test notifications!")
        sys.exit(1)


if __name__ == "__main__":
    main()
