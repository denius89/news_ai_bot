-- Migration: 2025_01_08_soft_delete_digests.sql
-- Description: Add soft delete and archive functionality to digests table
-- Author: PulseAI Team
-- Date: 2025-01-08

-- Add soft delete and archive columns to digests table
ALTER TABLE digests 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_digests_deleted ON digests(deleted_at);
CREATE INDEX IF NOT EXISTS idx_digests_archived ON digests(archived);
CREATE INDEX IF NOT EXISTS idx_digests_active ON digests(user_id, created_at DESC) WHERE deleted_at IS NULL AND archived = FALSE;

-- Add comments for documentation
COMMENT ON COLUMN digests.deleted_at IS 'Timestamp when digest was soft deleted (NULL = active)';
COMMENT ON COLUMN digests.archived IS 'Whether digest is archived (TRUE = archived, FALSE = active)';

-- Update existing records to have default values
UPDATE digests 
SET 
    deleted_at = NULL,
    archived = FALSE
WHERE 
    deleted_at IS NULL OR 
    archived IS NULL;
