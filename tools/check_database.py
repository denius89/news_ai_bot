#!/usr/bin/env python3
"""
Check database schema and test user creation.

This script verifies that the database has the correct schema
and can create users with all required fields.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_database():
    """Check database schema and functionality."""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        print("🔍 Checking database schema...")
        
        # Check users table schema
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                print(f"✅ Users table columns: {columns}")
                
                required_columns = ['id', 'telegram_id', 'username', 'locale', 'created_at', 'updated_at']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"❌ Missing columns: {missing_columns}")
                    print("\n📋 To fix this, run the migration in Supabase Dashboard:")
                    print("   1. Open SQL Editor")
                    print("   2. Run the SQL from database/migrations/2025_10_02_add_missing_columns.sql")
                    return False
                else:
                    print("✅ All required columns present")
            else:
                print("ℹ️  Users table exists but has no data")
        except Exception as e:
            print(f"❌ Error accessing users table: {e}")
            return False
        
        # Test user creation
        print("\n🧪 Testing user creation...")
        try:
            from database.db_models import upsert_user_by_telegram
            
            # Test user creation
            user_id = upsert_user_by_telegram(
                telegram_id=999999999,
                username="test_user",
                locale="en"
            )
            
            if user_id:
                print(f"✅ User created successfully with ID: {user_id}")
                
                # Clean up test user
                supabase.table('users').delete().eq('telegram_id', 999999999).execute()
                print("🧹 Test user cleaned up")
                return True
            else:
                print("❌ Failed to create user")
                return False
                
        except Exception as e:
            print(f"❌ Error testing user creation: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Checking database setup...")
    print("=" * 50)
    
    success = check_database()
    
    print("=" * 50)
    if success:
        print("✅ Database is ready!")
        sys.exit(0)
    else:
        print("❌ Database setup needs attention!")
        print("\n📖 See database/MIGRATION_INSTRUCTIONS.md for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
