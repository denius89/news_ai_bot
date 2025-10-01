-- Migration: Add updated_at column to users table
-- Description: Add updated_at column to existing users table
-- Date: 2025-10-02

-- Add updated_at column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Update existing rows to set updated_at
UPDATE users SET updated_at = now() WHERE updated_at IS NULL;
