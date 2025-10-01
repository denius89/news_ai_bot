-- Migration: 2025_10_02_subscriptions_notifications.sql
-- Description: Create tables for user subscriptions and notifications system
-- Author: PulseAI Team
-- Date: 2025-10-02

-- Users table
-- Stores Telegram users with their preferences
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  locale TEXT DEFAULT 'ru',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index for fast Telegram ID lookups
CREATE INDEX IF NOT EXISTS idx_users_tg ON users(telegram_id);

-- Subscriptions table
-- One record per category per user (many-to-many relationship)
CREATE TABLE IF NOT EXISTS subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  category TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, category)
);

-- Index for fast user subscription lookups
CREATE INDEX IF NOT EXISTS idx_subs_user ON subscriptions(user_id);
-- Notifications table
-- Notification preferences per user per type
CREATE TABLE IF NOT EXISTS notifications (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('digest','events','breaking')),
  frequency TEXT NOT NULL DEFAULT 'daily' CHECK (frequency IN ('daily','weekly','instant')),
  preferred_hour SMALLINT DEFAULT 9 CHECK (preferred_hour BETWEEN 0 AND 23),
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, type)
);

-- Index for fast user notification lookups
CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id);

-- Comments for documentation
COMMENT ON TABLE users IS 'Telegram users with their preferences and settings';
COMMENT ON TABLE subscriptions IS 'User subscriptions to news categories (one record per category)';
COMMENT ON TABLE notifications IS 'User notification preferences by type (digest, events, breaking)';

COMMENT ON COLUMN users.telegram_id IS 'Unique Telegram user ID';
COMMENT ON COLUMN users.locale IS 'User preferred language (ru, en, etc.)';
COMMENT ON COLUMN subscriptions.category IS 'News category (crypto, economy, tech, etc.)';
COMMENT ON COLUMN notifications.type IS 'Notification type: digest, events, breaking';
COMMENT ON COLUMN notifications.frequency IS 'How often to send: daily, weekly, instant';
COMMENT ON COLUMN notifications.preferred_hour IS 'Preferred hour for daily notifications (0-23)';
COMMENT ON COLUMN notifications.enabled IS 'Whether this notification type is enabled';
