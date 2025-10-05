-- Migration: Add subcategory field to news and events tables
-- Date: 2025-01-04
-- Description: Adds subcategory field to support hierarchical categorization

-- Add subcategory field to news table
ALTER TABLE news ADD COLUMN IF NOT EXISTS subcategory TEXT;

-- Add subcategory field to events table  
ALTER TABLE events ADD COLUMN IF NOT EXISTS subcategory TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_news_subcategory ON news (subcategory);
CREATE INDEX IF NOT EXISTS idx_events_subcategory ON events (subcategory);

-- Add composite indexes for category + subcategory queries
CREATE INDEX IF NOT EXISTS idx_news_category_subcategory ON news (category, subcategory);
CREATE INDEX IF NOT EXISTS idx_events_category_subcategory ON events (category, subcategory);

-- Update existing records with default subcategory based on category
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'crypto';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'economy';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'world';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'technology';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'politics';

-- Update events table similarly
UPDATE events SET subcategory = 'general' WHERE subcategory IS NULL;

-- Add comments
COMMENT ON COLUMN news.subcategory IS 'Subcategory for hierarchical categorization (e.g., bitcoin, ethereum for crypto)';
COMMENT ON COLUMN events.subcategory IS 'Subcategory for hierarchical categorization (e.g., stocks, bonds for markets)';
