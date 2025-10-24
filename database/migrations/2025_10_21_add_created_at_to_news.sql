-- =============================================================================
-- Migration: Add created_at column to news table
-- Date: 2025-10-21
-- Description: Add created_at column with default value for tracking when news
--              items were added to the database (vs published_at for when news
--              was originally published)
-- =============================================================================

-- Add created_at column if it doesn't exist
ALTER TABLE news ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();

-- Update existing records to have created_at = published_at for now
-- (since we don't know the real insertion time)
UPDATE news
SET created_at = published_at
WHERE created_at IS NULL;

-- Set NOT NULL constraint after populating data
ALTER TABLE news ALTER COLUMN created_at SET NOT NULL;

-- Add index for performance on created_at queries
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news (created_at DESC);

-- Update the default to current timestamp for future inserts
ALTER TABLE news ALTER COLUMN created_at SET DEFAULT now();
