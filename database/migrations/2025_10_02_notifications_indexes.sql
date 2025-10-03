-- Migration: Add indexes for fast notifications queries
-- Date: 2025-10-02
-- Purpose: Optimize notifications and subscription queries for WebApp Dashboard

-- Index for fast unread notifications lookup by user
CREATE INDEX IF NOT EXISTS idx_user_notifications_unread 
ON user_notifications (user_id, read, created_at DESC) 
WHERE read = false;

-- Index for notification settings lookup by user
CREATE INDEX IF NOT EXISTS idx_notification_settings_user 
ON notification_settings (user_id, category);

-- Index for subscriptions lookup by user
CREATE INDEX IF NOT EXISTS idx_subscriptions_user 
ON subscriptions (user_id, category);

-- Index for user lookup by telegram_id
CREATE INDEX IF NOT EXISTS idx_users_telegram_id 
ON users (telegram_id);

-- Index for general notifications ordering (read/unread mixed)
CREATE INDEX IF NOT EXISTS idx_user_notifications_general 
ON user_notifications (user_id, created_at DESC);

-- Comments for future reference
COMMENT ON INDEX idx_user_notifications_unread IS 
'Optimizes queries for unread notifications count and list for WebApp badge';

COMMENT ON INDEX idx_notification_settings_user IS 
'Optimizes notification settings lookup for WebApp settings tab';

COMMENT ON INDEX idx_subscriptions_user IS 
'Optimizes subscription lookup for WebApp subscriptions tab';

COMMENT ON INDEX idx_users_telegram_id IS 
'Optimizes user lookup when converting Telegram ID to internal UUID';
