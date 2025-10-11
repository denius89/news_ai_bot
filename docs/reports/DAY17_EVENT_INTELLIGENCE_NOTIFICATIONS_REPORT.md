# Day 17 — Event Intelligence & Notifications (Part 3)

**Дата:** 11 января 2025  
**Статус:** ✅ Реализовано  
**Версия:** v3.0.0

## 🎯 Цель

Создать умную систему событий с персональными уведомлениями, кешированием, throttling и полным учетом API-лимитов всех провайдеров.

## ✅ Выполненные задачи

### 1. Rate Limit Manager ⚡

**Файл:** `services/rate_limit_manager.py`

**Реализовано:**
- ✅ Умное управление лимитами для всех 11 провайдеров
- ✅ Автоматический расчет времени ожидания
- ✅ Smart caching с TTL для каждого провайдера
- ✅ Мониторинг превышений лимитов
- ✅ Статистика использования API

**Конфигурация лимитов:**
```python
RATE_LIMITS = {
    'coinmarketcal': {'requests': 100, 'period': 86400, 'cache_ttl': 43200},  # 100/day, cache 12h
    'fmp': {'requests': 250, 'period': 86400, 'cache_ttl': 3600},  # 250/day, cache 1h
    'finnhub': {'requests': 60, 'period': 60, 'cache_ttl': 300},  # 60/min, cache 5min
    'football_data': {'requests': 10, 'period': 60, 'cache_ttl': 900},  # 10/min, cache 15min
    'pandascore': {'requests': 100, 'period': 86400, 'cache_ttl': 7200},  # 100/day, cache 2h
    'thesportsdb': {'requests': 100, 'period': 3600, 'cache_ttl': 1800},  # 100/h, cache 30min
    'github_releases': {'requests': 60, 'period': 3600, 'cache_ttl': 3600},  # 60/h, cache 1h
    'coingecko': {'requests': 50, 'period': 60, 'cache_ttl': 600},  # 50/min, cache 10min
    'defillama': {'requests': 300, 'period': 300, 'cache_ttl': 600},  # 300/5min, cache 10min
    'tokenunlocks': {'requests': 100, 'period': 3600, 'cache_ttl': 1800},  # 100/h, cache 30min
    'eodhd': {'requests': 100, 'period': 86400, 'cache_ttl': 3600},  # 100/day, cache 1h
    'oecd': {'requests': 50, 'period': 3600, 'cache_ttl': 21600},  # 50/h, cache 6h (HTML scraping)
}
```

**API:**
- `can_make_request(provider)` - проверка возможности запроса
- `record_request(provider)` - запись запроса
- `get_cached(provider, key)` - получение из кеша
- `set_cache(provider, key, data)` - сохранение в кеш
- `get_wait_time(provider)` - расчет времени ожидания
- `get_stats()` - статистика по всем провайдерам
- `clear_cache(provider)` - очистка кеша

### 2. Notification System 🔔

**Файл:** `services/notification_service.py`

**Реализовано:**
- ✅ Подготовка персональных дайджестов событий
- ✅ Отправка уведомлений через Telegram и WebApp
- ✅ Управление предпочтениями пользователей
- ✅ Rate limiting (макс. 3 уведомления/день)
- ✅ Фильтрация событий по категориям и важности
- ✅ Форматирование сообщений с эмодзи

**Основные методы:**
- `prepare_daily_digest(user_id)` - подготовка дайджеста
- `send_telegram_notification(user_id, events)` - отправка в Telegram
- `push_webapp_notification(user_id, events)` - отправка в WebApp
- `get_user_preferences(user_id)` - получение настроек
- `update_user_preferences(user_id, preferences)` - обновление настроек

**Логика фильтрации:**
- Фильтр по категориям (crypto, markets, sports, tech, world)
- Фильтр по минимальной важности (0.0-1.0)
- Только upcoming события
- Только события на ближайшие 7 дней
- Группировка по важности (high/medium)

### 3. Telegram Sender 📱

**Файл:** `notifications/telegram_sender.py`

**Реализовано:**
- ✅ Интеграция с существующим Telegram ботом
- ✅ Форматирование сообщений в Markdown
- ✅ Отправка уведомлений о событиях
- ✅ Отправка ежедневных дайджестов
- ✅ Обработка ошибок и retry логика

**Основные методы:**
- `send_notification(user_id, message, parse_mode)` - базовая отправка
- `send_event_notification(user_id, events)` - уведомление о событиях
- `send_daily_digest(user_id, digest_data)` - ежедневный дайджест

**Формат сообщений:**
```markdown
🔔 *Важные события:*

🪙 *Bitcoin Halving Event*
   📊 Важность: 90% | 📅 15.01 14:00
   🔗 [Подробнее](https://example.com)

📈 *FOMC Meeting*
   📊 Важность: 95% | 📅 20.01 18:00
   🔗 [Подробнее](https://example.com)
```

### 4. SSE Real-time Stream 🌊

**Файл:** `services/events_stream.py`

**Реализовано:**
- ✅ Server-Sent Events (SSE) для real-time обновлений
- ✅ Управление подключениями пользователей
- ✅ Rate limiting (30s между обновлениями)
- ✅ Broadcast для всех или конкретных пользователей
- ✅ Автоматическое удаление failed connections

**Основные методы:**
- `add_connection(user_id, connection)` - добавление подключения
- `remove_connection(user_id)` - удаление подключения
- `can_send_update(user_id)` - проверка rate limit
- `broadcast_event(event_type, event_data, user_ids)` - broadcast
- `send_to_user(user_id, event_type, event_data)` - отправка пользователю
- `get_stats()` - статистика подключений

**Типы событий:**
- `new` - новое событие
- `updated` - обновление события
- `removed` - удаление события
- `event_notification` - уведомление о событии

### 5. API Endpoints 🔌

**Файл:** `routes/api_routes.py`

**Добавлено 3 новых endpoint:**

#### GET `/api/user/preferences`
Получение настроек уведомлений пользователя.

**Response:**
```json
{
  "success": true,
  "data": {
    "categories": ["crypto", "markets"],
    "min_importance": 0.7,
    "delivery_method": "bot",
    "notification_frequency": "daily",
    "max_notifications_per_day": 3
  }
}
```

#### POST/PUT `/api/user/preferences`
Обновление настроек уведомлений.

**Request:**
```json
{
  "categories": ["crypto", "markets"],
  "min_importance": 0.7,
  "delivery_method": "bot",
  "notification_frequency": "daily",
  "max_notifications_per_day": 3
}
```

#### POST `/api/user/notifications/test`
Тестовая отправка уведомления.

**Response:**
```json
{
  "success": true,
  "message": "Test notification sent",
  "events_count": 5
}
```

### 6. Smart Scheduler 📅

**Файл:** `tools/events_scheduler.py`

**Реализовано:**
- ✅ Планирование фетчей с учетом rate limits
- ✅ Автоматический расчет оптимальных интервалов
- ✅ Принудительный fetch с флагом `--force`
- ✅ Просмотр расписания `--show-schedule`
- ✅ Очистка кеша `--clear-cache`

**Расписание фетчей:**
```python
FETCH_SCHEDULE = {
    'crypto': {'interval': 14400, 'providers': [...]},  # 4 часа
    'markets': {'interval': 21600, 'providers': [...]},  # 6 часов
    'sports': {'interval': 7200, 'providers': [...]},  # 2 часа
    'tech': {'interval': 43200, 'providers': [...]},  # 12 часов
    'world': {'interval': 21600, 'providers': [...]},  # 6 часов
}
```

**Использование:**
```bash
# Показать расписание
python tools/events_scheduler.py --show-schedule

# Запланировать фетч для категории
python tools/events_scheduler.py --category crypto

# Принудительный фетч
python tools/events_scheduler.py --category crypto --force

# Очистить кеш
python tools/events_scheduler.py --clear-cache all
```

### 7. Notification Sender Tool 📧

**Файл:** `tools/send_notifications.py`

**Реализовано:**
- ✅ Отправка уведомлений конкретному пользователю
- ✅ Массовая отправка всем пользователям
- ✅ Тестовый режим без реальной отправки
- ✅ Просмотр настроек пользователя
- ✅ Статистика отправки

**Использование:**
```bash
# Отправить пользователю
python tools/send_notifications.py --user 12345

# Тестовая отправка
python tools/send_notifications.py --user 12345 --test

# Отправить всем
python tools/send_notifications.py --all

# Показать настройки
python tools/send_notifications.py --show-preferences 12345
```

### 8. WebApp Settings UI ⚙️

**Файл:** `webapp/src/components/NotificationSettings.tsx`

**Реализовано:**
- ✅ React компонент для настройки уведомлений
- ✅ Выбор категорий с чекбоксами
- ✅ Слайдер минимальной важности
- ✅ Выбор частоты уведомлений
- ✅ Выбор способа доставки
- ✅ Слайдер максимума уведомлений/день
- ✅ Анимации с Framer Motion
- ✅ Dark mode support
- ✅ Валидация и сохранение

**UI компоненты:**
- Категории: crypto, markets, sports, tech, world
- Частота: realtime, hourly, daily, weekly
- Доставка: bot, webapp, all
- Важность: 0% - 100%
- Макс/день: 1 - 10

## 📊 Архитектура

### Схема взаимодействия

```
┌─────────────────┐
│   User (WebApp) │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│   API Endpoints     │ (/api/user/preferences)
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│  Notification Service    │
├──────────────────────────┤
│ - prepare_daily_digest() │
│ - send_notification()    │
│ - get/update_preferences │
└────────┬─────────────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌────────────────┐    ┌─────────────────┐
│ Telegram Sender│    │  Events Stream  │
│                │    │      (SSE)      │
└────────────────┘    └─────────────────┘
         │                      │
         ▼                      ▼
┌────────────────┐    ┌─────────────────┐
│  Telegram Bot  │    │  WebApp Client  │
└────────────────┘    └─────────────────┘
```

### Rate Limit Flow

```
┌──────────────────┐
│  Event Scheduler │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Rate Limit Manager      │
├──────────────────────────┤
│ - can_make_request()?    │
│ - get_cached()?          │
│ - record_request()       │
│ - set_cache()            │
└────────┬─────────────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐         ┌──────────────────┐
│  Cache (TTL)    │         │  Request History │
│  - 12h crypto   │         │  - 100/day limit │
│  - 1h markets   │         │  - 60/min limit  │
│  - 5min sports  │         │  - 10/min limit  │
└─────────────────┘         └──────────────────┘
```

## 🗄️ База данных

### Таблица: `user_preferences`

```sql
CREATE TABLE IF NOT EXISTS user_preferences (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL UNIQUE REFERENCES users(telegram_id) ON DELETE CASCADE,
  categories TEXT[] DEFAULT '{}',
  min_importance NUMERIC DEFAULT 0.6 CHECK (min_importance >= 0 AND min_importance <= 1),
  delivery_method TEXT DEFAULT 'bot' CHECK (delivery_method IN ('bot', 'webapp', 'email', 'all')),
  notification_frequency TEXT DEFAULT 'daily' CHECK (notification_frequency IN ('realtime', 'hourly', 'daily', 'weekly')),
  max_notifications_per_day INT DEFAULT 3 CHECK (max_notifications_per_day >= 1 AND max_notifications_per_day <= 10),
  last_notified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Таблица: `event_logs`

```sql
CREATE TABLE IF NOT EXISTS event_logs (
  id BIGSERIAL PRIMARY KEY,
  event_id INT REFERENCES events_new(id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
  action TEXT NOT NULL CHECK (action IN ('viewed', 'notified', 'clicked', 'dismissed')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 📈 Метрики и мониторинг

### Rate Limit Statistics

```python
{
    "providers": {
        "coinmarketcal": {
            "current_requests": 45,
            "max_requests": 100,
            "period_seconds": 86400,
            "cache_ttl": 43200,
            "limit_exceeded_count": 0,
            "can_request": True,
            "wait_time": 0.0
        },
        ...
    },
    "total_cached_items": 127,
    "total_limit_exceeded": 3
}
```

### Notification Statistics

```python
{
    "total_users": 150,
    "sent": 120,
    "failed": 5,
    "skipped": 25  # No matching events
}
```

## 🧪 Тестирование

### Unit тесты

- ✅ `tests/unit/services/test_rate_limit_manager.py` - rate limiter, caching
- ✅ `tests/unit/services/test_notification_service.py` - уведомления
- ✅ `tests/unit/services/test_events_stream.py` - SSE stream
- ✅ `tests/unit/notifications/test_telegram_sender.py` - Telegram отправка

### Integration тесты

- ✅ `tests/integration/test_notifications_flow.py` - полный flow уведомлений
- ✅ `tests/integration/test_rate_limits.py` - проверка лимитов
- ✅ `tests/integration/test_user_preferences.py` - API preferences

## 🚀 Использование

### 1. Настройка уведомлений (WebApp)

```typescript
// Открыть страницу настроек
<NotificationSettings />

// Выбрать категории
categories: ['crypto', 'markets']

// Установить важность
min_importance: 0.7

// Сохранить
await savePreferences()
```

### 2. Планирование фетчей

```bash
# Показать расписание
python tools/events_scheduler.py --show-schedule

# Запланировать crypto фетч
python tools/events_scheduler.py --category crypto

# Принудительный фетч всех категорий
python tools/events_scheduler.py --force
```

### 3. Отправка уведомлений

```bash
# Отправить пользователю
python tools/send_notifications.py --user 12345

# Отправить всем (тест)
python tools/send_notifications.py --all --test

# Отправить всем (production)
python tools/send_notifications.py --all
```

### 4. Мониторинг

```python
# Проверить статистику rate limits
from services.rate_limit_manager import get_rate_limit_manager

rate_limiter = get_rate_limit_manager()
stats = rate_limiter.get_stats()
print(stats)

# Проверить статистику stream
from services.events_stream import get_events_stream

stream = get_events_stream()
stats = stream.get_stats()
print(stats)
```

## 📝 Команды

```bash
# Запланировать фетчи
python tools/events_scheduler.py --category crypto
python tools/events_scheduler.py --show-schedule
python tools/events_scheduler.py --clear-cache all

# Отправить уведомления
python tools/send_notifications.py --user 12345
python tools/send_notifications.py --all --test
python tools/send_notifications.py --show-preferences 12345

# Тестирование
pytest tests/unit/services/test_rate_limit_manager.py
pytest tests/integration/test_notifications_flow.py
```

## ✅ Acceptance Criteria

- ✅ SQL миграция применена пользователем
- ✅ Rate-limit manager работает и логирует превышения
- ✅ Event Intelligence Layer кеширует и планирует фетчи
- ✅ Уведомления отправляются ботом и WebApp
- ✅ Пользователь может задать предпочтения в WebApp
- ✅ Real-time обновления работают (SSE)
- ✅ Все тесты проходят
- ✅ Линтер и форматтер проходят

## 🎉 Итоги

**Day 17 успешно завершен!**

Создана полноценная система Event Intelligence & Notifications с:
- ✅ Умным управлением API лимитами
- ✅ Персональными уведомлениями
- ✅ Real-time обновлениями
- ✅ WebApp UI для настроек
- ✅ CLI tools для управления
- ✅ Полным тестированием

**Готово к production использованию!** 🚀

