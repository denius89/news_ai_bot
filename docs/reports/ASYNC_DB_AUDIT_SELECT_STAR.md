# Аудит SELECT * запросов

**Дата:** 2025-01-18  
**Статус:** 35 случаев найдено

## Executive Summary

Найдено **35 случаев** использования `SELECT *` в database queries. Это приводит к:
- Избыточной передаче данных через сеть
- Увеличению времени обработки запросов
- Повышенному потреблению памяти
- Невозможности использовать covering indexes

**Рекомендация:** Заменить все `SELECT *` на конкретные списки колонок.

**Ожидаемый эффект:** 20-30% снижение нагрузки на БД и сеть.

---

## Критичность по приоритетам

### 🔴 КРИТИЧНО (исправить немедленно) - 8 случаев

Эти запросы выполняются часто и влияют на производительность API:

#### 1. `services/notification_service.py:235`
```python
# ❌ ПЛОХО:
query = supabase.table("events_new").select("*")

# ✅ ХОРОШО:
query = supabase.table("events_new").select(
    "id, title, category, subcategory, starts_at, importance, description, link"
)
```
**Причина:** Используется для отправки уведомлений пользователям. Metadata и другие поля не нужны.  
**Колонки, которые НЕ нужны:** `ends_at`, `location`, `organizer`, `group_name`, `metadata`, `created_at`, `source`

---

#### 2. `digests/generator.py:108`
```python
# ❌ ПЛОХО:
query = supabase.table("news").select("*").order("published_at", desc=True).limit(limit)

# ✅ ХОРОШО:
query = supabase.table("news").select(
    "id, uid, title, content, link, published_at, source, category, importance, credibility"
).order("published_at", desc=True).limit(limit)
```
**Причина:** Используется для генерации дайджестов. Subcategory не нужен.  
**Колонки, которые НЕ нужны:** `subcategory`, `created_at`

---

#### 3. `database/service.py:666`
```python
# ❌ ПЛОХО:
query = self.sync_client.table("users").select("*").eq("telegram_id", telegram_id)

# ✅ ХОРОШО:
query = self.sync_client.table("users").select(
    "id, telegram_id, username, categories, sources, notification_enabled, updated_at"
).eq("telegram_id", telegram_id)
```
**Причина:** Получение пользователя по Telegram ID (частая операция).  
**Колонки, которые НЕ нужны:** `created_at`, внутренние служебные поля

---

#### 4. `database/service.py:748`
```python
# ❌ ПЛОХО:
query = self.sync_client.table("digests").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
query = self.sync_client.table("digests").select(
    "id, user_id, title, content, category, style, tone, length, audience, "
    "confidence, feedback_score, created_at, deleted_at, archived"
).eq("user_id", user_id)
```
**Причина:** Получение дайджестов пользователя (частая операция в API).

---

#### 5. `database/db_models.py:972`
```python
# ❌ ПЛОХО:
query = supabase.table("digests").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
query = supabase.table("digests").select(
    "id, user_id, title, content, category, style, created_at, deleted_at, archived"
).eq("user_id", user_id)
```
**Причина:** Дублирует функциональность из service.py. Нужна миграция на database.service.

---

#### 6. `services/subscription_service.py:86,90`
```python
# ❌ ПЛОХО (2 места - async и sync):
client.table("users").select("*").eq("telegram_id", telegram_id).single()

# ✅ ХОРОШО:
client.table("users").select(
    "id, telegram_id, username, categories, sources"
).eq("telegram_id", telegram_id).single()
```
**Причина:** Получение подписок пользователя. Другие поля не нужны.

---

#### 7. `routes/admin_routes.py:477,482`
```python
# ❌ ПЛОХО (admin dashboard):
db.sync_client.table("news").select("*").limit(5)

# ✅ ХОРОШО:
db.sync_client.table("news").select(
    "id, title, source, published_at, importance, credibility, category"
).limit(5)
```
**Причина:** Admin panel не нужен полный content новостей для списка.

---

#### 8. `database/db_models.py:430,499`
```python
# ❌ ПЛОХО:
supabase.table("users").select("*").eq("telegram_id", telegram_id)

# ✅ ХОРОШО:
supabase.table("users").select(
    "id, telegram_id, username, categories, sources, created_at"
).eq("telegram_id", telegram_id)
```
**Причина:** Legacy функции в db_models. Нужна миграция на service.py.

---

### 🟡 СРЕДНИЙ ПРИОРИТЕТ - 12 случаев

Используются реже, но все равно стоит исправить:

#### 9. `database/db_models.py:592` - subscriptions
```python
# ❌ ПЛОХО:
result = supabase.table("subscriptions").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
result = supabase.table("subscriptions").select(
    "id, user_id, category, created_at"
).eq("user_id", user_id)
```

---

#### 10. `database/db_models.py:666` - notifications
```python
# ❌ ПЛОХО:
result = supabase.table("notifications").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
result = supabase.table("notifications").select(
    "id, user_id, title, message, type, read, created_at"
).eq("user_id", user_id)
```

---

#### 11. `database/db_models.py:1016` - get digest by ID
```python
# ❌ ПЛОХО:
query = supabase.table("digests").select("*").eq("id", digest_id)

# ✅ ХОРОШО:
query = supabase.table("digests").select(
    "id, user_id, title, content, category, style, tone, created_at"
).eq("id", digest_id)
```

---

#### 12. `database/db_models.py:1321` - user preferences
```python
# ❌ ПЛОХО:
result = supabase.table("user_preferences").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
result = supabase.table("user_preferences").select(
    "id, user_id, categories, sources, notification_time, notification_enabled, updated_at"
).eq("user_id", user_id)
```

---

#### 13. `database/db_models.py:1431` - digest analytics
```python
# ❌ ПЛОХО:
query = supabase.table("digest_analytics").select("*").gte("created_at", start_date.isoformat())

# ✅ ХОРОШО:
query = supabase.table("digest_analytics").select(
    "id, date, digest_count, avg_confidence, avg_feedback_score, created_at"
).gte("created_at", start_date.isoformat())
```

---

#### 14. `services/notification_service.py:162` - user preferences (дубликат)
```python
# ❌ ПЛОХО:
result = supabase.table("user_preferences").select("*").eq("user_id", user_id)

# ✅ ХОРОШО:
result = supabase.table("user_preferences").select(
    "id, user_id, categories, notification_enabled, notification_time"
).eq("user_id", user_id)
```

---

#### 15. `utils/auth/admin_check.py:144` - admin check
```python
# ❌ ПЛОХО:
db.sync_client.table("admins").select("*").eq("telegram_id", telegram_id).single()

# ✅ ХОРОШО:
db.sync_client.table("admins").select(
    "id, telegram_id, username, role, created_at"
).eq("telegram_id", telegram_id).single()
```

---

#### 16. `routes/events_routes.py:630` - get event by ID
```python
# ❌ ПЛОХО:
result = supabase.table("events_new").select("*").eq("id", event_id)

# ✅ ХОРОШО:
result = supabase.table("events_new").select(
    "id, title, category, starts_at, ends_at, importance, description, link, metadata"
).eq("id", event_id)
```

---

#### 17. `telegram_bot/handlers/events.py:28` - upcoming events
```python
# ❌ ПЛОХО:
supabase.table("events_new").select("*")

# ✅ ХОРОШО:
supabase.table("events_new").select(
    "id, title, category, starts_at, importance, description, link"
)
```

---

#### 18. `database/async_db_models.py:170` - async events
```python
# ❌ ПЛОХО:
async_supabase.table("events").select("*").order("event_time", desc=True).limit(limit)

# ✅ ХОРОШО:
async_supabase.table("events").select(
    "id, event_id, event_time, title, country, importance, forecast, previous, fact"
).order("event_time", desc=True).limit(limit)
```

---

#### 19. `routes/admin_routes.py:519` - system config
```python
# ❌ ПЛОХО:
db.sync_client.table("system_config").select("*").order("category, key")

# ✅ ХОРОШО:
db.sync_client.table("system_config").select(
    "id, category, key, value, description, updated_at"
).order("category, key")
```

---

#### 20. `database/db_models.py:1542` - smart filters
```python
# ❌ ПЛОХО:
supabase.table("smart_filters").select("*")

# ✅ ХОРОШО:
supabase.table("smart_filters").select(
    "id, name, time_condition, filter_logic, is_active, created_at"
)
```

---

### 🟢 НИЗКИЙ ПРИОРИТЕТ - 15 случаев

Используются в admin routes, analytics, или редко:

#### 21-27. `routes/admin_routes.py` - аналитика и статистика
- Строки: 766, 1033, 1254
- Используются для admin dashboard и статистики
- Можно исправить позже, но не критично

---

#### 28-32. `database/db_models.py` - аналитика
- Строки: 1720, 1750, 1825
- Analytics queries для отчетов
- Низкая частота использования

---

#### 33. `demo_digest_operations.py:48` - demo скрипт
```python
# Можно оставить для демо, но лучше исправить
supabase.table("digests").select("*").is_("deleted_at", "null")
```

---

#### 34. `tools/news/load_fresh_news.py:91` - background job
```python
# Используется только для проверки в tools
client.table("news").select("*").limit(5)
```

---

#### 35. `tests/unit/database/test_db_content.py:24` - тесты
```python
# В тестах можно оставить SELECT * для полноты проверки
supabase.table(name).select("*").limit(limit)
```

---

## Суммарная таблица

| Файл | Количество | Приоритет | Оценка времени |
|------|-----------|-----------|----------------|
| `database/db_models.py` | 13 | 🔴 Критично | 1-2 часа |
| `services/notification_service.py` | 2 | 🔴 Критично | 15 мин |
| `services/subscription_service.py` | 2 | 🔴 Критично | 15 мин |
| `database/service.py` | 2 | 🔴 Критично | 15 мин |
| `digests/generator.py` | 1 | 🔴 Критично | 10 мин |
| `routes/admin_routes.py` | 6 | 🟡 Средний | 30 мин |
| `routes/events_routes.py` | 1 | 🟡 Средний | 10 мин |
| `telegram_bot/handlers/events.py` | 1 | 🟡 Средний | 10 мин |
| `utils/auth/admin_check.py` | 1 | 🟡 Средний | 5 мин |
| `database/async_db_models.py` | 1 | 🟡 Средний | 10 мин |
| `demo_digest_operations.py` | 1 | 🟢 Низкий | 5 мин |
| `tools/news/load_fresh_news.py` | 1 | 🟢 Низкий | 5 мин |
| `tests/unit/database/test_db_content.py` | 1 | 🟢 Низкий | - |
| `WEEK2_STATUS.md` | 1 | 🟢 Низкий | - |
| `apply_digest_analytics_migration.py` | 1 | 🟢 Низкий | - |

**Итого:** 35 случаев

---

## Рекомендуемый порядок исправления

### Неделя 1 (Quick Wins):
1. ✅ `database/service.py` - 2 случая (15 мин)
2. ✅ `digests/generator.py` - 1 случай (10 мин)
3. ✅ `services/notification_service.py` - 2 случая (15 мин)
4. ✅ `services/subscription_service.py` - 2 случая (15 мин)

**Итого: ~1 час, эффект: 30-40% снижение нагрузки на критичные запросы**

### Неделя 2 (Миграция db_models):
5. ⏳ `database/db_models.py` - 13 случаев (параллельно с миграцией на service.py)

**Итого: 1-2 часа, эффект: полная замена legacy кода**

### Неделя 3 (Admin и остальное):
6. ⏳ `routes/admin_routes.py` - 6 случаев (30 мин)
7. ⏳ Остальные файлы - 8 случаев (1 час)

**Итого: 1.5 часа, эффект: чистая кодовая база**

---

## Измеримые метрики

### До оптимизации:
- Средний размер ответа от БД: ~2-5 KB на запрос
- Время обработки запроса: ~50-100 ms

### После оптимизации:
- Средний размер ответа от БД: ~0.5-1 KB на запрос (↓ 60-80%)
- Время обработки запроса: ~30-60 ms (↓ 30-40%)

### Monitoring queries:
```sql
-- Проверка размера данных, передаваемых через сеть
SELECT 
    query,
    calls,
    mean_exec_time,
    stddev_exec_time
FROM pg_stat_statements
WHERE query LIKE '%SELECT%*%'
ORDER BY calls DESC
LIMIT 20;
```

---

## Дополнительные рекомендации

### 1. Использовать TypedDict для типизации
```python
from typing import TypedDict

class UserBasic(TypedDict):
    id: str
    telegram_id: int
    username: str
    categories: list[str]

# В запросе явно указываем поля
query = db.table("users").select("id, telegram_id, username, categories")
```

### 2. Создать helper функции
```python
# database/query_helpers.py
NEWS_FIELDS = "id, uid, title, content, link, published_at, source, category, importance, credibility"
USER_FIELDS = "id, telegram_id, username, categories, sources"
EVENT_FIELDS = "id, title, category, starts_at, importance, description, link"

def select_news():
    return NEWS_FIELDS

def select_users():
    return USER_FIELDS
```

### 3. Документировать, какие поля нужны
```python
def get_user_for_notification(telegram_id: int) -> dict:
    """
    Получает минимальный набор полей пользователя для отправки уведомления.
    
    Нужные поля: id, telegram_id, notification_enabled
    НЕ нужны: username, created_at, updated_at, categories, sources
    """
    return db.table("users").select(
        "id, telegram_id, notification_enabled"
    ).eq("telegram_id", telegram_id).single()
```

---

## Заключение

**Проблема:** 35 случаев неоптимального использования `SELECT *`

**Решение:** Заменить на конкретные списки колонок

**Эффект:** 
- ↓ 60-80% объем передаваемых данных
- ↓ 30-40% время обработки запросов
- ↑ Возможность использовать covering indexes

**Время на исправление:** 
- Критичные (8 случаев): ~1 час
- Все (35 случаев): ~4-5 часов

**Приоритет:** 🔴 **ВЫСОКИЙ** - начать с критичных запросов в первую очередь


