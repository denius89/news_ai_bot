-- =============================================================================
-- database/init_tables.sql  (idempotent, совместимо с Supabase)
-- =============================================================================

-- В Supabase gen_random_uuid() доступен по умолчанию. На обычном Postgres:
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================
-- Таблица новостей
-- =========================
CREATE TABLE IF NOT EXISTS news (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  uid          text UNIQUE,                                -- уникальный ключ для upsert (url|title hash)
  title        text NOT NULL,
  content      text,
  link         text,                                       -- исходная ссылка
  source       text NOT NULL,
  category     text,
  subcategory  text,
  published_at timestamptz NOT NULL,
  credibility  numeric CHECK (credibility >= 0 AND credibility <= 1),
  importance   numeric CHECK (importance  >= 0 AND importance  <= 1),
  created_at   timestamptz DEFAULT now()
);

-- На случай, если таблица news уже существовала без нужных колонок:
ALTER TABLE news ADD COLUMN IF NOT EXISTS uid        text;
ALTER TABLE news ADD COLUMN IF NOT EXISTS link       text;
ALTER TABLE news ADD COLUMN IF NOT EXISTS category   text;
ALTER TABLE news ADD COLUMN IF NOT EXISTS subcategory text;
ALTER TABLE news ADD COLUMN IF NOT EXISTS credibility numeric;
ALTER TABLE news ADD COLUMN IF NOT EXISTS importance  numeric;

-- Уникальный индекс для upsert по uid
CREATE UNIQUE INDEX IF NOT EXISTS uniq_news_uid ON news (uid);

-- Индексы для ускорения выборок
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_source       ON news (source);
CREATE INDEX IF NOT EXISTS idx_news_link         ON news (link);

-- =========================
-- Пользователи
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id bigint UNIQUE NOT NULL,
  created_at  timestamptz DEFAULT now()
);

-- =========================
-- Дайджесты
-- =========================
CREATE TABLE IF NOT EXISTS digests (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid REFERENCES users(id) ON DELETE CASCADE,
  summary    text,
  created_at timestamptz DEFAULT now()
);

-- =========================
-- Таблица событий
-- =========================
-- Поддерживаем текущую логику: в коде upsert идёт по "event_id",
-- поэтому добавляем его как уникальное поле. Сохраняем также surrogate PK "id".
CREATE TABLE IF NOT EXISTS events (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id     text UNIQUE,                                -- уникальный ключ для upsert (hash title|country|time)
  event_time   timestamptz NOT NULL,                       -- UTC
  country      text,                                       -- например: US, EU, CN
  country_code text,                                       -- нормализованный ISO-код (2–3 символа)
  currency     text,                                       -- USD, EUR, BTC и т.д.
  category     text,                                       -- категория события
  subcategory  text,                                       -- подкатегория события
  title        text NOT NULL,
  importance   int  CHECK (importance BETWEEN 1 AND 3),    -- 1..3 звезды
  priority     text,                                       -- low / medium / high (оригинальная градация парсера)
  fact         text,
  forecast     text,
  previous     text,
  source       text,
  created_at   timestamptz DEFAULT now()
);

-- На случай, если таблица events уже была создана раньше — дублирующие ADD IF NOT EXISTS
ALTER TABLE events ADD COLUMN IF NOT EXISTS event_id     text;
ALTER TABLE events ADD COLUMN IF NOT EXISTS country_code text;
ALTER TABLE events ADD COLUMN IF NOT EXISTS category     text;
ALTER TABLE events ADD COLUMN IF NOT EXISTS subcategory  text;
ALTER TABLE events ADD COLUMN IF NOT EXISTS priority     text;
ALTER TABLE events ADD COLUMN IF NOT EXISTS importance   int;

-- Уникальный индекс, чтобы upsert по event_id работал
CREATE UNIQUE INDEX IF NOT EXISTS uniq_events_event_id ON events (event_id);

-- Контроль формата country_code (2–3 символа, допускаем EU и т.п.)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'events_country_code_check'
  ) THEN
    ALTER TABLE events
    ADD CONSTRAINT events_country_code_check
      CHECK (country_code IS NULL OR char_length(country_code) BETWEEN 2 AND 3);
  END IF;
END $$;

-- Полезные индексы
CREATE INDEX IF NOT EXISTS idx_events_time_desc   ON events (event_time DESC);
CREATE INDEX IF NOT EXISTS idx_events_country     ON events (country);
CREATE INDEX IF NOT EXISTS idx_events_country_code ON events (country_code);
CREATE INDEX IF NOT EXISTS idx_events_importance  ON events (importance);
CREATE INDEX IF NOT EXISTS idx_events_priority    ON events (priority);

-- Доп. индекс для дедупликации/поиска схожих событий (не unique, т.к. есть event_id)
CREATE INDEX IF NOT EXISTS idx_events_time_title_country
  ON events (event_time, title, COALESCE(country, ''));

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