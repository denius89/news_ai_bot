# PulseAI

![Tests – main](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
![Tests – day-01-docs-parsers](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=day-01-docs-parsers)
![Tests – day2-sources-cleaning](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=day2-sources-cleaning)
![Tests – day3-ai-events-telegram](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=day3-ai-events-telegram)


AI-платформа для превращения хаотичного потока новостей и событий в персональные дайджесты и умный календарь.

---

## ✨ Основные возможности (на текущем этапе)
- Сбор новостей из **RSS** (crypto, world, tech).  
- Парсинг экономического календаря (**Investing.com**).  
- Очистка текста и удаление дублей.  
- Автоматическая оценка **важности** и **достоверности**.  
- Сохранение в **Supabase**.  
- Просмотр новостей через webapp и `tools/show_news.py`.

---

## 📂 Структура проекта

Основные директории и файлы:

```text
├── ai_modules/        # AI-модули (credibility, importance)
├── config/            # настройки, константы, источники
├── database/          # работа с Supabase (db_models)
├── digests/           # генерация дайджестов (AI-summary, генератор)
├── docs/              # документация (ARCHITECTURE, ROADMAP, VISION, DEPLOY)
├── parsers/           # парсеры RSS и событий
├── routes/            # Flask-маршруты
├── tools/             # утилиты (fetch, show_news, фиксы)
├── tests/             # юнит- и интеграционные тесты
├── webapp.py          # Flask-приложение
└── main.py            # CLI-обработка новостей
```

## 🔜 В разработке
- Переводы материалов (DeepL API).  
- Формирование утренних и вечерних дайджестов.  
- Умный календарь ключевых событий.  

## 🚀 Quickstart

```bash
# Клонирование репозитория
git clone https://github.com/denius89/news_ai_bot.git
cd news_ai_bot

# (рекомендуется) Создание виртуального окружения
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Установка зависимостей
pip install -r requirements.txt

# Создание .env на основе примера
cp .env.example .env
# заполните SUPABASE_URL и SUPABASE_KEY
# (OPENAI_API_KEY, DEEPL_API_KEY — опционально, для будущих функций)

# Запуск сбора новостей (ETL)
python tools/fetch_and_store_news.py

# Просмотр последних новостей
python tools/show_news.py --limit 10

# Запуск сбора новостей (ETL)
python tools/fetch_and_store_news.py

# Просмотр последних новостей
python tools/show_news.py --limit 10

# Запуск webapp (Flask)
python webapp.py

# CLI (пример: собрать 20 новостей из всех источников)
python main.py --source all --limit 20
```

---

## ▶️ CLI-запуск

Запуск обработки новостей из предустановленных источников:

| Источник       | Пример запуска                                |
|----------------|-----------------------------------------------|
| Все            | `python main.py --source all --limit 20`      |
| Только crypto  | `python main.py --source crypto --limit 10`   |
| Только economy | `python main.py --source economy --limit 10`  |

### Параметры
- `--source` — набор источников: `all` | `crypto` | `economy`  
- `--limit`  — максимум новостей за прогон (по умолчанию берутся все)  

### Дополнительно
- Запуск webapp: `python webapp.py`  
- Просмотр последних новостей: `python tools/show_news.py --limit 10`  

---

## 🧪 Тестирование

Запуск тестов:

```bash
# быстрые тесты без интеграции
pytest -m "not integration"

# интеграционные тесты (работа с БД и API)
pytest -m integration
```
Перед пушем обязательно:
```bash
black .   # автоформатирование
flake8 .  # проверка стиля и ошибок
```
---

## 📰 Дайджесты

Можно собрать дайджест новостей прямо из базы.

### Обычный дайджест
Берём последние 5 новостей:
```bash
python main.py --digest 5
```
### AI-дайджест
То же самое, но с генерацией связного текста через OpenAI:
```bash
python main.py --digest 5 --ai
```
### Параметры
- `--digest N` — количество последних новостей для дайджеста  
- `--ai` — включить генерацию текста с помощью AI 

---

## 📅 Работа с событиями

PulseAI умеет собирать и хранить экономические и крипто-события (например, решения ФРС, релизы CPI, хардфорки блокчейнов).

- Источник: Investing.com (экономический календарь).
- Поля: `event_time`, `country`, `currency`, `title`, `importance (1–3)`, `fact`, `forecast`, `previous`, `source`.
- В БД события сохраняются в таблицу `events` с уникальным `event_id`.
- В UI события отображаются в виде таблицы (desktop) и карточек (mobile), с бейджами важности.

Запуск парсера:
```bash
python -m tools.fetch_and_store_events
```

---

## 🤖 Telegram bot (MVP)


PulseAI теперь доступен и в Telegram!
Бот реализован на **aiogram 3.x**, поддерживает inline-кнопки и навигацию.

### Команды
- `/start` — приветствие + кнопка «🚀 Старт».
- `/digest` — последние важные новости (с метриками Credibility/Importance).
- `/digest_ai` — выбор категории и генерация AI-дайджеста за день.
- `/events` — ближайшие события из экономического календаря.

### Навигация
- Главное меню: 📰 Новости, 🤖 AI-дайджест, 📅 События.
- Внутри разделов доступна кнопка ⬅️ «Назад» для возврата.
- AI-дайджест поддерживает выбор категории (Crypto, Economy, World, Technology, Politics).

### Запуск
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
python -m telegram_bot.bot
```
Требуется переменная окружения `TELEGRAM_BOT_TOKEN` в `.env`.

### Пример сценария
1. `/start` → кнопка «🚀 Старт».
2. Главное меню → выбираем «🤖 AI-дайджест».
3. Выбор категории → «📊 Crypto».
4. Получаем AI-дайджест за сегодня + кнопку «⬅️ Назад`.
---

## 📝 Пример логов

Ниже показан пример работы пайплайна при лимите `--limit 5`:

```text
2025-09-23 11:15:12 [INFO] news_ai_bot: Загружаем новости из crypto
2025-09-23 11:15:13 [INFO] news_ai_bot: Получено 5 новостей
2025-09-23 11:15:13 [INFO] news_ai_bot: ✅ Добавлено 5 новостей в базу
```
---
      
## 🧰 Используемый стек
- 🐍 **Python 3.11+**
- 🤖 **OpenAI API** — оценка достоверности и аналитика
- 🌍 **DeepL API** — переводы
- 🗄️ **Supabase (PostgreSQL + API)** — хранилище данных
- 🚀 **Render** — деплой webapp и фоновые задания (ETL)
- 🌐 **Flask** — web-интерфейс
- ✅ **Pytest** — тестирование и CI

---

## 🔄 Архитектура (визуально)
```mermaid
flowchart TD
    A["🌐 Источники: RSS, сайты, календари"] --> B["⚙️ Парсеры данных (rss_parser, events_parser, utils)"]
    B --> C["🤖 AI-модули анализа"]
    C --> D["🗄️ Supabase (PostgreSQL)"]
    D --> E["📰 Дайджесты (утро/вечер, AI-тексты)"]
    D --> F["📅 Календарь событий (macro+crypto)"]
    D --> G["🌐 Webapp + CLI (Flask + CLI для AI-текстов)"]
```
---

## 🗺 Дорожная карта

### ✅ Сделано
- Настроено окружение и репозиторий
- Подключены **OpenAI**, **DeepL** и **Supabase**
- Реализован **парсинг RSS** и сохранение новостей в базу
- Настроено централизованное **логирование**
- Добавлены базовые **тесты** (`pytest`)
- Подготовлен **MASTER_FILE.md** (структура, история решений)
- Настроены **git hooks** для `CODEMAP.md` и `TASKS.md`
- Реализован модуль **дайджестов** (CLI-флаг `--digest`, AI-генерация текста)

---

### 🔜 Ближайшие шаги (Week 1–2)
- 📄 Ревизия документации (`MASTER_FILE.md`, `README.md`, `TASKS.md`)
- 🧪 Расширение тестов (ETL и AI-модули)
- 🗂 Добавление **фильтра по темам**
- 📅 Поддержка **календаря событий** с приоритетами
- 🌐 Добавление новых источников (crypto + economy)

---

### 🚀 В перспективе (Month+)
- 🤖 **Telegram-бот** и WebUI
- 📰 White-label интеграции для медиа
- ⏰ Автоматические дайджесты (утро/вечер)
- ⚙️ CI через GitHub Actions (полный прогон тестов + форматирование)
- 📊 Улучшенные **AI-аналитические отчёты**

---

## 💰 Монетизация

Возможные модели монетизации проекта:

1. **Подписка SaaS (B2C)**
   - Базовый доступ к новостям и дайджестам бесплатный.
   - Расширенный тариф: AI-анализ, персонализация, сохранённые фильтры, дополнительные источники.

2. **B2B API**
   - Доступ к API новостей и событий с AI-оценкой достоверности и важности.
   - Тарифы по количеству запросов (news as a service).

3. **White-label решения**
   - Готовые виджеты/фиды для медиа, брокеров, финтеха.
   - Возможность интеграции под бренд клиента.

4. **Telegram-бот (Freemium)**
   - Бесплатный базовый бот: новости и дайджесты.
   - Премиум-подписка: персонализация, AI-аналитика, календарь событий, интеграция с другими платформами.

5. **Партнёрские интеграции**
   - Встраивание в финтех/криптосервисы (например, трейдинг-приложения).
   - Revenue share или referral-модель.

---

## 📌 Статус проекта
MVP в активной разработке. Фокус — минимальные затраты и рабочий прототип.

---

## 📫 Контакты

Автор: [@denius89](https://github.com/denius89)  
Лицензия: [MIT](https://github.com/denius89/news_ai_bot/blob/main/LICENSE)