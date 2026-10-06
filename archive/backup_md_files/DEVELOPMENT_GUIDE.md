# 🚀 PulseAI Development Guide

## 📋 **Быстрый старт**

```bash
# Запустить все сервисы
make start

# Проверить статус
make status

# Остановить все сервисы
make stop
```

## 🎯 **Схема портов**

| Сервис | Порт | URL | Назначение |
|--------|------|-----|------------|
| **React Frontend** | `3000` | `http://localhost:3000/webapp` | Основной фронтенд |
| **Flask API** | `8001` | `http://localhost:8001` | API для новостей |
| **FastAPI** | `8000` | `http://localhost:8000` | Резервный бэкенд |

## 🛠 **Команды Makefile**

### Основные команды:
```bash
make help          # Показать справку
make start         # Запустить все сервисы
make stop          # Остановить все сервисы
make restart       # Перезапустить все сервисы
make status        # Показать статус сервисов
```

### Проверка портов:
```bash
make check-ports   # Проверить все порты
make clean         # Очистить все процессы и порты
```

### Индивидуальные сервисы:
```bash
make react         # Только React (порт 3000)
make flask         # Только Flask API (порт 8001)
make bot           # Только Telegram Bot
```

### Логи и мониторинг:
```bash
make logs          # Показать логи всех сервисов
make logs-react    # Логи React (follow)
make logs-flask    # Логи Flask (follow)
make logs-bot      # Логи Bot (follow)
```

### Тестирование:
```bash
make test          # Тестировать все сервисы
make test-api      # Тестировать API
make test-react    # Тестировать React
```

### Разработка:
```bash
make install       # Установить зависимости
make dev           # Установить и запустить
```

## 🔧 **Решение конфликтов**

### ❌ **Старая проблема:**
- Flask и React конфликтовали за порты
- Неясно какой сервис на каком порту
- Сложно управлять процессами

### ✅ **Новое решение:**
- **Четкое разделение ролей:**
  - React ТОЛЬКО на 3000 - фронтенд
  - Flask ТОЛЬКО на 8001 - API
- **Автоматическая проверка портов**
- **Централизованное управление через Makefile**

## 📁 **Структура файлов**

```
├── Makefile              # 🎯 Основные команды
├── PORTS.md              # 📋 Схема портов
├── DEVELOPMENT_GUIDE.md  # 📖 Этот файл
├── logs/                 # 📝 Логи сервисов
│   ├── react.log
│   ├── flask.log
│   ├── bot.log
│   ├── react.pid
│   ├── flask.pid
│   └── bot.pid
├── webapp/               # ⚛️ React приложение
│   └── vite.config.ts    # Порт 3000, proxy на 8001
├── webapp.py             # 🐍 Flask API
│   └── Порт 8001, только API
└── main.py               # 🤖 Telegram Bot
```

## 🔄 **Workflow разработки**

### 1. **Начало работы:**
```bash
make clean    # Очистить все
make start    # Запустить сервисы
make status   # Проверить статус
```

### 2. **Разработка:**
```bash
make logs-react    # Смотреть логи React
make logs-flask    # Смотреть логи Flask
make test          # Тестировать изменения
```

### 3. **Отладка:**
```bash
make check-ports   # Проверить порты
make logs          # Показать все логи
curl http://localhost:3000/api/latest  # Тест API
```

### 4. **Завершение:**
```bash
make stop          # Остановить все
make clean         # Полная очистка
```

## 🚨 **Устранение неполадок**

### Порт занят:
```bash
make clean         # Убить все процессы
make check-ports   # Проверить порты
make start         # Запустить заново
```

### API не отвечает:
```bash
make logs-flask    # Проверить логи Flask
curl http://localhost:8001/api/health  # Тест API
```

### React не загружается:
```bash
make logs-react    # Проверить логи React
curl http://localhost:3000/webapp      # Тест React
```

### Конфликт процессов:
```bash
make stop          # Остановить все
ps aux | grep -E "(python|node)"  # Найти процессы
kill -9 <PID>      # Убить процесс
make start         # Запустить заново
```

## 🎯 **Telegram Bot интеграция**

### Настройка:
```python
# config/settings.py
WEBAPP_URL = "http://localhost:3000"  # Для локальной разработки
```

### Тестирование:
1. Запустить `make start`
2. Открыть Telegram Bot
3. Отправить `/dashboard`
4. Нажать кнопку "📱 Открыть Dashboard"
5. Должен открыться React на `http://localhost:3000/webapp`

## 🌐 **Production vs Development**

### Development (локально):
```bash
WEBAPP_URL=http://localhost:3000
make start
```

### Production (Cloudflare):
```bash
WEBAPP_URL=https://example.invalid
make start
```

## 📊 **Мониторинг**

### Статус сервисов:
```bash
make status
```

### Логи в реальном времени:
```bash
make logs-react &  # В одном терминале
make logs-flask &  # В другом терминале
```

### Проверка здоровья:
```bash
curl http://localhost:8001/api/health
curl http://localhost:3000/api/latest
```

## 🎉 **Результат**

✅ **Нет конфликтов портов**  
✅ **Простое управление сервисами**  
✅ **Автоматическая проверка портов**  
✅ **Централизованные логи**  
✅ **Четкое разделение ролей**  
✅ **Легкая отладка**  

**Теперь разработка стала намного проще! 🚀**
