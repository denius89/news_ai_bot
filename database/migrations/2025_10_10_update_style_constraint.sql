-- Update style constraint to include new v2 styles
ALTER TABLE digests DROP CONSTRAINT IF EXISTS check_style_valid;

ALTER TABLE digests ADD CONSTRAINT check_style_valid 
CHECK (style IN ('analytical', 'business', 'meme', 'newsroom', 'magazine', 'casual'));

-- Update existing digests with old styles to new ones if needed
-- (This is optional, we can keep old styles for backward compatibility)
