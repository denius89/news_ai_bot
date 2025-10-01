-- Migration: Convert published_at from text to timestamptz
-- Date: 2025-10-01
-- Description: Convert published_at column in news table from text/varchar to timestamptz with timezone support

-- Step 1: Add new column with timestamptz type
ALTER TABLE news ADD COLUMN published_at_new timestamptz;

-- Step 2: Convert existing data from text to timestamptz
-- Handle various date formats that might exist in the database
UPDATE news 
SET published_at_new = CASE 
    -- ISO format: 2025-09-30T15:30:00Z or 2025-09-30T15:30:00+00:00
    WHEN published_at ~ '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' THEN 
        published_at::timestamptz
    -- Date only: 2025-09-30
    WHEN published_at ~ '^\d{4}-\d{2}-\d{2}$' THEN 
        (published_at || 'T00:00:00Z')::timestamptz
    -- Date with time: 2025-09-30 15:30:00
    WHEN published_at ~ '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' THEN 
        (published_at || '+00:00')::timestamptz
    -- Unix timestamp (if stored as text)
    WHEN published_at ~ '^\d+$' AND length(published_at) = 10 THEN 
        to_timestamp(published_at::bigint)
    -- Unix timestamp with milliseconds
    WHEN published_at ~ '^\d+$' AND length(published_at) = 13 THEN 
        to_timestamp(published_at::bigint / 1000)
    -- Default fallback to current timestamp
    ELSE NOW()
END
WHERE published_at IS NOT NULL AND published_at != '';

-- Step 3: Drop old column and rename new one
ALTER TABLE news DROP COLUMN published_at;
ALTER TABLE news RENAME COLUMN published_at_new TO published_at;

-- Step 4: Add index for efficient querying by date
CREATE INDEX idx_news_published_at_desc ON news (published_at DESC);

-- Step 5: Add comment for documentation
COMMENT ON COLUMN news.published_at IS 'Publication timestamp with timezone support (timestamptz)';

-- Step 6: Verify the migration
-- Check that all rows have valid timestamps
SELECT 
    COUNT(*) as total_rows,
    COUNT(published_at) as rows_with_timestamp,
    MIN(published_at) as earliest_date,
    MAX(published_at) as latest_date
FROM news;
