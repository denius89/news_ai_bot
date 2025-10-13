# Database Layer

Модули для работы с базой данных PulseAI через Supabase.

## Структура

- **`db_models.py`** - Legacy модуль (1,968 строк, 22 потребителя)
  - ⚠️ Устаревший подход, используйте `service.py`
  - Глобальный синхронный Supabase клиент
  - Смешивает разные домены (news, events, users, digests)

- **`service.py`** - ✅ Рекомендуемый модуль (558 строк, 16 потребителей)
  - Современный объектно-ориентированный подход
  - Поддержка sync и async операций
  - Proper error handling и retry logic
  - Factory functions для создания сервисов

- **`events_service.py`** - Специализированный сервис для событий (220 строк)
  - Dataclass `EventRecord` для типизации
  - Async/sync методы для работы с событиями
  - Умная группировка по `group_name`

- **`async_db_models.py`** - Async wrapper (271 строка)
  - ⚠️ Не используется напрямую
  - Дублирует функционал `DatabaseService(async_mode=True)`

## Миграция

```python
# Старый способ (db_models):
from database.db_models import get_latest_news, upsert_news
news = get_latest_news(limit=10)
upsert_news(news_items)

# Новый способ (service):
from database.service import get_sync_service
db_service = get_sync_service()
news = db_service.get_latest_news(limit=10)
db_service.upsert_news(news_items)
```

## Конфигурация

Все модули используют `config.core.settings` для получения:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## TODO

- [ ] Мигрировать все потребители `db_models.py` на `service.py`
- [ ] Разбить `db_models.py` на доменные модули
- [ ] Добавить unit tests для всех сервисов
- [ ] Deprecate `db_models.py` после миграции
