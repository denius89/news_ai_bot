-- Migration: Add missing columns to users table
-- Description: Add username, locale, and updated_at columns to existing users table
-- Date: 2025-10-02

-- Add username column
ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;

-- Add locale column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS locale TEXT DEFAULT 'ru';

-- Add updated_at column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Update existing rows to set updated_at
UPDATE users SET updated_at = now() WHERE updated_at IS NULL;
