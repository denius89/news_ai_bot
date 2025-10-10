-- Migration: 2025_10_09_digest_metrics.sql
-- Description: Add metrics fields to digests table and create digest_analytics table
-- Author: PulseAI Team
-- Date: 2025-10-09

-- Add metrics fields to digests table
ALTER TABLE digests ADD COLUMN IF NOT EXISTS confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1);
ALTER TABLE digests ADD COLUMN IF NOT EXISTS generation_time_sec NUMERIC;
ALTER TABLE digests ADD COLUMN IF NOT EXISTS feedback_score NUMERIC CHECK (feedback_score >= 0 AND feedback_score <= 1);
ALTER TABLE digests ADD COLUMN IF NOT EXISTS feedback_count INTEGER DEFAULT 0;
ALTER TABLE digests ADD COLUMN IF NOT EXISTS skipped_reason TEXT;
ALTER TABLE digests ADD COLUMN IF NOT EXISTS meta JSONB; -- for style_profile, tone, length, audience
ALTER TABLE digests ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE digests ADD COLUMN IF NOT EXISTS style TEXT;

-- Create digest_analytics table for aggregated metrics
CREATE TABLE IF NOT EXISTS digest_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  generated_count INTEGER DEFAULT 0,
  avg_confidence NUMERIC,
  avg_generation_time_sec NUMERIC,
  skipped_low_quality INTEGER DEFAULT 0,
  feedback_count INTEGER DEFAULT 0,
  avg_feedback_score NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(date)
);

-- Index for fast date lookups
CREATE INDEX IF NOT EXISTS idx_digest_analytics_date ON digest_analytics(date DESC);
CREATE INDEX IF NOT EXISTS idx_digest_analytics_created_at ON digest_analytics(created_at DESC);

-- Index for digests metrics queries
CREATE INDEX IF NOT EXISTS idx_digests_created_at ON digests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_digests_confidence ON digests(confidence);
CREATE INDEX IF NOT EXISTS idx_digests_feedback_score ON digests(feedback_score);

-- Comments for documentation
COMMENT ON TABLE digest_analytics IS 'Daily aggregated metrics for digest generation quality';
COMMENT ON COLUMN digests.confidence IS 'AI confidence score (0.0-1.0)';
COMMENT ON COLUMN digests.generation_time_sec IS 'Time taken to generate digest in seconds';
COMMENT ON COLUMN digests.feedback_score IS 'Average user feedback score (0.0-1.0)';
COMMENT ON COLUMN digests.feedback_count IS 'Number of feedback submissions';
COMMENT ON COLUMN digests.skipped_reason IS 'Reason why digest was skipped (low quality)';
COMMENT ON COLUMN digests.meta IS 'Additional metadata (style, tone, length, audience)';
