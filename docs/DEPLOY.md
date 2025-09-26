# 🚀 Deploy Guide

Инструкция по локальному запуску и деплою PulseAI.

---

## 📦 Подготовка окружения

1. Клонировать репозиторий:
```bash
git clone https://github.com/denius89/news_ai_bot.git
cd news_ai_bot
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Создать файл `.env` на основе примера:
```bash
cp .env.example .env
```
Заполнить `SUPABASE_URL`, `SUPABASE_KEY` (и при необходимости `OPENAI_API_KEY`, `DEEPL_API_KEY`).

---

## ▶️ Запуск сервисов

### Flask webapp
```bash
python webapp.py
```
Доступно по адресу: [http://localhost:5000](http://localhost:5000).

### ETL новостей (RSS)
```bash
python -m tools.fetch_and_store_news --limit 20
```

### Просмотр новостей в CLI
```bash
python -m tools.show_news --limit 10
```

---

## 🧪 Тестирование

Быстрые тесты (без интеграции):
```bash
pytest -m "not integration"
```

Интеграционные тесты (с БД и API):
```bash
pytest -m integration
```

---

## 📅 Парсер событий

Для запуска парсинга экономического календаря:
```bash
python -m tools.fetch_and_store_events
```
События сохраняются в таблицу `events` в Supabase и отображаются в UI (таблица и карточки).

---

## 🤖 Telegram bot

Для запуска Telegram-бота:
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
python -m telegram_bot.bot
```

⚠️ Требуется наличие переменной окружения `TELEGRAM_BOT_TOKEN` в `.env`.
