-- Добавляем колонку published_at_fmt для форматированных дат
ALTER TABLE news ADD COLUMN IF NOT EXISTS published_at_fmt text;

-- Создаем индекс для ускорения поиска по форматированной дате
CREATE INDEX IF NOT EXISTS idx_news_published_at_fmt ON news (published_at_fmt);
