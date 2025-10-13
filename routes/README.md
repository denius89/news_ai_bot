# Routes Layer

Flask Blueprints для API endpoints PulseAI WebApp.

## Структура

- **`api_routes.py`** - Основные API endpoints
  - ⚠️ CRITICAL: Нет authentication и rate limiting
  - Subscriptions, user management, categories
  - Telegram WebApp webhook

- **`news_routes.py`** - Новости и главная страница
  - HTML templates для веб-интерфейса
  - API для получения новостей с фильтрацией
  - Интеграция с unified_digest_service

- **`events_routes.py`** - События и календарь
  - REST API для событий
  - Поддержка умной группировки
  - Фильтрация по категориям и группам

- **`dashboard_api.py`** - Dashboard API
  - Аналитика и метрики
  - User preferences
  - Digest management

## Проблемы

1. **Security**: API endpoints не защищены
2. **Legacy**: Используют `db_models` вместо `service.py`
3. **Validation**: Нет input validation
4. **Error handling**: Базовое error handling

## TODO

- [ ] Добавить authentication middleware
- [ ] Добавить rate limiting
- [ ] Добавить input validation
- [ ] Мигрировать на `database.service`
- [ ] Добавить proper error handling
- [ ] Добавить API documentation (OpenAPI)
