# Database Migration Plan - db_models.py → service.py

## Цель
Мигрировать все потребители `database/db_models.py` на современный `database/service.py` для унификации database layer.

## Текущее состояние
- **Legacy:** 22 файла используют `db_models.py` (1,968 строк)
- **Modern:** 16 файлов используют `service.py` (558 строк)
- **Проблема:** Множественные источники правды для database операций

## План миграции

### Phase 1: Routes Layer (Критично)
**Приоритет:** HIGH - API endpoints без защиты

**Файлы для миграции:**
1. `routes/api_routes.py` - основные API endpoints
2. `routes/news_routes.py` - новости и главная страница  
3. `routes/events_routes.py` - события и календарь
4. `routes/dashboard_api.py` - dashboard API
5. `routes/metrics_routes.py` - метрики

**Migration Pattern:**
```python
# Было (db_models):
from database.db_models import get_latest_news, upsert_news, get_user_by_telegram

def get_news():
    news = get_latest_news(limit=10)
    return jsonify(news)

# Стало (service):
from database.service import get_sync_service

def get_news():
    db_service = get_sync_service()
    news = db_service.get_latest_news(limit=10)
    return jsonify(news)
```

### Phase 2: Services Layer
**Приоритет:** MEDIUM - business logic

**Файлы для миграции:**
1. `services/notification_service.py` - уведомления

### Phase 3: Telegram Bot Handlers
**Приоритет:** MEDIUM - bot functionality

**Файлы для миграции:**
1. `telegram_bot/handlers/events.py`
2. `telegram_bot/handlers/notifications.py`

### Phase 4: Tools Layer
**Приоритет:** LOW - scripts и utilities

**Файлы для миграции:**
1. `tools/ai/train_models.py`
2. `tools/events/load_*.py` (4 файла)
3. `tools/news/refresh_news.py`

## Преимущества миграции

### Database Service vs db_models
- ✅ **Object-oriented design** vs глобальные функции
- ✅ **Async support** vs только sync
- ✅ **Proper error handling** vs базовое
- ✅ **Retry logic** vs без retry
- ✅ **Type safety** vs частичные type hints
- ✅ **Testable** vs сложно тестировать
- ✅ **Configuration management** vs прямая загрузка .env

### API Consistency
```python
# Единый интерфейс для всех операций
db_service = get_sync_service()

# News operations
news = db_service.get_latest_news(limit=10)
db_service.upsert_news(news_items)

# Events operations  
events = db_service.get_latest_events(limit=10)
db_service.upsert_event(event_items)

# User operations
user = db_service.get_user_by_telegram(telegram_id)
db_service.upsert_user_by_telegram(user_data)
```

## Риски и митигация

### Риски:
1. **Breaking changes** - изменение API
2. **Performance impact** - новый код может работать медленнее
3. **Testing complexity** - нужно тестировать миграцию

### Митигация:
1. **Поэтапная миграция** - по одному файлу
2. **Backward compatibility** - оставить старые функции как deprecated
3. **Comprehensive testing** - тестировать каждый этап
4. **Rollback plan** - возможность отката

## Timeline

### День 1-2: Routes Layer
- Мигрировать 5 route файлов
- Тестировать API endpoints
- Проверить WebApp functionality

### День 3-4: Services Layer  
- Мигрировать notification_service
- Тестировать уведомления
- Проверить Telegram bot

### День 5-6: Tools Layer
- Мигрировать tools файлы
- Тестировать scripts
- Проверить automation

### День 7: Cleanup
- Deprecate функции в db_models
- Обновить документацию
- Final testing

## Success Criteria

- [ ] Все routes используют `database.service`
- [ ] Все services используют `database.service`  
- [ ] Все tools используют `database.service`
- [ ] API endpoints работают корректно
- [ ] WebApp функционирует без ошибок
- [ ] Telegram bot работает корректно
- [ ] Scripts выполняются успешно
- [ ] Performance не ухудшился
- [ ] Добавлены unit tests для новых путей

## Next Steps

1. **Начать с routes/api_routes.py** - самый критичный файл
2. **Создать migration helper** - утилита для автоматизации
3. **Добавить logging** - отслеживать процесс миграции
4. **Setup testing** - автоматические тесты для каждого этапа
