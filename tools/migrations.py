#!/usr/bin/env python3
"""
Unified Migration Tool for PulseAI.

This tool consolidates all database migration operations into a single interface.
Replaces multiple add_*.py and apply_*.py scripts.
"""

import argparse
import logging
import sys

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from database.service import get_sync_service  # noqa: E402
from utils.error_handler import DatabaseError, handle_database_error  # noqa: E402

logger = logging.getLogger("migrations")


class MigrationTool:
    """Unified tool for database migrations."""

    def __init__(self):
        self.service = get_sync_service()
        if not self.service.sync_client:
            raise DatabaseError("Database service not initialized")

    @handle_database_error("add subcategory field")
    def add_subcategory_field(self):
        """Add subcategory field to news and events tables."""
        logger.info("🔄 Adding subcategory field to tables...")

        # Add to news table
        try:
            self.service.sync_client.rpc(
                'add_column_if_not_exists',
                {'table_name': 'news', 'column_name': 'subcategory', 'column_type': 'text'},
            ).execute()
            logger.info("✅ Added subcategory field to 'news' table")
        except Exception as e:
            logger.error(f"❌ Error adding subcategory to 'news': {e}")

        # Add to events table
        try:
            self.service.sync_client.rpc(
                'add_column_if_not_exists',
                {'table_name': 'events', 'column_name': 'subcategory', 'column_type': 'text'},
            ).execute()
            logger.info("✅ Added subcategory field to 'events' table")
        except Exception as e:
            logger.error(f"❌ Error adding subcategory to 'events': {e}")

    @handle_database_error("add notifications table")
    def add_notifications_table(self):
        """Create user notifications table."""
        logger.info("🔄 Creating user notifications table...")

        # Check if table exists
        try:
            result = (
                self.service.sync_client.table("user_notifications").select("*").limit(1).execute()
            )
            logger.info("✅ User notifications table already exists")
            return
        except Exception:
            pass  # Table doesn't exist, create it

        # Create table
        create_sql = """
        CREATE TABLE IF NOT EXISTS user_notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            via_telegram BOOLEAN DEFAULT FALSE,
            via_webapp BOOLEAN DEFAULT FALSE,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        
        CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_notifications_read ON user_notifications(read);
        """

        try:
            # Execute the SQL
            self.service.sync_client.rpc('exec_sql', {'sql': create_sql}).execute()
            logger.info("✅ Created user notifications table")
        except Exception as e:
            logger.error(f"❌ Error creating user notifications table: {e}")

    @handle_database_error("add test notifications")
    def add_test_notifications(self, user_id: str = "test-user-123"):
        """Add test notifications for a user."""
        logger.info(f"🔄 Adding test notifications for user {user_id}...")

        test_notifications = [
            {
                "user_id": user_id,
                "title": "Тестовая уведомление 1",
                "text": "Это первая тестовая уведомление",
                "via_telegram": True,
                "via_webapp": True,
                "read": False,
            },
            {
                "user_id": user_id,
                "title": "Тестовая уведомление 2",
                "text": "Это вторая тестовая уведомление",
                "via_telegram": False,
                "via_webapp": True,
                "read": True,
            },
            {
                "user_id": user_id,
                "title": "Важное уведомление",
                "text": "Это важное уведомление для тестирования",
                "via_telegram": True,
                "via_webapp": True,
                "read": False,
            },
        ]

        try:
            result = (
                self.service.sync_client.table("user_notifications")
                .insert(test_notifications)
                .execute()
            )
            logger.info(f"✅ Added {len(test_notifications)} test notifications")
        except Exception as e:
            logger.error(f"❌ Error adding test notifications: {e}")

    @handle_database_error("apply subcategory migration")
    def apply_subcategory_migration(self):
        """Apply subcategory migration."""
        logger.info("🔄 Applying subcategory migration...")

        # Add subcategory field
        self.add_subcategory_field()

        # Check if migration was successful
        try:
            # Check news table
            news_result = self.service.sync_client.table("news").select("*").limit(1).execute()
            if news_result.data and 'subcategory' in news_result.data[0]:
                logger.info("✅ Subcategory field found in 'news' table")
            else:
                logger.warning("⚠️ Subcategory field not found in 'news' table")

            # Check events table
            events_result = self.service.sync_client.table("events").select("*").limit(1).execute()
            if events_result.data and 'subcategory' in events_result.data[0]:
                logger.info("✅ Subcategory field found in 'events' table")
            else:
                logger.warning("⚠️ Subcategory field not found in 'events' table")

        except Exception as e:
            logger.error(f"❌ Error checking migration: {e}")

    @handle_database_error("apply user notifications migration")
    def apply_user_notifications_migration(self):
        """Apply user notifications migration."""
        logger.info("🔄 Applying user notifications migration...")

        # Create notifications table
        self.add_notifications_table()

        # Add test notifications
        self.add_test_notifications()

        logger.info("✅ User notifications migration completed")


def main():
    """Main function for migration tool."""
    parser = argparse.ArgumentParser(description="PulseAI Migration Tool")
    parser.add_argument(
        "action",
        choices=[
            "add-subcategory",
            "add-notifications",
            "add-test-notifications",
            "apply-subcategory",
            "apply-notifications",
            "apply-all",
        ],
        help="Migration action to perform",
    )

    parser.add_argument(
        "--user-id",
        default="test-user-123",
        help="User ID for test notifications (default: test-user-123)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    try:
        tool = MigrationTool()

        if args.action == "add-subcategory":
            tool.add_subcategory_field()
        elif args.action == "add-notifications":
            tool.add_notifications_table()
        elif args.action == "add-test-notifications":
            tool.add_test_notifications(args.user_id)
        elif args.action == "apply-subcategory":
            tool.apply_subcategory_migration()
        elif args.action == "apply-notifications":
            tool.apply_user_notifications_migration()
        elif args.action == "apply-all":
            tool.apply_subcategory_migration()
            tool.apply_user_notifications_migration()

        logger.info("🎉 Migration completed successfully")

    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
