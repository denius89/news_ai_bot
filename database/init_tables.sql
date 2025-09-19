-- Новости
CREATE TABLE IF NOT EXISTS news (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text,
  source text NOT NULL,
  published_at timestamp with time zone NOT NULL,
  credibility numeric CHECK (credibility >= 0 AND credibility <= 1),
  importance numeric CHECK (importance >= 0 AND importance <= 1),
  created_at timestamp with time zone DEFAULT now()
);

-- Индексы для новостей
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);

-- Пользователи
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id bigint UNIQUE NOT NULL,
  created_at timestamp with time zone DEFAULT now()
);

-- Дайджесты
CREATE TABLE IF NOT EXISTS digests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  summary text,
  created_at timestamp with time zone DEFAULT now()
);