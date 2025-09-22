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