-- Create user_notifications table with correct schema
-- Execute this in Supabase SQL Editor

-- Drop table if exists
DROP TABLE IF EXISTS user_notifications CASCADE;

-- Create table with UUID reference to users table
CREATE TABLE user_notifications (
  id           BIGSERIAL PRIMARY KEY,
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  text         TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  read         BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create index for performance
CREATE INDEX idx_user_notifications_user_read_created
  ON user_notifications (user_id, read, created_at DESC);

-- Insert test data
INSERT INTO user_notifications (user_id, title, text, read)
SELECT 
  (SELECT id FROM users LIMIT 1),
  'Новый дайджест готов!',
  'Ваш утренний дайджест с последними новостями готов к прочтению.',
  false
UNION ALL
SELECT 
  (SELECT id FROM users LIMIT 1),
  'Важное событие',
  'Сегодня в 15:00 ожидается важное экономическое событие в США.',
  true
UNION ALL
SELECT 
  (SELECT id FROM users LIMIT 1),
  'Bitcoin обновил максимум',
  'Криптовалюта Bitcoin достигла нового исторического максимума.',
  false;
