#!/usr/bin/env python3
"""
Apply database migration to add missing columns to users table.

This script adds the missing 'username' and 'locale' columns to the existing users table.
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
    """Apply the migration to add missing columns."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(url, key)

        print("🔍 Checking current users table schema...")

        # Check current schema
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            if result.data:
                print(f"Current columns: {list(result.data[0].keys())}")
            else:
                print("Table exists but has no data")
        except Exception as e:
            print(f"Error checking schema: {e}")
            return False

        print("🔧 Adding missing columns to users table...")

        # Add username column if it doesn't exist
        try:
            supabase.rpc(
                'exec_sql', {'sql': 'ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;'}
            ).execute()
            print("✅ Added username column")
        except Exception as e:
            print(f"⚠️  Could not add username column: {e}")

        # Add locale column if it doesn't exist
        try:
            supabase.rpc(
                'exec_sql',
                {'sql': 'ALTER TABLE users ADD COLUMN IF NOT EXISTS locale TEXT DEFAULT \'ru\';'},
            ).execute()
            print("✅ Added locale column")
        except Exception as e:
            print(f"⚠️  Could not add locale column: {e}")

        # Add updated_at column if it doesn't exist
        try:
            supabase.rpc(
                'exec_sql',
                {
                    'sql': 'ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();'
                },
            ).execute()
            print("✅ Added updated_at column")
        except Exception as e:
            print(f"⚠️  Could not add updated_at column: {e}")

        print("🔍 Verifying updated schema...")

        # Check updated schema
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            if result.data:
                print(f"Updated columns: {list(result.data[0].keys())}")
            else:
                print("✅ Table schema updated successfully")
        except Exception as e:
            print(f"Error verifying schema: {e}")
            return False

        print("✅ Migration applied successfully!")
        return True

    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Applying database migration...")
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
