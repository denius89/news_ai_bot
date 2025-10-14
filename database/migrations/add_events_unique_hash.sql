-- Migration: Add unique_hash field to events_new table for deduplication
-- Date: 2025-10-13
-- Description: Adds unique_hash column and index for event deduplication

-- Add unique_hash column if it doesn't exist
ALTER TABLE events_new ADD COLUMN IF NOT EXISTS unique_hash TEXT;

-- Create unique index on unique_hash for deduplication
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_new_unique_hash ON events_new(unique_hash);

-- Add metadata column as JSONB if it doesn't exist
ALTER TABLE events_new ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Add group_name column if it doesn't exist
ALTER TABLE events_new ADD COLUMN IF NOT EXISTS group_name TEXT;

-- Add GIN index for faster JSON metadata queries
CREATE INDEX IF NOT EXISTS idx_events_new_metadata_gin ON events_new USING GIN (metadata);

-- Add index on group_name for grouping queries
CREATE INDEX IF NOT EXISTS idx_events_new_group_name ON events_new(group_name);

-- Comment on columns
COMMENT ON COLUMN events_new.unique_hash IS 'SHA256 hash of title|starts_at|source for deduplication';
COMMENT ON COLUMN events_new.metadata IS 'Provider-specific metadata (teams, coins, votes, etc.) stored as JSON';
COMMENT ON COLUMN events_new.group_name IS 'Group name for smart grouping (league name, coin name, etc.)';

