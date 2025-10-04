#!/usr/bin/env python3
"""
Add test notifications with correct schema (including category).
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
    """Add test notifications with correct schema."""
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
                'message': 'Ваш утренний дайджест с последними новостями готов к прочтению.',
                'category': 'digest',
                'read': False,
            },
            {
                'user_id': user_id,
                'title': 'Важное событие',
                'message': 'Сегодня в 15:00 ожидается важное экономическое событие в США.',
                'category': 'events',
                'read': True,
            },
            {
                'user_id': user_id,
                'title': 'Bitcoin обновил максимум',
                'message': 'Криптовалюта Bitcoin достигла нового исторического максимума.',
                'category': 'crypto',
                'read': False,
            },
            {
                'user_id': user_id,
                'title': 'Новое уведомление',
                'message': 'Это тестовое уведомление для проверки API.',
                'category': 'general',
                'read': False,
            },
        ]

        try:
            result = supabase.table('user_notifications').insert(test_notifications).execute()
            if result.data:
                print(f"✅ Added {len(result.data)} test notifications")

                # Show added notifications
                for notification in result.data:
                    print(
                "telegram_id": 123456789
                    )

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
    print("🚀 Adding test notifications with correct schema...")
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
