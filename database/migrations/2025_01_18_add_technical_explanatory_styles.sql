-- Migration: 2025_01_18_add_technical_explanatory_styles.sql
-- Description: Update style constraint to include technical and explanatory styles
-- Author: PulseAI Team
-- Date: 2025-01-18

-- Drop existing constraint if it exists
ALTER TABLE digests DROP CONSTRAINT IF EXISTS check_style_valid;

-- Add updated constraint with all supported styles
ALTER TABLE digests ADD CONSTRAINT check_style_valid 
CHECK (style IN (
    -- Original v1 styles
    'analytical', 
    'business', 
    'meme',
    
    -- v2 styles added later
    'newsroom', 
    'magazine', 
    'casual',
    
    -- New specialized styles
    'explanatory', 
    'technical'
));

-- Add comment for documentation
COMMENT ON COLUMN digests.style IS 'AI generation style (analytical, business, meme, newsroom, magazine, casual, explanatory, technical)';
