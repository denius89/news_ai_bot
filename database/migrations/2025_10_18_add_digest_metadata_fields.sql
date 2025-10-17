-- Migration: 2025_10_18_add_digest_metadata_fields.sql
-- Description: Add missing metadata fields to digests table
-- Author: PulseAI Team
-- Date: 2025-10-18
-- Issue: column digests.title does not exist (error 42703)

-- Add missing columns to digests table
ALTER TABLE digests 
ADD COLUMN IF NOT EXISTS title TEXT,
ADD COLUMN IF NOT EXISTS content TEXT,
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS style TEXT,
ADD COLUMN IF NOT EXISTS tone TEXT,
ADD COLUMN IF NOT EXISTS length TEXT,
ADD COLUMN IF NOT EXISTS audience TEXT,
ADD COLUMN IF NOT EXISTS confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1),
ADD COLUMN IF NOT EXISTS feedback_score NUMERIC;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_digests_user_created ON digests(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_digests_category ON digests(category);
CREATE INDEX IF NOT EXISTS idx_digests_style ON digests(style);
CREATE INDEX IF NOT EXISTS idx_digests_tone ON digests(tone);

-- Add comments for documentation
COMMENT ON COLUMN digests.title IS 'Digest title';
COMMENT ON COLUMN digests.content IS 'Digest content (AI generated summary)';
COMMENT ON COLUMN digests.category IS 'News category (crypto, sports, markets, tech, world)';
COMMENT ON COLUMN digests.style IS 'AI generation style (analytical, business, meme)';
COMMENT ON COLUMN digests.tone IS 'Content tone (formal, casual, professional)';
COMMENT ON COLUMN digests.length IS 'Content length (short, medium, long)';
COMMENT ON COLUMN digests.audience IS 'Target audience (beginner, advanced, expert)';
COMMENT ON COLUMN digests.confidence IS 'AI confidence score (0.0-1.0)';
COMMENT ON COLUMN digests.feedback_score IS 'User feedback score';

-- Update summary → content for existing records
UPDATE digests 
SET content = summary
WHERE content IS NULL AND summary IS NOT NULL;

-- Set default values for existing records
UPDATE digests 
SET 
    style = COALESCE(style, 'analytical'),
    tone = COALESCE(tone, 'formal'),
    length = COALESCE(length, 'medium'),
    audience = COALESCE(audience, 'general'),
    confidence = COALESCE(confidence, 0.7)
WHERE id IS NOT NULL;

