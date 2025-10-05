#!/usr/bin/env python3
"""
Database Inspector Tool for PulseAI.

This tool consolidates all database inspection and checking operations.
Replaces multiple check_*.py scripts.
"""

import argparse
import logging
import sys
from typing import Dict, List, Optional

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from database.service import get_sync_service  # noqa: E402
from utils.error_handler import DatabaseError, handle_database_error  # noqa: E402

logger = logging.getLogger("database_inspector")


class DatabaseInspector:
    """Unified tool for database inspection and checking."""

    def __init__(self):
        self.service = get_sync_service()
        if not self.service.sync_client:
            raise DatabaseError("Database service not initialized")

    @handle_database_error("check all columns")
    def check_all_columns(self) -> Dict[str, List[str]]:
        """Check all columns in all tables."""
        logger.info("🔍 Checking all columns in database tables...")

        tables = ["users", "news", "events", "subscriptions", "notifications", "user_notifications"]
        results = {}

        for table in tables:
            try:
                result = self.service.sync_client.table(table).select("*").limit(1).execute()
                if result.data:
                    columns = list(result.data[0].keys())
                    results[table] = columns
                    logger.info(f"✅ {table}: {len(columns)} columns")
                    logger.debug(f"   Columns: {', '.join(columns)}")
                else:
                    results[table] = []
                    logger.warning(f"⚠️ {table}: no data found")
            except Exception as e:
                logger.error(f"❌ {table}: error checking columns - {e}")
                results[table] = []

        return results

    @handle_database_error("check users table")
    def check_users_table(self) -> Dict:
        """Check users table structure and data."""
        logger.info("🔍 Checking users table...")

        try:
            result = self.service.sync_client.table("users").select("*").limit(5).execute()

            if not result.data:
                logger.warning("⚠️ Users table is empty")
                return {"count": 0, "columns": [], "sample": []}

            columns = list(result.data[0].keys())
            count_result = (
                self.service.sync_client.table("users").select("id", count="exact").execute()
            )
            total_count = count_result.count if hasattr(count_result, 'count') else len(result.data)

            info = {
                "count": total_count,
                "columns": columns,
                "sample": result.data[:3],  # First 3 users
            }

            logger.info(f"✅ Users table: {total_count} users, {len(columns)} columns")
            logger.debug(f"   Columns: {', '.join(columns)}")

            return info

        except Exception as e:
            logger.error(f"❌ Error checking users table: {e}")
            return {"count": 0, "columns": [], "sample": [], "error": str(e)}

    @handle_database_error("check notifications schema")
    def check_notifications_schema(self) -> Dict:
        """Check notifications table schema."""
        logger.info("🔍 Checking notifications schema...")

        try:
            result = self.service.sync_client.table("notifications").select("*").limit(1).execute()

            if not result.data:
                logger.warning("⚠️ Notifications table is empty")
                return {"columns": [], "sample": None}

            columns = list(result.data[0].keys())

            info = {"columns": columns, "sample": result.data[0] if result.data else None}

            logger.info(f"✅ Notifications table: {len(columns)} columns")
            logger.debug(f"   Columns: {', '.join(columns)}")

            return info

        except Exception as e:
            logger.error(f"❌ Error checking notifications schema: {e}")
            return {"columns": [], "sample": None, "error": str(e)}

    @handle_database_error("check user notifications")
    def check_user_notifications(self) -> Dict:
        """Check user_notifications table."""
        logger.info("🔍 Checking user_notifications table...")

        try:
            result = (
                self.service.sync_client.table("user_notifications").select("*").limit(5).execute()
            )

            if not result.data:
                logger.warning("⚠️ User notifications table is empty")
                return {"count": 0, "columns": [], "sample": []}

            columns = list(result.data[0].keys())
            count_result = (
                self.service.sync_client.table("user_notifications")
                .select("id", count="exact")
                .execute()
            )
            total_count = count_result.count if hasattr(count_result, 'count') else len(result.data)

            info = {
                "count": total_count,
                "columns": columns,
                "sample": result.data[:3],  # First 3 notifications
            }

            logger.info(
                f"✅ User notifications table: {total_count} notifications, {len(columns)} columns"
            )
            logger.debug(f"   Columns: {', '.join(columns)}")

            return info

        except Exception as e:
            logger.error(f"❌ Error checking user_notifications table: {e}")
            return {"count": 0, "columns": [], "sample": [], "error": str(e)}

    @handle_database_error("check subcategory migration")
    def check_subcategory_migration(self) -> Dict:
        """Check if subcategory migration was applied successfully."""
        logger.info("🔍 Checking subcategory migration...")

        results = {}

        # Check news table
        try:
            news_result = (
                self.service.sync_client.table("news").select("subcategory").limit(1).execute()
            )
            if news_result.data:
                has_subcategory = 'subcategory' in news_result.data[0]
                results['news'] = {"has_subcategory": has_subcategory}
                logger.info(f"✅ News table subcategory: {'✅' if has_subcategory else '❌'}")
            else:
                results['news'] = {"has_subcategory": False, "error": "No data"}
                logger.warning("⚠️ News table has no data")
        except Exception as e:
            results['news'] = {"has_subcategory": False, "error": str(e)}
            logger.error(f"❌ Error checking news subcategory: {e}")

        # Check events table
        try:
            events_result = (
                self.service.sync_client.table("events").select("subcategory").limit(1).execute()
            )
            if events_result.data:
                has_subcategory = 'subcategory' in events_result.data[0]
                results['events'] = {"has_subcategory": has_subcategory}
                logger.info(f"✅ Events table subcategory: {'✅' if has_subcategory else '❌'}")
            else:
                results['events'] = {"has_subcategory": False, "error": "No data"}
                logger.warning("⚠️ Events table has no data")
        except Exception as e:
            results['events'] = {"has_subcategory": False, "error": str(e)}
            logger.error(f"❌ Error checking events subcategory: {e}")

        return results

    @handle_database_error("check database health")
    def check_database_health(self) -> Dict:
        """Perform comprehensive database health check."""
        logger.info("🔍 Performing comprehensive database health check...")

        health_report = {
            "timestamp": None,
            "tables": {},
            "issues": [],
            "summary": {"healthy": True, "total_tables": 0, "healthy_tables": 0},
        }

        # Import datetime here to avoid issues

        health_report["timestamp"] = datetime.now().isoformat()

        # Check all tables
        tables = ["users", "news", "events", "subscriptions", "notifications", "user_notifications"]

        for table in tables:
            try:
                result = self.service.sync_client.table(table).select("*").limit(1).execute()

                table_info = {
                    "exists": True,
                    "has_data": bool(result.data),
                    "columns": list(result.data[0].keys()) if result.data else [],
                    "sample_count": len(result.data) if result.data else 0,
                }

                health_report["tables"][table] = table_info
                health_report["summary"]["healthy_tables"] += 1

                logger.info(f"✅ {table}: healthy")

            except Exception as e:
                table_info = {
                    "exists": False,
                    "error": str(e),
                    "has_data": False,
                    "columns": [],
                    "sample_count": 0,
                }

                health_report["tables"][table] = table_info
                health_report["issues"].append(f"{table}: {str(e)}")

                logger.error(f"❌ {table}: unhealthy - {e}")

        health_report["summary"]["total_tables"] = len(tables)
        health_report["summary"]["healthy"] = len(health_report["issues"]) == 0

        logger.info(
            f"🎯 Database health: {health_report['summary']['healthy_tables']}/{health_report['summary']['total_tables']} tables healthy"
        )

        if health_report["issues"]:
            logger.warning(f"⚠️ Issues found: {len(health_report['issues'])}")
            for issue in health_report["issues"]:
                logger.warning(f"   - {issue}")

        return health_report

    def generate_report(self, checks: List[str]) -> str:
        """Generate a comprehensive report."""
        logger.info("📊 Generating comprehensive database report...")

        report_lines = [
            "# Database Inspection Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        for check in checks:
            if check == "all-columns":
                results = self.check_all_columns()
                report_lines.append("## All Tables Columns")
                for table, columns in results.items():
                    report_lines.append(f"### {table}")
                    report_lines.append(f"Columns: {', '.join(columns)}")
                    report_lines.append("")

            elif check == "users":
                results = self.check_users_table()
                report_lines.append("## Users Table")
                report_lines.append(f"Count: {results.get('count', 0)}")
                report_lines.append(f"Columns: {', '.join(results.get('columns', []))}")
                report_lines.append("")

            elif check == "notifications":
                results = self.check_notifications_schema()
                report_lines.append("## Notifications Schema")
                report_lines.append(f"Columns: {', '.join(results.get('columns', []))}")
                report_lines.append("")

            elif check == "user-notifications":
                results = self.check_user_notifications()
                report_lines.append("## User Notifications")
                report_lines.append(f"Count: {results.get('count', 0)}")
                report_lines.append(f"Columns: {', '.join(results.get('columns', []))}")
                report_lines.append("")

            elif check == "subcategory":
                results = self.check_subcategory_migration()
                report_lines.append("## Subcategory Migration")
                for table, info in results.items():
                    status = "✅" if info.get('has_subcategory') else "❌"
                    report_lines.append(f"{table}: {status}")
                report_lines.append("")

            elif check == "health":
                results = self.check_database_health()
                report_lines.append("## Database Health")
                report_lines.append(
                    f"Overall: {'✅ Healthy' if results['summary']['healthy'] else '❌ Issues Found'}"
                )
                report_lines.append(
                    f"Tables: {results['summary']['healthy_tables']}/{results['summary']['total_tables']}"
                )
                if results['issues']:
                    report_lines.append("Issues:")
                    for issue in results['issues']:
                        report_lines.append(f"  - {issue}")
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """Main function for database inspector."""
    parser = argparse.ArgumentParser(description="PulseAI Database Inspector")
    parser.add_argument(
        "check",
        nargs="+",
        choices=[
            "all-columns",
            "users",
            "notifications",
            "user-notifications",
            "subcategory",
            "health",
            "all",
        ],
        help="Checks to perform",
    )

    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Handle "all" check
    if "all" in args.check:
        args.check = [
            "all-columns",
            "users",
            "notifications",
            "user-notifications",
            "subcategory",
            "health",
        ]

    try:
        inspector = DatabaseInspector()

        # Perform checks
        for check in args.check:
            if check == "all-columns":
                inspector.check_all_columns()
            elif check == "users":
                inspector.check_users_table()
            elif check == "notifications":
                inspector.check_notifications_schema()
            elif check == "user-notifications":
                inspector.check_user_notifications()
            elif check == "subcategory":
                inspector.check_subcategory_migration()
            elif check == "health":
                inspector.check_database_health()

        # Generate report if requested
        if args.output:

            report = inspector.generate_report(args.check)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 Report saved to {args.output}")

        logger.info("🎉 Database inspection completed successfully")

    except Exception as e:
        logger.error(f"💥 Database inspection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
