-- Migration: Notifications System
-- Date: 2025-10-02
-- Description: Create tables for notifications and notification settings

-- Create user_notifications table (renamed to avoid conflict with existing notifications table)
CREATE TABLE IF NOT EXISTS user_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create notification_settings table
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    enabled BOOLEAN DEFAULT true,
    via_telegram BOOLEAN DEFAULT true,
    via_webapp BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, category)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_timestamp ON user_notifications(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_notifications_read ON user_notifications(read);
CREATE INDEX IF NOT EXISTS idx_notification_settings_user_id ON notification_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_settings_category ON notification_settings(category);

-- Add some sample notifications for demo user
-- This will be handled by the application, but keeping as reference
-- INSERT INTO notifications (user_id, title, message, category, timestamp, read) VALUES
-- ('demo-user-uuid', 'Bitcoin Breaks $50K', 'Bitcoin has reached a new milestone crossing $50,000 mark', 'crypto', now() - interval '2 hours', false),
-- ('demo-user-uuid', 'Fed Rate Decision', 'Federal Reserve announces interest rate decision', 'economy', now() - interval '1 day', true);
