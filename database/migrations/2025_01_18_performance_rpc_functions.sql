-- Migration: Performance RPC Functions
-- Date: 2025-01-18
-- Purpose: Добавить RPC функции для оптимизации N+1 queries и агрегаций
-- Автор: AI Assistant (Async & DB Audit)

-- ==================================================================
-- RPC 1: Get News by Categories (Batch)
-- ==================================================================
-- Заменяет N запросов (по одному на категорию) одним эффективным запросом
-- Использование: routes/news_routes.py:339 (цикл по категориям)

CREATE OR REPLACE FUNCTION get_news_by_categories_batch(
  cats TEXT[],
  limit_per_category INT DEFAULT 100
)
RETURNS TABLE(
  category TEXT,
  id UUID,
  uid TEXT,
  title TEXT,
  content TEXT,
  link TEXT,
  published_at TIMESTAMPTZ,
  source TEXT,
  importance NUMERIC,
  credibility NUMERIC
) AS $$
  SELECT 
    category,
    id,
    uid,
    title,
    content,
    link,
    published_at,
    source,
    importance,
    credibility
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY category 
        ORDER BY importance DESC, published_at DESC
      ) as rn
    FROM news
    WHERE category = ANY(cats)
      AND category IS NOT NULL
  ) ranked
  WHERE rn <= limit_per_category
  ORDER BY category, importance DESC, published_at DESC;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_news_by_categories_batch IS 
'Batch загрузка новостей по категориям. Заменяет N запросов одним. 
Пример: SELECT * FROM get_news_by_categories_batch(ARRAY[''tech'', ''crypto''], 50)';


-- ==================================================================
-- RPC 2: Get All Category Stats
-- ==================================================================
-- Заменяет загрузку тысяч записей для вычисления статистики в Python
-- Использование: routes/news_routes.py:462 (статистика по категориям)

CREATE OR REPLACE FUNCTION get_all_category_stats()
RETURNS TABLE(
  category TEXT,
  count BIGINT,
  avg_importance NUMERIC,
  avg_credibility NUMERIC,
  latest_news_at TIMESTAMPTZ
) AS $$
  SELECT 
    category,
    COUNT(*) as count,
    ROUND(AVG(importance)::NUMERIC, 3) as avg_importance,
    ROUND(AVG(credibility)::NUMERIC, 3) as avg_credibility,
    MAX(published_at) as latest_news_at
  FROM news
  WHERE category IS NOT NULL
  GROUP BY category
  ORDER BY count DESC;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_all_category_stats IS 
'Агрегированная статистика по всем категориям. Эффективнее загрузки 10K+ записей.
Пример: SELECT * FROM get_all_category_stats()';


-- ==================================================================
-- RPC 3: Count Sources in Period
-- ==================================================================
-- Заменяет загрузку 1000 записей для подсчета уникальных источников
-- Использование: routes/dashboard_api.py:80 (подсчет активных источников)

CREATE OR REPLACE FUNCTION count_sources_in_period(
  start_date TIMESTAMPTZ DEFAULT NULL,
  end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS BIGINT AS $$
  SELECT COUNT(DISTINCT source)
  FROM news
  WHERE source IS NOT NULL
    AND (start_date IS NULL OR published_at >= start_date)
    AND (end_date IS NULL OR published_at < end_date);
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION count_sources_in_period IS 
'Подсчет уникальных источников за период. SQL COUNT(DISTINCT) вместо Python.
Пример: SELECT count_sources_in_period(NOW() - INTERVAL ''7 days'', NOW())';


-- ==================================================================
-- RPC 4: Count Unique Categories
-- ==================================================================
-- Заменяет загрузку всей таблицы для подсчета категорий
-- Использование: routes/dashboard_api.py:131

CREATE OR REPLACE FUNCTION count_unique_categories()
RETURNS BIGINT AS $$
  SELECT COUNT(DISTINCT category)
  FROM news
  WHERE category IS NOT NULL;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION count_unique_categories IS 
'Подсчет уникальных категорий. Эффективнее загрузки всех записей.
Пример: SELECT count_unique_categories()';


-- ==================================================================
-- RPC 5: Get Provider Stats (Events)
-- ==================================================================
-- Заменяет загрузку всех событий для группировки в Python
-- Использование: routes/admin_routes.py:1194

CREATE OR REPLACE FUNCTION get_provider_stats()
RETURNS TABLE(
  source TEXT,
  event_count BIGINT,
  categories TEXT[],
  avg_importance NUMERIC,
  latest_event_at TIMESTAMPTZ
) AS $$
  SELECT 
    source,
    COUNT(*) as event_count,
    array_agg(DISTINCT category) as categories,
    ROUND(AVG(importance)::NUMERIC, 3) as avg_importance,
    MAX(starts_at) as latest_event_at
  FROM events_new
  WHERE source IS NOT NULL
  GROUP BY source
  ORDER BY event_count DESC;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_provider_stats IS 
'Статистика провайдеров событий с GROUP BY в SQL.
Пример: SELECT * FROM get_provider_stats()';


-- ==================================================================
-- RPC 6: Get News Stats by Period
-- ==================================================================
-- Комплексная статистика новостей за период
-- Использование: dashboard analytics

CREATE OR REPLACE FUNCTION get_news_stats_period(
  start_date TIMESTAMPTZ,
  end_date TIMESTAMPTZ
)
RETURNS TABLE(
  total_count BIGINT,
  categories_count BIGINT,
  sources_count BIGINT,
  avg_importance NUMERIC,
  avg_credibility NUMERIC
) AS $$
  SELECT
    COUNT(*) as total_count,
    COUNT(DISTINCT category) as categories_count,
    COUNT(DISTINCT source) as sources_count,
    ROUND(AVG(importance)::NUMERIC, 3) as avg_importance,
    ROUND(AVG(credibility)::NUMERIC, 3) as avg_credibility
  FROM news
  WHERE published_at >= start_date 
    AND published_at < end_date;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_news_stats_period IS 
'Комплексная статистика новостей за период. Одним запросом вместо нескольких.
Пример: SELECT * FROM get_news_stats_period(NOW() - INTERVAL ''1 day'', NOW())';


-- ==================================================================
-- Проверка установки функций
-- ==================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ RPC функции успешно созданы:';
  RAISE NOTICE '  - get_news_by_categories_batch()';
  RAISE NOTICE '  - get_all_category_stats()';
  RAISE NOTICE '  - count_sources_in_period()';
  RAISE NOTICE '  - count_unique_categories()';
  RAISE NOTICE '  - get_provider_stats()';
  RAISE NOTICE '  - get_news_stats_period()';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Ожидаемый эффект:';
  RAISE NOTICE '  - ↓ 80-90%% количество DB queries';
  RAISE NOTICE '  - ↓ 90-95%% объем загружаемых данных';
  RAISE NOTICE '  - ↑ 5-10x скорость endpoints';
  RAISE NOTICE '';
  RAISE NOTICE '🔗 Следующий шаг: применить в routes/news_routes.py';
END $$;

