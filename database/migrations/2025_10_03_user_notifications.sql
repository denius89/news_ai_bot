-- Migration: Create user_notifications table
-- Date: 2025-10-03
-- Description: Add user notifications table for storing user-specific notifications

-- =========================
-- Уведомления пользователей
-- =========================
CREATE TABLE IF NOT EXISTS user_notifications (
  id           BIGSERIAL PRIMARY KEY,
  user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  text         TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  read         BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_user_notifications_user_read_created
  ON user_notifications (user_id, read, created_at DESC);

-- Добавляем тестовые данные
INSERT INTO user_notifications (user_id, title, text, read)
SELECT 
  (SELECT id FROM users WHERE telegram_id = '123456789' LIMIT 1),
  'Новый дайджест готов!',
  'Ваш утренний дайджест с последними новостями готов к прочтению.',
  false
WHERE EXISTS (SELECT 1 FROM users WHERE telegram_id = '123456789')
UNION ALL
SELECT 
  (SELECT id FROM users WHERE telegram_id = '123456789' LIMIT 1),
  'Важное событие',
  'Сегодня в 15:00 ожидается важное экономическое событие в США.',
  true
WHERE EXISTS (SELECT 1 FROM users WHERE telegram_id = '123456789');
