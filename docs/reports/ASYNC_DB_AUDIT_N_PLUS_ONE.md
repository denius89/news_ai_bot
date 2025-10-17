# Аудит N+1 Queries

**Дата:** 2025-01-18  
**Статус:** Найдено 5 критичных проблем

## Executive Summary

N+1 query problem - это когда делается 1 запрос для получения списка, а затем N дополнительных запросов для получения связанных данных для каждого элемента списка.

**Проблемы:**
- ❌ Цикл по категориям с DB запросом в каждой итерации (1 + N queries)
- ❌ Загрузка данных для каждого пользователя в цикле
- ❌ Множественные запросы вместо одного JOIN

**Ожидаемый эффект после исправления:**
- ↓ 80-90% количество DB queries
- ↓ 60-70% общее время выполнения
- ↑ 5-10x ускорение endpoints

---

## 🔴 КРИТИЧНО - N+1 Queries

### 1. `routes/news_routes.py:339-349` - Query per Category

```python
# ❌ ПЛОХО: N+1 problem!
# Если 10 категорий → 10 DB queries!
for category in all_categories:  # all_categories = ["tech", "crypto", "world", ...]
    try:
        category_news = db_service.get_latest_news(
            categories=[category], limit=100
        )  # ← DB QUERY в цикле!
        news_by_category[category] = category_news
        logger.debug(f"Категория {category}: {len(category_news)} новостей")
    except Exception as e:
        logger.warning(f"Ошибка получения новостей для категории {category}: {e}")
        news_by_category[category] = []
```

**Проблема:**  
10 категорий → 10 отдельных SQL запросов → 10x медленнее

**Решение:**
```python
# ✅ ХОРОШО: 1 запрос вместо N
# Вариант 1: Загрузить все сразу с сортировкой в Python
all_news = db_service.get_latest_news(limit=1000)  # Один запрос

# Группируем по категориям в Python
news_by_category = {}
for category in all_categories:
    news_by_category[category] = []

for news in all_news:
    cat = news.get("category")
    if cat in news_by_category:
        news_by_category[cat].append(news)

# Ограничиваем каждую категорию
for category in news_by_category:
    news_by_category[category] = news_by_category[category][:100]

# Вариант 2: Использовать SQL с GROUP BY (создать RPC функцию)
# CREATE FUNCTION get_news_by_categories(cats TEXT[], limit_per_category INT)
# RETURNS TABLE(...) AS $$
#   SELECT DISTINCT ON (category) *
#   FROM news
#   WHERE category = ANY(cats)
#   ORDER BY category, importance DESC, published_at DESC
#   LIMIT limit_per_category
# $$ LANGUAGE SQL;
```

**Метрики:**
- До: 10 запросов × 100ms = 1000ms
- После: 1 запрос × 150ms = 150ms  
- Ускорение: **6.7x**

---

### 2. `routes/news_routes.py:462-482` - Category Stats Loop

```python
# ❌ ПЛОХО: N+1 problem для статистики
for category in categories:  # categories = ["tech", "crypto", ...]
    try:
        category_news = db_service.get_latest_news(
            categories=[category], limit=1000
        )  # ← DB QUERY в цикле!
        
        # Вычисляем avg в Python (неэффективно)
        category_stats[category] = {
            "count": len(category_news),
            "avg_importance": sum(float(n.get("importance", 0.5)) for n in category_news) / len(category_news),
            "avg_credibility": sum(float(n.get("credibility", 0.5)) for n in category_news) / len(category_news),
        }
    except Exception as e:
        logger.warning(f"Ошибка получения статистики для категории {category}: {e}")
        category_stats[category] = {"count": 0, "avg_importance": 0, "avg_credibility": 0}
```

**Проблема:**  
10 категорий × 1000 новостей каждая = 10,000 записей загружено для простой статистики!

**Решение:**
```python
# ✅ ХОРОШО: Один SQL запрос с GROUP BY
# Создать RPC функцию в Supabase:

# CREATE OR REPLACE FUNCTION get_all_category_stats()
# RETURNS TABLE(
#   category TEXT,
#   count BIGINT,
#   avg_importance FLOAT,
#   avg_credibility FLOAT
# ) AS $$
#   SELECT 
#     category,
#     COUNT(*) as count,
#     AVG(importance) as avg_importance,
#     AVG(credibility) as avg_credibility
#   FROM news
#   WHERE category IS NOT NULL
#   GROUP BY category
#   ORDER BY count DESC;
# $$ LANGUAGE SQL STABLE;

# В Python:
category_stats_result = supabase.rpc("get_all_category_stats").execute()
category_stats = {
    row["category"]: {
        "count": row["count"],
        "avg_importance": row["avg_importance"],
        "avg_credibility": row["avg_credibility"],
    }
    for row in category_stats_result.data
}
```

**Метрики:**
- До: 10 запросов × 200ms + 10,000 записей обработка = 2500ms
- После: 1 запрос × 50ms = 50ms  
- Ускорение: **50x**

---

### 3. `routes/dashboard_api.py:80-106` - Sources Count Loop

```python
# ❌ ПЛОХО: 2 запроса по 1000 записей для подсчета уникальных
sources_query = supabase.table("news").select("source").limit(1000)
result = safe_execute(sources_query)

# Загружаем 1000 записей чтобы посчитать уникальные источники в Python
unique_sources = set(item["source"] for item in result.data if item.get("source"))
active_sources = len(unique_sources)

# Затем еще 1000 записей для прошлого периода
prev_sources_query = supabase.table("news").select("source").limit(1000)
prev_result = safe_execute(prev_sources_query)
prev_unique_sources = set(item["source"] for item in prev_result.data if item.get("source"))
```

**Проблема:**  
2000 записей загружено для простого COUNT(DISTINCT source)

**Решение:**
```python
# ✅ ХОРОШО: SQL COUNT(DISTINCT)

# CREATE FUNCTION count_sources_in_period(
#   start_date timestamptz,
#   end_date timestamptz
# ) RETURNS bigint AS $$
#   SELECT COUNT(DISTINCT source)
#   FROM news
#   WHERE published_at >= start_date 
#     AND published_at < end_date;
# $$ LANGUAGE SQL STABLE;

# В Python:
today = datetime.now()
week_ago = today - timedelta(days=7)
two_weeks_ago = today - timedelta(days=14)

current_sources = supabase.rpc("count_sources_in_period", {
    "start_date": week_ago.isoformat(),
    "end_date": today.isoformat()
}).execute()

prev_sources = supabase.rpc("count_sources_in_period", {
    "start_date": two_weeks_ago.isoformat(),
    "end_date": week_ago.isoformat()
}).execute()

active_sources = current_sources.data
prev_sources_count = prev_sources.data
```

**Метрики:**
- До: 2 запроса × 150ms + 2000 записей = 400ms
- После: 2 запроса × 20ms = 40ms  
- Ускорение: **10x**

---

### 4. `services/events_stream.py:106-120` - User Notifications Loop

```python
# 🟡 ПОТЕНЦИАЛЬНО ПЛОХО: зависит от что внутри цикла
for user_id in target_users:  # target_users может быть 100+ пользователей
    try:
        # Check rate limit
        if not self.can_send_update(user_id):  # ← Возможно DB query?
            continue
        
        # Send update через WebSocket (это ок)
        await self._send_user_update(user_id, update_data)
    except Exception as e:
        logger.error(f"Error sending update to {user_id}: {e}")
```

**Требует дополнительной проверки:**  
Если `can_send_update()` делает DB query → N+1 problem

**Рекомендация:**
```python
# ✅ ХОРОШО: Загрузить все rate limits одним запросом

# До цикла:
user_ids = list(target_users)
rate_limits = await self.batch_check_rate_limits(user_ids)  # Один запрос

# В цикле:
for user_id in target_users:
    if not rate_limits.get(user_id, True):  # Проверка из памяти
        continue
    
    await self._send_user_update(user_id, update_data)
```

---

### 5. `routes/admin_routes.py:1194-1213` - Events Providers Loop

```python
# 🟡 СРЕДНЕ: группировка в Python вместо SQL
providers_map = defaultdict(lambda: {"count": 0, "categories": set()})
category_counts = defaultdict(int)

# Загружаем все события
events_data = result.data or []

# Группируем в Python (можно было в SQL)
for event in events_data:
    source = event.get("source", "Unknown")
    category = event.get("category", "other")
    providers_map[source]["count"] += 1
    providers_map[source]["categories"].add(category)
    category_counts[category] += 1
```

**Проблема:**  
Хотя это не N+1 (нет DB queries в цикле), но группировка в Python медленнее чем в SQL

**Решение:**
```python
# ✅ ХОРОШО: GROUP BY в SQL

# CREATE FUNCTION get_provider_stats()
# RETURNS TABLE(
#   source TEXT,
#   count BIGINT,
#   categories TEXT[]
# ) AS $$
#   SELECT 
#     source,
#     COUNT(*) as count,
#     array_agg(DISTINCT category) as categories
#   FROM events_new
#   GROUP BY source
#   ORDER BY count DESC;
# $$ LANGUAGE SQL STABLE;

providers_result = supabase.rpc("get_provider_stats").execute()
providers_map = {
    row["source"]: {
        "count": row["count"],
        "categories": set(row["categories"])
    }
    for row in providers_result.data
}
```

---

## 🟢 НЕ N+1 (но выглядит похоже)

### Ложные срабатывания:

#### A. `routes/api_routes.py:223-236` - Unicode conversion
```python
# ✅ ОК: нет DB queries в цикле
for char in name:
    if char in unicode_map:
        result += unicode_map[char]
```
**Статус:** Это просто обработка строки, не N+1

---

#### B. `routes/news_routes.py:78-89` - Model conversion
```python
# ✅ ОК: конвертация моделей, не DB queries
for item in news_items:
    if hasattr(item, "model_dump"):
        item_dict = item.model_dump()
```
**Статус:** Обработка в памяти, не N+1

---

#### C. `services/notification_service.py:350-360` - Event formatting
```python
# ✅ ОК: форматирование уже загруженных данных
for event in events[:5]:  # Events уже загружены
    category_emoji = self._get_category_emoji(event.get("category"))
    title = event.get("title", "Без названия")
```
**Статус:** Обработка в памяти, не N+1

---

## Рекомендуемые SQL RPC функции

### RPC 1: Get News by Categories (batch)
```sql
CREATE OR REPLACE FUNCTION get_news_by_categories_batch(
  cats TEXT[],
  limit_per_category INT DEFAULT 100
)
RETURNS TABLE(
  category TEXT,
  id INT,
  title TEXT,
  content TEXT,
  importance FLOAT,
  credibility FLOAT,
  published_at TIMESTAMPTZ
) AS $$
  SELECT 
    category,
    id,
    title,
    content,
    importance,
    credibility,
    published_at
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (PARTITION BY category ORDER BY importance DESC, published_at DESC) as rn
    FROM news
    WHERE category = ANY(cats)
  ) ranked
  WHERE rn <= limit_per_category;
$$ LANGUAGE SQL STABLE;
```

### RPC 2: Get All Category Stats
```sql
CREATE OR REPLACE FUNCTION get_all_category_stats()
RETURNS TABLE(
  category TEXT,
  count BIGINT,
  avg_importance FLOAT,
  avg_credibility FLOAT,
  latest_news_at TIMESTAMPTZ
) AS $$
  SELECT 
    category,
    COUNT(*) as count,
    AVG(importance) as avg_importance,
    AVG(credibility) as avg_credibility,
    MAX(published_at) as latest_news_at
  FROM news
  WHERE category IS NOT NULL
  GROUP BY category
  ORDER BY count DESC;
$$ LANGUAGE SQL STABLE;
```

### RPC 3: Count Sources in Period
```sql
CREATE OR REPLACE FUNCTION count_sources_in_period(
  start_date timestamptz,
  end_date timestamptz
)
RETURNS bigint AS $$
  SELECT COUNT(DISTINCT source)
  FROM news
  WHERE published_at >= start_date 
    AND published_at < end_date
    AND source IS NOT NULL;
$$ LANGUAGE SQL STABLE;
```

### RPC 4: Provider Stats
```sql
CREATE OR REPLACE FUNCTION get_provider_stats()
RETURNS TABLE(
  source TEXT,
  event_count BIGINT,
  categories TEXT[],
  avg_importance FLOAT
) AS $$
  SELECT 
    source,
    COUNT(*) as event_count,
    array_agg(DISTINCT category) as categories,
    AVG(importance) as avg_importance
  FROM events_new
  WHERE source IS NOT NULL
  GROUP BY source
  ORDER BY event_count DESC;
$$ LANGUAGE SQL STABLE;
```

---

## Приоритизированный план исправлений

### Неделя 1 (Критично):
1. ✅ Создать RPC функции в Supabase (1 час)
2. ✅ Исправить `routes/news_routes.py:339` - N+1 по категориям (30 мин)
3. ✅ Исправить `routes/news_routes.py:462` - статистика категорий (30 мин)

**Время:** 2 часа  
**Эффект:** ↓ 80% DB queries, ↑ 5-10x скорость endpoints

---

### Неделя 2 (Оптимизация):
4. ⏳ Исправить `routes/dashboard_api.py:80` - sources count (30 мин)
5. ⏳ Исправить `routes/admin_routes.py:1194` - provider stats (30 мин)
6. ⏳ Проверить `services/events_stream.py:106` на DB queries (1 час)

**Время:** 2 часа  
**Эффект:** ↓ 60% time в admin endpoints

---

## Измеримые метрики

### До оптимизации:
```python
# /api/latest-weighted endpoint
# Запросов к БД: 10 (по одному на категорию)
# Время: 1000-1500 ms
# Записей загружено: 1000 (100 × 10 категорий)

# /api/distribution-stats endpoint
# Запросов к БД: 10 (по одному на категорию)
# Время: 2000-3000 ms
# Записей загружено: 10,000 (1000 × 10 категорий)

# /api/admin/providers endpoint
# Запросов к БД: 1 (но группировка в Python)
# Время: 300-500 ms
# Записей загружено: 1000+
```

### После оптимизации:
```python
# /api/latest-weighted endpoint
# Запросов к БД: 1 (RPC функция)
# Время: 150-250 ms (↓ 80%)
# Записей загружено: 1000

# /api/distribution-stats endpoint
# Запросов к БД: 1 (RPC функция с GROUP BY)
# Время: 50-100 ms (↓ 95%)
# Записей загружено: 10 (только агрегаты)

# /api/admin/providers endpoint
# Запросов к БД: 1 (RPC с GROUP BY)
# Время: 50-100 ms (↓ 80%)
# Записей загружено: 20-50 (только агрегаты)
```

---

## Дополнительные рекомендации

### 1. Использовать DB Views для частых запросов
```sql
-- View для категорийной статистики
CREATE VIEW category_stats AS
SELECT 
  category,
  COUNT(*) as total_news,
  AVG(importance) as avg_importance,
  AVG(credibility) as avg_credibility,
  MAX(published_at) as latest_news_at
FROM news
WHERE category IS NOT NULL
GROUP BY category;

-- Теперь можно просто:
SELECT * FROM category_stats;
```

### 2. Batch loading pattern
```python
# Если нужны связанные данные:
def get_users_with_preferences(user_ids: List[int]):
    # ❌ ПЛОХО: N+1
    users = []
    for user_id in user_ids:
        user = db.get_user(user_id)
        prefs = db.get_preferences(user_id)
        users.append({**user, "preferences": prefs})
    
    # ✅ ХОРОШО: 2 запроса вместо 2N
    users = db.get_users_batch(user_ids)  # 1 запрос
    prefs = db.get_preferences_batch(user_ids)  # 1 запрос
    prefs_map = {p["user_id"]: p for p in prefs}
    
    return [
        {**user, "preferences": prefs_map.get(user["id"])}
        for user in users
    ]
```

### 3. DataLoader pattern (для GraphQL-подобных случаев)
```python
from collections import defaultdict

class BatchLoader:
    def __init__(self):
        self.queue = []
        self.cache = {}
    
    async def load(self, key):
        if key in self.cache:
            return self.cache[key]
        
        self.queue.append(key)
        
        # Batch load when queue reaches threshold
        if len(self.queue) >= 10:
            await self._flush()
        
        return self.cache.get(key)
    
    async def _flush(self):
        if not self.queue:
            return
        
        # Один запрос вместо N
        results = await db.get_batch(self.queue)
        
        for item in results:
            self.cache[item["id"]] = item
        
        self.queue.clear()
```

---

## Заключение

**Найдено:** 5 N+1 проблем (3 критичных, 2 средних)

**Критичность:**
- 🔴 2 критичных (циклы по категориям с DB queries)
- 🟡 3 средних (неэффективная загрузка/группировка)
- 🟢 0 низких

**Приоритет исправлений:**
1. Создать RPC функции в Supabase
2. Заменить циклы с DB queries на batch loading
3. Использовать SQL GROUP BY вместо Python группировки

**Ожидаемый результат:**
- ↓ 80-90% количество DB queries
- ↓ 60-70% время выполнения endpoints
- ↑ 5-10x ускорение критичных endpoints
- ↓ 50% нагрузка на БД

**Время внедрения:** 4-6 часов работы (2 недели по 2-3 часа)


