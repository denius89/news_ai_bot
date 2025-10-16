# ✅ Admin Panel Configuration - Готово!

## 🎉 Что реализовано

### Backend API (Flask)

Все endpoints добавлены в `routes/admin_routes.py`:

1. **`/admin/api/config/all`** - Получить все настройки из БД, сгруппированные по категориям
2. **`/admin/api/config/<category>/<key>`** (PUT) - Обновить конкретную настройку
3. **`/admin/api/prompts`** - Получить промпты из `digests/prompts_v2.py`
4. **`/admin/api/sources`** - Получить структуру источников из `services/categories.py`
5. **`/admin/api/sources/test`** (POST) - Протестировать RSS парсер
6. **`/admin/api/system/status`** - Мониторинг сервисов и системных ресурсов

### Frontend Hooks

Созданы в `webapp/src/admin/hooks/`:

- **`useConfig.ts`** - `useAllConfig()`, `useUpdateConfig()`
- **`usePrompts.ts`** - `usePrompts()`
- **`useSources.ts`** - `useSources()`, `useTestSource()`
- **`useSystemStatus.ts`** - `useSystemStatus()` (автообновление каждые 10 сек)

### React Components

Созданы в `webapp/src/admin/components/config/`:

#### 1. **AISettings** 🤖
- Выбор AI моделей (summarization, scoring)
- Слайдеры для `max_tokens`, `min_importance`, `min_credibility`
- Сохранение в БД с кнопкой "Сохранить настройки"

#### 2. **PromptsViewer** 📝
- Просмотр всех стилей (newsroom, analytical, magazine, etc.)
- Просмотр всех тонов (neutral, insightful, optimistic, etc.)
- Read-only режим с badge "View Only"

#### 3. **SourcesManager** 📰
- Статистика источников (категории, подкатегории, источники)
- Структура всех источников по категориям
- Тестирование RSS парсера (любой URL)

#### 4. **SystemSettings** ⚙️
- News fetch interval (минуты)
- Max digest items
- Notification hour (0-23)
- API rate limit
- Сохранение в БД

#### 5. **SystemMonitor** 📊
- Статус сервисов (Flask, Bot, Database)
- CPU/Memory/Disk usage с progress bars
- Uptime системы
- Автообновление каждые 10 секунд

### UI Components

Добавлены в `webapp/src/components/ui/`:

- **`Progress.tsx`** - Progress bar для ресурсов
- **`Badge.tsx`** - Badges для статусов

---

## 🚀 Как использовать

### 1. Открыть Admin Panel

```
http://localhost:8001/admin
```

### 2. Перейти на вкладку Config

В sidebar кликните на "Config" или перейдите напрямую:

```
http://localhost:8001/admin/config
```

### 3. Навигация по табам

- **AI Settings** - Настройка моделей и порогов
- **Prompts** - Просмотр промптов
- **Sources** - Управление источниками новостей
- **System** - Системные настройки
- **Monitor** - Мониторинг сервисов

---

## 📊 Примеры использования

### Изменить AI модель

1. Перейти на таб "AI Settings"
2. Выбрать новую модель из dropdown (gpt-4o, claude-3-sonnet, etc.)
3. Нажать "Сохранить настройки"
4. Изменения сохранятся в БД (`system_config` таблица)

### Протестировать RSS парсер

1. Перейти на таб "Sources"
2. Ввести URL RSS ленты
3. Нажать "Тест"
4. Увидеть результат: количество новостей + примеры

### Мониторинг системы

1. Перейти на таб "Monitor"
2. Увидеть статус всех сервисов в реальном времени
3. CPU/Memory/Disk usage обновляются каждые 10 секунд

---

## 🗄️ База данных

Все настройки хранятся в таблице `system_config`:

```sql
SELECT * FROM system_config WHERE category = 'ai';
```

Пример записи:

```json
{
  "key": "ai.model_summary",
  "value": "gpt-4o-mini",
  "category": "ai",
  "description": "AI model for summarization",
  "updated_at": "2025-10-15T11:36:43.926824+00:00"
}
```

---

## 🔧 Технические детали

### Backend

- **Framework**: Flask
- **Database**: PostgreSQL (Supabase)
- **Authentication**: `@require_admin` decorator
- **Monitoring**: `psutil` для системных метрик

### Frontend

- **Framework**: React 18 + TypeScript
- **State Management**: TanStack Query (React Query)
- **UI**: Tailwind CSS + shadcn/ui
- **Auto-refresh**: System status каждые 10 секунд

### API Response Examples

**GET /admin/api/config/all**:
```json
{
  "ai": {
    "model_summary": {
      "value": "gpt-4o-mini",
      "description": "AI model for summarization",
      "updated_at": "2025-10-15T11:36:43+00:00"
    }
  }
}
```

**GET /admin/api/system/status**:
```json
{
  "services": {
    "flask": { "running": true, "status": "ok" },
    "bot": { "running": true, "status": "ok" },
    "database": { "running": true, "status": "ok" }
  },
  "resources": {
    "cpu_percent": 28.1,
    "memory_percent": 85.6
  },
  "uptime": "0:15:32"
}
```

---

## ✅ Checklist

- [x] Database migration выполнена
- [x] Backend API endpoints реализованы
- [x] Frontend hooks созданы
- [x] React components созданы
- [x] UI components добавлены
- [x] Frontend собран (npm run build)
- [x] Flask перезапущен
- [x] API endpoints протестированы
- [ ] Интеграция с `config/core/settings.py` (опционально)

---

## 🎯 Что дальше?

### Опциональные улучшения

1. **Интеграция с settings.py** - Читать настройки из БД при старте приложения
2. **Включение/выключение источников** - Toggle для каждого источника
3. **Редактирование промптов** - UI для изменения промптов (v2)
4. **Audit log** - История изменений настроек
5. **Validation** - Более строгая валидация значений

---

## 📝 Файлы проекта

### Backend
- `routes/admin_routes.py` - Все API endpoints
- `database/migrations/2025_10_15_system_config.sql` - Миграция БД

### Frontend
- `webapp/src/admin/pages/AdminConfig.tsx` - Главная страница
- `webapp/src/admin/hooks/useConfig.ts`
- `webapp/src/admin/hooks/usePrompts.ts`
- `webapp/src/admin/hooks/useSources.ts`
- `webapp/src/admin/hooks/useSystemStatus.ts`
- `webapp/src/admin/components/config/AISettings.tsx`
- `webapp/src/admin/components/config/PromptsViewer.tsx`
- `webapp/src/admin/components/config/SourcesManager.tsx`
- `webapp/src/admin/components/config/SystemSettings.tsx`
- `webapp/src/admin/components/config/SystemMonitor.tsx`
- `webapp/src/components/ui/Progress.tsx`
- `webapp/src/components/ui/Badge.tsx`

---

**Дата реализации:** 15 октября 2025  
**Статус:** ✅ Полностью готово и работает  
**Тестирование:** Все endpoints протестированы, frontend собран успешно

