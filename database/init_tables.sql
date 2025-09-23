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

-- Таблица событий (экономика, крипта, политика и т.д.)
create table if not exists events (
    id uuid primary key default gen_random_uuid(),
    event_time timestamptz not null,              -- время события (UTC)
    country text,                                 -- страна (ISO-код, напр. US, EU, CN)
    currency text,                                -- валюта (ISO-код, напр. USD, EUR, BTC)
    title text not null,                          -- название события
    importance int check (importance between 1 and 3), -- важность (1-3 звезды)
    fact text,                                    -- фактическое значение
    forecast text,                                -- прогноз
    previous text,                                -- предыдущее значение
    source text,                                  -- источник (например, TradingEconomics)
    created_at timestamptz default now()          -- дата добавления
);

-- Примеры событий для отладки
insert into events (event_time, country, currency, title, importance, fact, forecast, previous, source)
values
    ('2025-09-25 12:30:00+00', 'US', 'USD', 'GDP Growth Rate QoQ Final', 3, '3.2%', '3.3%', '3.1%', 'TradingEconomics'),
    ('2025-09-26 08:00:00+00', 'EU', 'EUR', 'ECB Interest Rate Decision', 3, null, '4.25%', '4.25%', 'TradingEconomics'),
    ('2025-09-27 10:00:00+00', 'CN', 'CNY', 'Manufacturing PMI', 2, '50.1', '49.8', '49.5', 'TradingEconomics'),
    ('2025-09-28 14:00:00+00', 'US', 'BTC', 'Ethereum Hard Fork', 2, null, null, null, 'Cointelegraph');

-- database/init_tables.sql (добавь в конец файла)

-- 1) Таблица событий (если ещё не создана)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_time TIMESTAMPTZ NOT NULL,         -- UTC
    country TEXT,                             -- код страны (пример: us, gb, eu)
    currency TEXT,                            -- USD, EUR и т.п.
    title TEXT NOT NULL,
    importance INT,                           -- 1=Low, 2=Medium, 3=High
    fact TEXT,
    forecast TEXT,
    previous TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2) Уникальный ключ для дедупликации
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
          AND indexname = 'uniq_events_time_title_country'
    ) THEN
        CREATE UNIQUE INDEX uniq_events_time_title_country
        ON events (event_time, title, COALESCE(country, ''));
    END IF;
END $$;

-- Добавляем колонку для ISO-кода страны (для флагов)
ALTER TABLE events
ADD COLUMN IF NOT EXISTS country_code TEXT;

-- Можно сразу ограничить длину кода (2 символа для ISO или 2–3, если EU и т.п.)
ALTER TABLE events
ADD CONSTRAINT events_country_code_check CHECK (
    country_code IS NULL OR char_length(country_code) BETWEEN 2 AND 3
);