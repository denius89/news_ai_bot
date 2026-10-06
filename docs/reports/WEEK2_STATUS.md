# 📊 Week 2 Status: Subscriptions & Core Features

**Дата создания:** 17 октября 2025  
**Статус:** 80% готово ✅  
**Осталось:** ~6 часов работы

---

## 🎯 Цель Week 2

Интегрировать систему подписок и уведомлений с реальной логикой бота для автоматической отправки персонализированных дайджестов.

---

## ✅ ЧТО УЖЕ ГОТОВО (80%)

### 1. Database Layer (100% ✅)

**Таблицы созданы и мигрированы:**

```sql
-- users - пользователи Telegram
CREATE TABLE users (
  id UUID PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  locale TEXT DEFAULT 'ru',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- subscriptions - подписки на категории
CREATE TABLE subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  category TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, category)
);

-- notifications - настройки уведомлений по типу
CREATE TABLE notifications (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('digest','events','breaking')),
  frequency TEXT NOT NULL DEFAULT 'daily',
  preferred_hour SMALLINT DEFAULT 9,
  enabled BOOLEAN DEFAULT TRUE,
  UNIQUE(user_id, type)
);

-- notification_settings - детальные настройки по категориям
CREATE TABLE notification_settings (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  category TEXT NOT NULL,
  enabled BOOLEAN DEFAULT true,
  via_telegram BOOLEAN DEFAULT true,
  via_webapp BOOLEAN DEFAULT true,
  UNIQUE(user_id, category)
);
```

**Миграции применены:**
- ✅ `2025_10_02_subscriptions_notifications.sql`
- ✅ `2025_10_02_notifications_system.sql`
- ✅ `2025_10_02_notifications_indexes.sql`
- ✅ `2025_10_03_user_notifications.sql`

**Индексы созданы:**
- ✅ `idx_users_tg` - быстрый поиск по telegram_id
- ✅ `idx_subs_user` - подписки пользователя
- ✅ `idx_notif_user` - уведомления пользователя
- ✅ `idx_notification_settings_user` - настройки по категориям

---

### 2. Services Layer (100% ✅)

#### SubscriptionService (`services/subscription_service.py`)

```python
class SubscriptionService:
    """Service for managing user subscriptions."""
    
    async def get_user_subscriptions(user_id: int) -> Dict[str, List[str]]
        """Получить подписки пользователя."""
        
    async def subscribe_to_category(user_id: int, category: str) -> bool
        """Подписать пользователя на категорию."""
        
    async def unsubscribe_from_category(user_id: int, category: str) -> bool
        """Отписать пользователя от категории."""
        
    async def subscribe_to_subcategory(user_id: int, category: str, subcategory: str) -> bool
        """Подписать на подкатегорию."""
        
    async def unsubscribe_from_subcategory(user_id: int, category: str, subcategory: str) -> bool
        """Отписать от подкатегории."""
```

**Статус:** Полностью реализован, работает с async/sync режимами.

#### NotificationService (`services/notification_service.py`)

```python
class NotificationService:
    """Service for managing notifications."""
    
    async def get_users_by_notification_type(type: str, hour: int) -> List[Dict]
        """Получить пользователей для уведомлений в определенный час."""
```

**Статус:** Используется в send_digests.py, работает корректно.

---

### 3. Database Functions (100% ✅)

**Файл:** `database/db_models.py`

```python
def add_subscription(user_id: str, category: str) -> bool
    """Добавить подписку на категорию."""

def remove_subscription(user_id: str, category: str) -> int
    """Удалить подписку на категорию."""

def list_subscriptions(user_id: str) -> list[dict]
    """Получить список подписок пользователя."""

def upsert_notification(
    user_id: str,
    type_: str = "digest",
    frequency: str = "daily",
    enabled: bool = True,
    preferred_hour: int = 9,
) -> None
    """Создать или обновить настройки уведомлений."""
```

**Статус:** Все функции реализованы и протестированы.

---

### 4. Automatic Digest Sending (100% ✅)

**Файл:** `tools/notifications/send_digests.py` (338 строк)

**Архитектура:**
- ✅ Async/await для параллельной отправки
- ✅ Часовые пояса (Europe/Warsaw)
- ✅ Персонализация по подпискам пользователя
- ✅ Error handling и retry logic
- ✅ Graceful degradation (fallback для дайджестов)
- ✅ Логирование всех действий
- ✅ Ограничение параллелизма (semaphore)

**Ключевые функции:**

```python
async def get_users_for_digest(notif_svc, target_hour) -> List[Dict]
    """Получить пользователей для отправки в определенный час."""

async def get_user_subscriptions(subs_svc, user_id) -> List[str]
    """Получить категории подписок пользователя."""

async def fetch_news_by_categories(categories, limit=10) -> List[NewsItem]
    """Получить свежие новости по категориям."""

async def generate_personalized_digest(news_items, user_categories, style) -> str
    """Сгенерировать персонализированный дайджест."""

async def send_personalized_digest(user, subs_svc, telegram_sender) -> bool
    """Отправить дайджест пользователю."""

async def main()
    """Основная функция - полный цикл отправки дайджестов."""
```

**Использование:**
```bash
# Запуск из корня проекта
python tools/notifications/send_digests.py
```

**Что делает:**
1. Определяет текущий час в Europe/Warsaw
2. Получает пользователей с включенными уведомлениями на этот час
3. Для каждого пользователя:
   - Получает подписки (категории)
   - Загружает новости по этим категориям
   - Генерирует персонализированный AI дайджест
   - Отправляет в Telegram
4. Логирует результаты (успешно/ошибки)

**Статус:** Полностью готов к использованию!

---

### 5. Telegram Bot Integration (90% ✅)

**Файлы:**
- `telegram_bot/handlers/subscriptions.py` - handlers для подписок
- `telegram_bot/keyboards.py` - клавиатуры для bot

**Что работает:**
- ✅ `/subscribe` - подписка на категорию
- ✅ `/unsubscribe` - отписка от категории
- ✅ `/subscriptions` - список подписок
- ✅ Inline keyboards с категориями

**Что осталось:**
- [ ] Интеграция с SubscriptionService (сейчас используются прямые запросы к БД)

---

## ❌ ЧТО ОСТАЛОСЬ СДЕЛАТЬ (20%)

### 1. API Endpoints (2 часа)

**Файл:** `routes/api_routes.py`

**Проблема:** Endpoints возвращают 501 (Not Implemented)

#### Endpoint 1: GET /api/notification-settings

**Текущий код (line 654-662):**
```python
@api_bp.route("/notification-settings", methods=["GET"])
def get_notification_settings():
    """
    GET /api/notification-settings?user_id=<id>
    Returns user's notification settings for all categories.
    TODO (Week 2): Implement get_notification_settings function in db_models
    Запланировано в Subscriptions Integration
    """
    return jsonify({"status": "error", "message": "Not implemented yet"}), 501
```

**Что нужно:**
```python
@api_bp.route("/notification-settings", methods=["GET"])
def get_notification_settings():
    """GET /api/notification-settings?user_id=<id>"""
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        return jsonify({"status": "error", "message": "user_id required"}), 400
    
    try:
        # Query notification_settings table
        result = supabase.table("notification_settings")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        settings = result.data or []
        return jsonify({"status": "success", "settings": settings})
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
```

#### Endpoint 2: POST /api/notification-settings/update

**Текущий код (line 665-673):**
```python
@api_bp.route("/notification-settings/update", methods=["POST"])
def update_notification_settings():
    """
    POST /api/notification-settings/update
    Updates user's notification settings.
    TODO (Week 2): Implement upsert_notification_setting function in db_models
    Запланировано в Subscriptions Integration
    """
    return jsonify({"status": "error", "message": "Not implemented yet"}), 501
```

**Что нужно:**
```python
@api_bp.route("/notification-settings/update", methods=["POST"])
def update_notification_settings():
    """
    POST /api/notification-settings/update
    Body: {
        "user_id": 123,
        "category": "crypto",
        "enabled": true,
        "via_telegram": true,
        "via_webapp": true
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "JSON required"}), 400
    
    user_id = data.get("user_id")
    category = data.get("category")
    enabled = data.get("enabled", True)
    
    if not all([user_id, category]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    
    try:
        result = supabase.table("notification_settings").upsert({
            "user_id": user_id,
            "category": category,
            "enabled": enabled,
            "via_telegram": data.get("via_telegram", True),
            "via_webapp": data.get("via_webapp", True),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="user_id,category").execute()
        
        return jsonify({"status": "success", "result": result.data})
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
```

**Acceptance Criteria:**
- [ ] GET endpoint возвращает настройки пользователя
- [ ] POST endpoint обновляет/создает настройки
- [ ] Error handling для всех случаев
- [ ] Валидация входных данных
- [ ] Логирование ошибок

---

### 2. Cron Jobs Setup (1 час)

**Что нужно:**

#### Создать wrapper scripts:

**Файл:** `scripts/send_morning_digests.sh`
```bash
#!/bin/bash
cd /home/user/news_ai_bot
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

python tools/notifications/send_digests.py >> logs/digests_morning.log 2>&1
echo "$(date): Morning digests sent" >> logs/cron.log
```

**Файл:** `scripts/send_evening_digests.sh`
```bash
#!/bin/bash
cd /home/user/news_ai_bot
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

python tools/notifications/send_digests.py >> logs/digests_evening.log 2>&1
echo "$(date): Evening digests sent" >> logs/cron.log
```

#### Настроить crontab:

```bash
# Edit crontab
crontab -e

# Add:
# Morning digest at 9:00 AM (Europe/Warsaw)
0 9 * * * /home/user/news_ai_bot/scripts/send_morning_digests.sh

# Evening digest at 6:00 PM (Europe/Warsaw)
0 18 * * * /home/user/news_ai_bot/scripts/send_evening_digests.sh
```

**Или документировать без настройки:**
Создать `CRON_SETUP.md` с инструкциями для пользователя.

**Acceptance Criteria:**
- [ ] Wrapper scripts созданы и исполняемы
- [ ] Scripts протестированы вручную
- [ ] Crontab настроен ИЛИ задокументирован
- [ ] Логи пишутся корректно

---

### 3. Pagination для /api/news (1 час)

**Файл:** `routes/news_routes.py` (line 45)

**Текущий TODO:**
```python
# TODO (Week 2): Добавить pagination для больших списков
# Запланировано после Subscriptions Integration
```

**Что нужно:**

```python
@news_bp.route("/api/news")
def get_news_list():
    """
    GET /api/news?page=1&per_page=50&category=crypto
    
    Returns:
        {
            "status": "success",
            "news": [...],
            "pagination": {
                "page": 1,
                "per_page": 50,
                "total": 1234,
                "pages": 25
            }
        }
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    category = request.args.get("category")
    
    # Validate and limit per_page
    per_page = min(max(per_page, 1), 100)  # Between 1 and 100
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Query with pagination
    query = supabase.table("news").select("*", count="exact")
    
    if category:
        query = query.eq("category", category)
    
    query = query.order("published_at", desc=True)\
                 .range(offset, offset + per_page - 1)
    
    result = query.execute()
    
    news = result.data or []
    total = result.count if hasattr(result, 'count') else len(news)
    
    return jsonify({
        "status": "success",
        "news": news,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })
```

**Acceptance Criteria:**
- [ ] Pagination parameters работают (page, per_page)
- [ ] Фильтрация по category работает
- [ ] Limit max 100 items per page
- [ ] Возвращается pagination metadata
- [ ] Обработка edge cases (page=0, negative values)

---

### 4. Testing & Integration (2 часа)

**Что нужно:**

#### 4.1 End-to-End тестирование:

```bash
# 1. Запустить send_digests.py вручную
python tools/notifications/send_digests.py

# 2. Проверить логи
tail -f logs/app.log

# 3. Протестировать API endpoints
curl "http://localhost:8001/api/notification-settings?user_id=1"

curl -X POST http://localhost:8001/api/notification-settings/update \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "category": "crypto", "enabled": true}'

# 4. Протестировать pagination
curl "http://localhost:8001/api/news?page=1&per_page=10&category=crypto"
```

#### 4.2 Написать integration тесты:

**Файл:** `tests/integration/test_subscriptions_flow.py`

```python
import pytest
from services.subscription_service import SubscriptionService
from database.db_models import get_notification_settings, upsert_notification_setting

@pytest.mark.asyncio
async def test_subscription_flow():
    """Test full subscription flow."""
    service = SubscriptionService(async_mode=True)
    
    # 1. Subscribe
    result = await service.subscribe_to_category(user_id=1, category="crypto")
    assert result is True
    
    # 2. Get subscriptions
    subs = await service.get_user_subscriptions(user_id=1)
    assert "crypto" in subs["categories"]
    
    # 3. Unsubscribe
    result = await service.unsubscribe_from_category(user_id=1, category="crypto")
    assert result is True
```

#### 4.3 Обновить документацию:

**Создать:** `docs/SUBSCRIPTIONS_GUIDE.md`
- Как работает система подписок
- Как пользователи подписываются
- Как работает автоматическая отправка
- Настройка cron jobs
- API endpoints

**Обновить:** `README.md`
- Добавить секцию "Subscriptions & Notifications"
- Примеры использования API

**Обновить:** `PRODUCTION_CHECKLIST.md`
- [x] Week 2: Subscriptions Integration (completed)

**Acceptance Criteria:**
- [ ] End-to-end тест проходит
- [ ] Integration тесты написаны и проходят
- [ ] Документация обновлена
- [ ] README актуален

---

## 📊 УПРОЩЕННЫЙ ПЛАН ВЫПОЛНЕНИЯ

### День 1 (3 часа):
- **09:00-11:00** - Этап 2.1: API Endpoints (2 часа)
- **11:00-12:00** - Этап 2.2: Cron Jobs (1 час)

### День 2 (3 часа):
- **09:00-10:00** - Этап 2.3: Pagination (1 час)
- **10:00-12:00** - Этап 2.4: Testing & Integration (2 часа)

**Итого:** 6 часов работы, 2 дня

---

## 🔍 ВАЖНЫЕ ФАЙЛЫ

### Для изменения:
1. `routes/api_routes.py` - lines 654-673 (API endpoints)
2. `routes/news_routes.py` - add pagination
3. `scripts/send_morning_digests.sh` - создать
4. `scripts/send_evening_digests.sh` - создать

### Для тестирования:
1. `tools/notifications/send_digests.py` - запустить
2. API endpoints - curl тесты
3. `tests/integration/test_subscriptions_flow.py` - создать

### Для документирования:
1. `docs/SUBSCRIPTIONS_GUIDE.md` - создать
2. `README.md` - обновить
3. `PRODUCTION_CHECKLIST.md` - отметить Week 2

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **Начать с Этапа 2.1** (API Endpoints) - самое важное
2. **Затем Этап 2.2** (Cron Jobs) - для автоматизации
3. **Затем Этап 2.3** (Pagination) - для масштабирования
4. **Завершить Этапом 2.4** (Testing) - проверка всего

**После Week 2:**
- Week 3: Performance & Infrastructure (caching, rate limiting, monitoring)
- Week 4: CI/CD & Security
- Week 5: Load Testing & Monetization
- Week 6: Deployment & Launch

---

## 📞 КОНТАКТЫ И РЕСУРСЫ

**Repository:** https://github.com/repository-owner/news_ai_bot  
**Documentation:** docs/README.md  
**Production Checklist:** PRODUCTION_CHECKLIST.md

**Ключевые файлы:**
- Database: `database/migrations/2025_10_02_*.sql`
- Services: `services/subscription_service.py`, `services/notification_service.py`
- Tools: `tools/notifications/send_digests.py`
- Routes: `routes/api_routes.py`, `routes/news_routes.py`

---

**Последнее обновление:** 17 октября 2025  
**Статус:** 80% готово, осталось 6 часов работы  
**Приоритет:** Week 2 - критично для MVP

