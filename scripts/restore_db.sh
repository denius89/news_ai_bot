#!/bin/bash
#
# Restore PulseAI Database from Backup
#
# This script restores the database from a compressed backup file.
#
# Usage:
#   ./scripts/restore_db.sh backups/pulseai_20251027_123456.sql.gz
#
# Environment Variables (from .env):
#   - SUPABASE_URL
#   - SUPABASE_KEY
#   - SUPABASE_DB_NAME (default: pulseai)
#
# WARNING: This will replace ALL existing data in the database!
# Make sure you have a recent backup before running this.
#
# Author: PulseAI Team
# Date: 2025-10-27

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Backup file not specified${NC}"
    echo ""
    echo "Usage: ./scripts/restore_db.sh backups/pulseai_20251027_123456.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
DB_NAME="${SUPABASE_DB_NAME:-pulseai}"

echo -e "${RED}⚠️  WARNING: This will REPLACE all data in the database!${NC}"
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Database: $DB_NAME"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 0
fi

# Check if Supabase credentials are available
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env${NC}"
    exit 1
fi

# Extract host and port from SUPABASE_URL
if [[ $SUPABASE_URL =~ ^https://([^.]+)\.supabase\.co$ ]]; then
    DB_HOST="${BASH_REMATCH[1]}.supabase.co"
    DB_PORT="5432"
else
    echo -e "${RED}❌ Error: Invalid SUPABASE_URL format${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Restoring database from backup...${NC}"

# Restore database using psql
gunzip < "$BACKUP_FILE" | PGPASSWORD="$SUPABASE_KEY" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U postgres \
    -d "$DB_NAME"

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database restored successfully!${NC}"
else
    echo -e "${RED}❌ Restore failed${NC}"
    exit 1
fi
