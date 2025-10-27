#!/bin/bash
#
# Backup PulseAI Database
#
# This script creates a backup of the Supabase PostgreSQL database.
# It compresses the backup with gzip and maintains the last 30 days of backups.
#
# Usage:
#   ./scripts/backup_db.sh                    # Use .env variables
#   ./scripts/backup_db.sh /custom/path       # Custom backup directory
#
# Environment Variables (from .env):
#   - SUPABASE_URL
#   - SUPABASE_KEY
#   - SUPABASE_DB_NAME (default: pulseai)
#
# Author: PulseAI Team
# Date: 2025-10-27

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
BACKUP_DIR="${1:-$(pwd)/backups}"
DB_NAME="${SUPABASE_DB_NAME:-pulseai}"
KEEP_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pulseai_$DATE.sql.gz"

echo -e "${GREEN}🗄️  PulseAI Database Backup${NC}"
echo "===================================="
echo "Backup directory: $BACKUP_DIR"
echo "Database name: $DB_NAME"
echo ""

# Check if Supabase credentials are available
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env${NC}"
    echo ""
    echo "Please add to your .env file:"
    echo "  SUPABASE_URL=https://your-project.supabase.co"
    echo "  SUPABASE_KEY=your-anon-key"
    exit 1
fi

# Extract host and port from SUPABASE_URL
# Format: https://[project-ref].supabase.co
if [[ $SUPABASE_URL =~ ^https://([^.]+)\.supabase\.co$ ]]; then
    DB_HOST="${BASH_REMATCH[1]}.supabase.co"
    DB_PORT="5432"
else
    echo -e "${RED}❌ Error: Invalid SUPABASE_URL format${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Creating backup...${NC}"

# Create backup using pg_dump
# Note: Supabase requires SSL connection
PGPASSWORD="$SUPABASE_KEY" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U postgres \
    -d "$DB_NAME" \
    --no-acl \
    --no-owner \
    --format=plain \
    | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created successfully${NC}"
    echo "File: $BACKUP_FILE"
    echo "Size: $BACKUP_SIZE"
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi

# Clean up old backups (keep last 30 days)
echo ""
echo -e "${YELLOW}🧹 Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "pulseai_*.sql.gz" -mtime +$KEEP_DAYS -delete

OLD_COUNT=$(find "$BACKUP_DIR" -name "pulseai_*.sql.gz" -mtime +$KEEP_DAYS | wc -l | tr -d ' ')
if [ "$OLD_COUNT" -gt 0 ]; then
    echo "Deleted $OLD_COUNT old backup(s)"
fi

# List all backups
echo ""
echo -e "${GREEN}📊 Available backups:${NC}"
ls -lh "$BACKUP_DIR"/pulseai_*.sql.gz 2>/dev/null || echo "No backups found"

echo ""
echo -e "${GREEN}✅ Backup completed successfully!${NC}"
