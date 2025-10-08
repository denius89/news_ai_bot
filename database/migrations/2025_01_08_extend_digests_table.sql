-- Migration: 2025_01_08_extend_digests_table.sql
-- Description: Extend digests table for AI digest storage with metadata
-- Author: PulseAI Team
-- Date: 2025-01-08

-- Add new columns to digests table for AI digest metadata
ALTER TABLE digests 
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS style TEXT,
ADD COLUMN IF NOT EXISTS period TEXT,
ADD COLUMN IF NOT EXISTS limit_count INTEGER,
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_digests_user_created ON digests(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_digests_category ON digests(category);
CREATE INDEX IF NOT EXISTS idx_digests_style ON digests(style);

-- Add comments for documentation
COMMENT ON COLUMN digests.category IS 'News category (crypto, sports, markets, tech, world)';
COMMENT ON COLUMN digests.style IS 'AI generation style (analytical, business, meme)';
COMMENT ON COLUMN digests.period IS 'Time period (today, 7d, 30d)';
COMMENT ON COLUMN digests.limit_count IS 'Number of news items in digest';
COMMENT ON COLUMN digests.metadata IS 'Additional metadata as JSON';

-- Update existing records to have default values
UPDATE digests 
SET 
    category = 'all',
    style = 'analytical',
    period = 'today',
    limit_count = 10,
    metadata = '{}'
WHERE 
    category IS NULL OR 
    style IS NULL OR 
    period IS NULL OR 
    limit_count IS NULL OR 
    metadata IS NULL;
