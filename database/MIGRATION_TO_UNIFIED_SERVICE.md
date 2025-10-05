# Миграция на Unified DatabaseService

## Обзор

Этот документ описывает процесс миграции с дублированных sync/async версий database операций на единый `DatabaseService`.

## Что изменилось

### До (Дублирование)
- `database/db_models.py` - синхронные операции
- `database/async_db_models.py` - асинхронные операции
- Дублированная логика в обоих файлах
- Разные интерфейсы для одних и тех же операций

### После (Унификация)
- `database/service.py` - единый сервис с поддержкой sync/async
- Единый интерфейс для всех операций
- Автоматический выбор между sync/async режимами
- Обратная совместимость через compatibility функции

## План миграции

### Этап 1: Внедрение нового сервиса ✅
- [x] Создан `database/service.py`
- [x] Реализован `DatabaseService` класс
- [x] Добавлены compatibility функции
- [x] Написаны тесты

### Этап 2: Постепенная замена импортов
Заменить импорты в следующих файлах:

#### 2.1 Парсеры
```python
# Было:
from database.db_models import upsert_news
from database.async_db_models import async_insert_news_batch

# Станет:
from database.service import upsert_news, async_upsert_news
```

#### 2.2 Сервисы
```python
# Было:
from database.db_models import get_latest_news
from database.async_db_models import async_get_latest_news

# Станет:
from database.service import get_latest_news, async_get_latest_news
```

#### 2.3 Telegram Bot handlers
```python
# Было:
from database.db_models import supabase
from database.async_db_models import init_async_supabase

# Станет:
from database.service import get_sync_service, get_async_service
```

### Этап 3: Обновление инициализации
```python
# Было:
await init_async_supabase()

# Станет:
service = get_async_service()
await service._init_async_client()
```

### Этап 4: Удаление старых файлов
После полной миграции:
- Удалить `database/db_models.py`
- Удалить `database/async_db_models.py`
- Обновить все импорты

## Преимущества новой архитектуры

### 1. Устранение дублирования
- Единая логика для sync/async операций
- Общие методы подготовки данных
- Консистентная обработка ошибок

### 2. Улучшенная поддерживаемость
- Одно место для изменений в database логике
- Единый интерфейс для всех операций
- Лучшая тестируемость

### 3. Обратная совместимость
- Старые функции продолжают работать
- Постепенная миграция без breaking changes
- Простой откат при необходимости

## Примеры использования

### Синхронное использование
```python
from database.service import DatabaseService

# Создание сервиса
service = DatabaseService(async_mode=False)

# Получение новостей
news = service.get_latest_news(categories=["crypto"], limit=10)

# Сохранение новостей
count = service.upsert_news(news_items)
```

### Асинхронное использование
```python
from database.service import DatabaseService

# Создание сервиса
service = DatabaseService(async_mode=True)
await service._init_async_client()

# Получение новостей
news = await service.async_get_latest_news(categories=["crypto"], limit=10)

# Сохранение новостей
count = await service.async_upsert_news(news_items)
```

### Глобальные сервисы (рекомендуется)
```python
from database.service import get_sync_service, get_async_service

# Синхронный сервис
sync_service = get_sync_service()
news = sync_service.get_latest_news()

# Асинхронный сервис
async_service = get_async_service()
news = await async_service.async_get_latest_news()
```

### Обратная совместимость
```python
# Старые импорты продолжают работать
from database.service import get_latest_news, upsert_news, async_get_latest_news, async_upsert_news

# Использование как раньше
news = get_latest_news(categories=["crypto"])
count = upsert_news(news_items)
```

## Тестирование

Все изменения покрыты тестами:
- Unit тесты для `DatabaseService`
- Тесты backward compatibility
- Интеграционные тесты

Запуск тестов:
```bash
pytest tests/test_database_service.py -v
```

## Риски и митигация

### Риск: Breaking changes
**Митигация:** Полная обратная совместимость через compatibility функции

### Риск: Производительность
**Митигация:** Тот же код, просто переорганизован

### Риск: Сложность миграции
**Митигация:** Постепенная миграция по файлам, возможность отката

## Следующие шаги

1. **Тестирование в dev окружении**
2. **Миграция парсеров** (низкий риск)
3. **Миграция сервисов** (средний риск)
4. **Миграция Telegram Bot** (высокий риск)
5. **Удаление старых файлов** (финальный шаг)

## Мониторинг

После каждого этапа миграции:
- Запустить полный набор тестов
- Проверить работу Telegram Bot
- Проверить парсинг новостей
- Проверить WebApp функциональность
