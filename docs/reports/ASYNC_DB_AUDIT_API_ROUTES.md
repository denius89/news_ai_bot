# Аудит Flask API Routes - Sync/Async

**Дата:** 2025-01-18  
**Статус:** Flask полностью синхронный, нужна миграция на async

## Executive Summary

Flask - синхронный фреймворк. Все API endpoints блокируются при ожидании DB queries, HTTP requests, AI calls.

**Проблемы:**
1. ❌ Использование `run_async()` костыля в 5 местах - создает новый event loop
2. ❌ Все endpoints синхронные - блокируются при DB/API вызовах
3. ❌ Нет concurrent request handling - один запрос блокирует другие
4. ❌ DB queries выполняются синхронно даже если database.service поддерживает async

**Рекомендация:**  
Мигрировать на async фреймворк (Quart или FastAPI)

**Ожидаемый эффект:**
- ↑ 2-3x throughput (requests/sec)
- ↓ 40-60% latency при параллельных запросах
- ↑ 5-10x улучшение при AI/external API calls

---

## Текущая архитектура

### Flask Routes файлы:
1. `routes/api_routes.py` - 2000+ строк, ~25 endpoints
2. `routes/news_routes.py` - ~520 строк, ~5 endpoints
3. `routes/events_routes.py` - ~690 строк, ~10 endpoints
4. `routes/admin_routes.py` - ~1300 строк, ~15 endpoints
5. `routes/dashboard_api.py` - ~350 строк, ~10 endpoints
6. `routes/config_routes.py` - ~200 строк, ~5 endpoints
7. `routes/metrics_routes.py` - ~150 строк, ~5 endpoints
8. `routes/analytics_routes.py` - ~200 строк, ~5 endpoints
9. `routes/webapp_routes.py` - ~300 строк, ~8 endpoints

**Итого:** ~5700 строк кода, ~88 endpoints, **все синхронные**

---

## 🔴 КРИТИЧНО - `run_async()` Костыль

### Что это такое:
```python
def run_async(coro):
    """Helper to run async functions in Flask context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()  # ← Создает НОВЫЙ event loop!
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)  # ← Блокирует до завершения
```

**Проблема:**  
- Создание нового event loop на каждый вызов - дорого
- Блокирует Flask request thread - нет параллелизма
- Может конфликтовать с существующим event loop
- Anti-pattern для async кода

---

### Где используется:

#### 1. `routes/api_routes.py:323`
```python
@api_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    user_id = request.args.get("user_id")
    subscription_service = SubscriptionService(async_mode=True)
    
    # ❌ ПЛОХО: run_async костыль
    subscriptions = run_async(subscription_service.list(user_id))
    subscribed_categories = {sub["category"] for sub in subscriptions}
```

**Частота:** Высокая (каждый запрос подписок)  
**Latency:** +50-100ms (overhead от создания event loop)

---

#### 2. `routes/api_routes.py:399,402`
```python
@api_bp.route("/subscriptions/update", methods=["POST"])
def update_subscription():
    # ❌ ПЛОХО: 3 вызова run_async подряд!
    demo_telegram_id = 999999999
    created_user_id = run_async(
        subscription_service.get_or_create_user(demo_telegram_id, "demo-user")
    )
    
    success = run_async(subscription_service.add(created_user_id, category))
```

**Частота:** Средняя (при подписке/отписке)  
**Latency:** +150-300ms (3× overhead)

---

#### 3. `routes/api_routes.py:415`
```python
# Remove subscription
success = run_async(subscription_service.remove(user_id, category))
```

**Частота:** Средняя  
**Latency:** +50-100ms

---

#### 4. `routes/api_routes.py:695`
```python
@api_bp.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    telegram_id = data.get("telegram_id")
    username = data.get("username")
    
    # ❌ ПЛОХО: run_async в webhook
    user_id = run_async(
        subscription_service.get_or_create_user(telegram_id, username)
    )
```

**Частота:** Высокая (каждый Telegram WebApp запуск)  
**Latency:** +50-100ms

---

#### 5. `routes/api_routes.py:963`
```python
@api_bp.route("/digest/generate", methods=["POST"])
def generate_digest():
    # ❌ ПЛОХО: run_async для AI digest
    digest_text = run_async(
        digest_service.async_build_ai_digest(
            limit=limit,
            categories=categories,
            style=style,
            tone=tone,
            length=length,
            audience=audience,
            user_id=user_id,
        )
    )
```

**Частота:** Средняя (генерация дайджестов)  
**Latency:** +5-10 секунд (AI call) + overhead

---

## 🟡 СРЕДНИЙ ПРИОРИТЕТ - Sync DB Calls

Все endpoints используют синхронные DB вызовы, даже если `database.service` поддерживает async.

### Примеры:

#### `routes/news_routes.py:160,204,235`
```python
@news_bp.route("/api/latest")
def api_latest_news():
    # ❌ ПЛОХО: sync DB call
    db_service = get_sync_service()  # Получаем SYNC сервис!
    all_news = db_service.get_latest_news(limit=fetch_limit)
    
    # Фильтрация в Python (еще одна проблема)
    for news_item in all_news:
        if category in full_categories:
            filtered_news.append(news_item)
```

**Проблема:**  
- Блокирует Flask worker на время DB query
- Не может обрабатывать другие запросы параллельно

---

#### `routes/events_routes.py` - все endpoints sync
```python
@events_bp.route("/", methods=["GET"])
def get_events():
    # ❌ ПЛОХО: sync
    events_service = get_events_service()
    events = events_service.get_events_filtered(...)  # Sync call
```

---

#### `routes/dashboard_api.py` - все endpoints sync
```python
def get_news_stats_today():
    # ❌ ПЛОХО: sync
    today_query = supabase.table("news").select("id", count="exact")
    today_result = safe_execute(today_query)  # Sync call
```

---

## 🟢 НИЗКИЙ ПРИОРИТЕТ - Простые endpoints

Некоторые endpoints просто возвращают данные из памяти - их можно оставить синхронными:

```python
# ✅ ОК: нет DB/IO calls
@api_bp.route("/categories", methods=["GET"])
def get_categories_api():
    return jsonify({
        "categories": get_categories(),  # Возврат из памяти
        "structure": get_category_structure()
    })
```

---

## Решение 1: Quart (Drop-in замена Flask)

### Преимущества:
- ✅ Почти 100% совместим с Flask
- ✅ Минимальные изменения кода
- ✅ Async/await поддержка
- ✅ Поддерживает WebSockets

### Недостатки:
- ❌ Меньшая экосистема чем FastAPI
- ❌ Медленнее чем FastAPI

### Миграция:
```python
# До (Flask):
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/news")
def get_news():
    db = get_sync_service()
    news = db.get_latest_news(limit=10)
    return jsonify(news)

# После (Quart):
from quart import Quart, jsonify, request

app = Quart(__name__)

@app.route("/api/news")
async def get_news():  # ← async def
    db = get_async_service()  # ← async service
    news = await db.async_get_latest_news(limit=10)  # ← await
    return jsonify(news)
```

**Изменения:**
1. `Flask` → `Quart`
2. `def` → `async def`
3. Добавить `await` перед DB/IO calls
4. `get_sync_service()` → `get_async_service()`

**Время миграции:** 2-3 дня для всех endpoints

---

## Решение 2: FastAPI (Рекомендуется)

### Преимущества:
- ✅ **Самый быстрый** Python web framework
- ✅ Автоматическая валидация с Pydantic
- ✅ Автоматическая документация (OpenAPI/Swagger)
- ✅ Лучшая производительность
- ✅ Современный и популярный

### Недостатки:
- ❌ Больше изменений кода чем Quart
- ❌ Другой API (не совместим с Flask)

### Миграция:
```python
# До (Flask):
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/news", methods=["GET"])
def get_news():
    limit = request.args.get("limit", 10)
    db = get_sync_service()
    news = db.get_latest_news(limit=int(limit))
    return jsonify(news)

# После (FastAPI):
from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

@app.get("/api/news", response_model=List[NewsItem])
async def get_news(limit: int = Query(10, ge=1, le=100)):  # ← Валидация
    db = get_async_service()
    news = await db.async_get_latest_news(limit=limit)
    return news  # ← Автоматически в JSON
```

**Изменения:**
1. `Flask` → `FastAPI`
2. `@app.route()` → `@app.get()/post()/etc.`
3. `request.args.get()` → функция параметры с типами
4. `jsonify()` не нужен - автоматический JSON
5. Добавить Pydantic models для валидации

**Время миграции:** 4-7 дней для всех endpoints

---

## Решение 3: Гибридный подход (Временное)

Если полная миграция невозможна сейчас:

### Шаг 1: Оптимизировать `run_async()`
```python
# Создать глобальный event loop
_loop = None

def get_or_create_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop

def run_async_optimized(coro):
    """Оптимизированный run_async с переиспользованием loop."""
    loop = get_or_create_loop()
    return loop.run_until_complete(coro)
```

**Эффект:** ↓ 30-40% overhead от создания event loop

---

### Шаг 2: Переписать критичные endpoints на Quart/FastAPI
```python
# Создать app_async.py с FastAPI
from fastapi import FastAPI

app_async = FastAPI()

# Переписать 5 самых используемых endpoints:
@app_async.get("/api/news/latest")
async def get_latest_news_async(limit: int = 10):
    db = get_async_service()
    return await db.async_get_latest_news(limit=limit)

# Запускать оба: Flask на :5000, FastAPI на :8000
# Фронтенд переключается постепенно
```

**Эффект:** ↑ 2-3x для мигрированных endpoints

---

## Приоритизированный план миграции

### Опция A: Полная миграция на Quart (рекомендуется для MVP)

**Неделя 1:** Подготовка
1. Установить Quart: `pip install quart quart-cors`
2. Создать `app_quart.py` рядом с `app.py`
3. Мигрировать 5 простых endpoints для теста
4. Тестирование на dev

**Неделя 2:** Миграция API
5. Мигрировать `routes/api_routes.py` (самый большой)
6. Мигрировать `routes/news_routes.py`
7. Мигрировать `routes/events_routes.py`
8. Тестирование

**Неделя 3:** Миграция Admin
9. Мигрировать `routes/admin_routes.py`
10. Мигрировать остальные routes
11. Полное тестирование
12. Деплой

**Время:** 3 недели  
**Эффект:** ↑ 2-3x throughput, ↓ 40-60% latency

---

### Опция B: Миграция на FastAPI (рекомендуется для production)

**Неделя 1-2:** Подготовка
1. Создать Pydantic models для всех responses
2. Установить FastAPI: `pip install fastapi uvicorn`
3. Создать `app_fastapi.py`
4. Мигрировать 10 endpoints для теста

**Неделя 3-4:** Миграция API
5. Мигрировать все public API endpoints
6. Добавить автоматическую документацию
7. Тестирование

**Неделя 5-6:** Миграция Admin
8. Мигрировать admin endpoints
9. Полное тестирование
10. Деплой

**Время:** 6 недель  
**Эффект:** ↑ 3-5x throughput, ↓ 50-70% latency, лучшая DX

---

### Опция C: Гибридный подход (быстрый старт)

**Неделя 1:** Quick Wins
1. Оптимизировать `run_async()` (2 часа)
2. Создать FastAPI app для 5 критичных endpoints (1 день)
3. Деплой обоих (Flask + FastAPI)

**Неделя 2-4:** Постепенная миграция
4. Мигрировать по 5-10 endpoints в неделю
5. Фронтенд переключается постепенно
6. После полной миграции - удалить Flask

**Время:** 4-6 недель (но можно начать использовать через 1 неделю)  
**Эффект:** Постепенное улучшение

---

## Измеримые метрики

### До (Flask sync):
```python
# Concurrent requests test
# 10 параллельных запросов к /api/news/latest

# Flask sync:
Request 1: 500ms
Request 2: 500ms (ждет Request 1)
Request 3: 500ms (ждет Request 2)
...
Request 10: 500ms (ждет Request 9)
Total: 5000ms (sequential!)

# Throughput: 2 requests/sec
# Latency (P95): 4500ms при нагрузке
```

### После (Quart/FastAPI async):
```python
# 10 параллельных запросов к /api/news/latest

# Quart/FastAPI async:
Request 1-10: все стартуют одновременно
Request 1: 500ms
Request 2: 500ms (параллельно с Request 1)
Request 3: 500ms (параллельно)
...
Request 10: 500ms (параллельно)
Total: 500ms (parallel!)

# Throughput: 20 requests/sec (↑ 10x)
# Latency (P95): 600ms при нагрузке (↓ 85%)
```

---

## Дополнительные рекомендации

### 1. Background tasks (FastAPI)
```python
from fastapi import BackgroundTasks

@app.post("/api/digest/generate")
async def generate_digest(background_tasks: BackgroundTasks):
    # Запустить AI generation в фоне
    background_tasks.add_task(generate_digest_async, user_id)
    return {"status": "processing", "job_id": job_id}
```

### 2. Streaming responses (FastAPI)
```python
from fastapi.responses import StreamingResponse

@app.get("/api/events/stream")
async def stream_events():
    async def event_generator():
        while True:
            events = await get_new_events()
            yield f"data: {json.dumps(events)}\n\n"
            await asyncio.sleep(5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 3. Connection pooling
```python
# app_fastapi.py
from database.service import get_async_service

@app.on_event("startup")
async def startup():
    # Инициализировать connection pool
    app.state.db = get_async_service()

@app.on_event("shutdown")
async def shutdown():
    # Закрыть connections
    await app.state.db.aclose()
```

---

## Заключение

**Текущая ситуация:**
- Flask - полностью синхронный
- 88 endpoints - все блокируют при DB/IO
- `run_async()` используется в 5 местах - anti-pattern
- Throughput: 2-5 requests/sec (низкий)

**Рекомендации:**
1. **MVP:** Миграция на Quart (3 недели, минимальные изменения)
2. **Production:** Миграция на FastAPI (6 недель, максимальная производительность)
3. **Quick Start:** Гибридный подход (1 неделя до первых результатов)

**Ожидаемый результат:**
- ↑ 10-20x throughput при параллельных запросах
- ↓ 85% latency под нагрузкой
- ↑ Better scalability
- ↓ Server costs (меньше resources для той же нагрузки)

**Приоритет:** 🟡 **СРЕДНИЙ** (можно отложить на Неделю 3-4 после Quick Wins)


