# WebSocket Migration Audit Report

**Дата:** 2024-12-19  
**Цель:** Миграция с Flask-SocketIO на чистый FastAPI WebSocket  
**Статус:** Префлайт-аудит завершен

## 🔍 Найденные Flask-SocketIO артефакты

### 1. Backend файлы с SocketIO зависимостями

| Файл | Строки | Описание |
|------|--------|----------|
| `routes/ws_routes.py` | 11, 20-21, 27-32, 169 | Основной WebSocket роут с Flask-SocketIO |
| `webapp.py` | 51, 79, 84 | Инициализация SocketIO в Flask app |

### 2. Frontend файлы с Socket.IO

| Файл | Строки | Описание |
|------|--------|----------|
| `static/js/reactor.js` | 29, 47, 49, 63-87 | WebSocket клиент с Socket.IO CDN |
| `frontend/package.json` | 17 | socket.io-client зависимость |
| `frontend/src/components/ReactorProvider.jsx` | 2, 21 | React компонент с Socket.IO |

### 3. Зависимости для удаления

| Пакет | Версия | Статус |
|-------|--------|--------|
| `Flask-SocketIO` | >=5.3.0 | ❌ Удалить |
| `Flask` | >=3.1.2 | ❌ Удалить |
| `Werkzeug` | >=3.1.3 | ❌ Удалить |

### 4. Зависимости для добавления

| Пакет | Версия | Статус |
|-------|--------|--------|
| `fastapi` | >=0.111,<1.0 | ✅ Добавить |
| `uvicorn[standard]` | >=0.30,<1.0 | ✅ Добавить |
| `aiofiles` | >=23.1 | ✅ Уже есть (24.1.0) |
| `websockets` | >=12 | ✅ Уже есть (15.0.1) |
| `psutil` | >=5.9 | ✅ Уже есть (6.1.0) |

## 📊 Анализ структуры проекта

### Текущие WebSocket пути
- `/ws/stream` - основной WebSocket endpoint
- `/ws/status` - статус WebSocket Hub
- `/ws/stats` - статистика WebSocket
- `/ws/health` - здоровье Reactor

### Фронтенд интеграция
- CDN Socket.IO: `https://cdn.socket.io/4.7.5/socket.io.min.js`
- Reactor клиент: `static/js/reactor.js`
- React интеграция: `frontend/src/components/ReactorProvider.jsx`

## 🎯 План миграции

### Этап 1: Очистка зависимостей
- Удалить Flask-SocketIO, Flask, Werkzeug из requirements.txt
- Добавить FastAPI, Uvicorn
- Проверить совместимость

### Этап 2: Backend миграция
- Заменить `routes/ws_routes.py` на FastAPI WebSocket
- Обновить `webapp.py` для FastAPI
- Интегрировать с Reactor

### Этап 3: Frontend миграция
- Заменить Socket.IO на чистый WebSocket в `static/js/reactor.js`
- Обновить React компонент
- Удалить CDN зависимости

### Этап 4: Тестирование
- Создать тесты для WebSocket
- Проверить интеграцию с Reactor
- Валидировать фронтенд

## ⚠️ Риски и предосторожности

### Высокий риск
- Потеря существующих WebSocket соединений
- Нарушение фронтенд функциональности
- Проблемы с CORS и прокси

### Средний риск
- Изменение API для Reactor событий
- Несовместимость с существующими шаблонами

### Низкий риск
- Изменение структуры проекта (минимальное)
- Проблемы с зависимостями (контролируемые)

## 🔧 Технические детали

### Текущая архитектура
```
Flask App → Flask-SocketIO → Socket.IO Protocol → Frontend
```

### Целевая архитектура
```
FastAPI App → Native WebSocket → WebSocket Protocol → Frontend
```

### Совместимость
- WebSocket путь `/ws/stream` остается неизменным
- Reactor API не изменяется
- Frontend события остаются совместимыми

## ✅ Критерии успеха

1. **Отсутствие Flask-SocketIO** в коде и зависимостях
2. **Рабочий WebSocket** на `/ws/stream` с FastAPI
3. **Совместимость фронтенда** с чистым WebSocket
4. **Сохранение функциональности** Reactor
5. **Зеленые тесты** и линтеры

## 📝 Следующие шаги

1. Создать бэкап текущего состояния
2. Выполнить миграцию по этапам
3. Провести тестирование
4. Документировать изменения

---

**Статус:** Готов к миграции  
**Риск:** Средний (контролируемый)  
**Время:** ~2-3 часа
