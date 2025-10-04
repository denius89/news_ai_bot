# PulseAI — Master Development Log

This file contains the master rules, architecture, and agreements for the PulseAI project.  
This is the main document for developers and project participants.

## Table of Contents

- [Project Rules](#project-rules)
- [Architecture Decisions](#architecture-decisions)
- [Database Schema](#database-schema)
- [Logging System](#logging-system)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Technology Stack](#technology-stack)
- [Development History](#development-history)
- [Future Tasks](#future-tasks)

## Project Rules

- Git: commit/push after each step
- Tasks: tracked in TASKS.md with priorities 🔴/🟡/🟢
- Decisions and agreements are documented here
- Documentation: English for technical docs, Russian for product descriptions

---

## Architecture Decisions

### Day 01: Parsers and Database
- `rss_parser.py`/`events_parser.py`: unified data format
- `db_models.py`: verified unique keys, indexes, INFO-level logging

### Day 02: Sources and Data Cleaning
- **Sources**: Removed Axios (no stable RSS) and temporarily excluded Reuters (DNS/availability issues)
- **New RSS sources**: CoinDesk, Cointelegraph, Bloomberg Markets, TechCrunch
- **Text cleaning**: moved to `utils/clean_text.py` (unified preprocessing)
- **Deduplication**: `uid = sha256(url|title)`, `upsert` by `uid` to eliminate duplicates
- **Utilities**: added `tools/show_news.py` for viewing latest news from DB
- **Constants**: `COUNTRY_MAP`, categories, and tags moved to `config/constants.py`

### Technical Details
- MIME validation for RSS (`requests` → `Content-Type` header must contain `xml`/`rss`)
- Date normalization: `dateutil` → UTC (`astimezone(timezone.utc)`)
- HTML cleaning: BeautifulSoup → `.get_text()`, whitespace normalization
- Duplicate filtering at parser level (in-memory `seen`) + DB level (`on_conflict="uid"`)
- Logging: named loggers `parsers.rss`, `parsers.events`, `database`

### Results
- No duplicates in `news` table
- Stable parsing: problematic sources disabled/replaced
- Parser and utility tests passing


## Database Schema

Project uses **Supabase (PostgreSQL)** instead of local SQLite.

### `news` Table (Primary)

| Field         | Type         | Description |
|---------------|--------------|-------------|
| uid           | text (PK)    | Unique identifier `sha256(url|title)` |
| title         | text         | News headline |
| link          | text         | Source link |
| published_at  | timestamptz  | Publication date/time (UTC) |
| content       | text         | News content (if available) |
| credibility   | numeric      | Credibility score (AI) |
| importance    | numeric      | Importance score (AI) |
| source        | text         | Source name (from configuration) |
| category      | text         | Category (crypto, economy, world, tech, etc.) |

**Features**  
`upsert_news` function saves news by unique `uid = sha256(url|title)`.  
Insertion happens via `upsert` with `on_conflict="uid"`.

### `events` Table

| Field        | Type         | Description |
|--------------|--------------|-------------|
| id           | uuid (PK)    | Unique identifier |
| title        | text         | Event name |
| country      | text         | Country code (e.g., `US`) |
| currency     | text         | Currency (e.g., `USD`) |
| importance   | int          | Importance (1 = low, 2 = medium, 3 = high) |
| event_time   | timestamptz  | Event time in UTC |
| fact         | text         | Actual value |
| forecast     | text         | Forecast |
| previous     | text         | Previous value |

**Features**
- `importance` stored as **int (1–3)**
- When parsing Investing, `low/medium/high` values converted to numbers via `IMPORTANCE_TO_PRIORITY`
- Enables unified storage and filtering in Telegram bot

### Additional Tables
- **users** — users (e.g., for future Telegram bot integration)
  Fields: `telegram_id`, `created_at`
- **digests** — user digests (future)
  Fields: `summary`, `created_at`

### Key Features
- `upsert_news` function saves news by unique `uid = sha256(url|title)`
- Insertion via `upsert` with `on_conflict="uid"`
- Dates normalized to **UTC**
- `content` field can be `NULL` if missing
- AI scores (`credibility`, `importance`) saved when inserting news and events
- Tables created via Supabase or local SQL scripts (`database/init_tables.sql`, `seed_data.sql`)   

## Logging System

Project uses standard Python `logging` module with centralized initialization in `utils/logging_setup.py`. Log level configuration planned via `config/logging.yaml`.

### Main Features
- Logs written **simultaneously to console and file** `logs/app.log`
- **File rotation**: when reaching certain size, old logs saved with suffix (`app.log.1`, `app.log.2`, etc.)
- Log format: `YYYY-MM-DD HH:MM:SS,mmm [LEVEL] Message`

### Additional Log Information
- List of used sources (`name`, `category`, `url`)
- Number of news loaded from each source
- Total number of saved news

### Example
```
2025-09-18 17:36:52,841 [INFO] Loading news from 24 sources (all)...
    2025-09-18 17:36:52,842 [INFO]   CoinDesk (crypto): https://www.coindesk.com/arc/outboundfeeds/rss/
    2025-09-18 17:36:52,843 [INFO]   BBC World (world): http://feeds.bbci.co.uk/news/world/rss.xml
2025-09-18 17:36:53,012 [INFO] Retrieved 50 news items. Writing to database...
```

### Where to Check
- **Console** — quick view during development
- **logs/app.log** — history for debugging (with rotation)

> ⚠️ `logs/` folder added to `.gitignore` to prevent logs from entering repository
## Development Workflow

### Main Script `main.py`
Runs news loading and saving process (ETL) or digest generation.

**Examples:**
```bash
# All sources, max 20 news from each (up to 480 total), then general slice of 100
python main.py --source all --per-source-limit 20 --limit 100

# Only crypto, 20 news from each source in category
python main.py --source crypto --per-source-limit 20

# Only economy, total up to 10 news
python main.py --source economy --limit 10

# Generate digest of last 5 news
python main.py --digest 5

# Generate digest using AI
python main.py --digest 5 --ai
```

**Parameters:**
- `--source` — source set: `all` | `crypto` | `economy` | `world` | `technology` | `politics`
- `--per-source-limit` — max news loaded from **each source** (default 20)
- `--limit` — total max news per run (top slice after combining all sources)
- `--digest` — generate text digest (default 5 news)
- `--ai` — use AI for digest generation (instead of simple list)  

### Utility `tools/show_news.py`
Displays latest news from database for verification.

**Example:**
```bash
python tools/show_news.py --limit 5
```

---

### Utility `tools/fix_old_news.py`
Used for fixing old database records:

- Adds `source` field if missing
- Updates empty `content` if description appears
- Can work selectively via flags (e.g., only for missing sources)

**Example:**
```bash
python tools/fix_old_news.py --mode fill-missing
```

### Git Rules
- Main branch: `main`
- New features: `feature/<name>`
- Bug fixes: `fix/<name>`
- Documentation updates: `docs/<name>`
- After adding code always:
  ```bash
  git add .
  git commit -m "type: description"
  git push
  ```

### Code Review Rules (GALLOP)
1. Goal — purpose of change
2. Action — what we're changing
3. Location — where (file/module)
4. Logic — why
5. Output — what should result
6. Push — don't forget git add . && git commit && git push

---

## Technology Stack

- **Python 3.11+** — main development language
- **Flask** — web framework for WebApp
- **Supabase (PostgreSQL)** — cloud database instead of local SQLite
- **OpenAI API (GPT-4o-mini)** — for analysis, annotations, and AI scores
- **Requests, Feedparser, BeautifulSoup** — for RSS/HTML loading and parsing
- **PyYAML** — source configurations (`config/sources.yaml`)
- **Logging (RotatingFileHandler)** — unified log collection to console and file
- **Jinja2** (via Flask) — template engine for UI (pages /digest, /events)
- **Custom CSS** — custom styles with light/dark theme adaptation and mobile devices
- **aiogram 3.x** — Telegram bot framework
- **Pydantic** — data validation and models
- Ability to connect **new news sources** via `sources.yaml`



## Development History

### ✅ Day 01 (24.09.2025)
- Added `CONTRIBUTING.md`, `.editorconfig`, `pyproject.toml`
- Set up CI: flake8, black, pytest, coverage, isort, mypy
- Fixed tests (`ai_modules`, `supabase`, `openai`, `digests`, `parsers`)
- Added helper tests (`test_main_import`, `test_routes`, `test_webapp`)
- Added `tools/fetch_and_store_events.py` and `tools/show_latest_news.py`
- Fixed `repo_map.py`, now correctly generates `CODEMAP.md`
- Auto-formatting black/isort across entire project
- CI passing: both badges (`main` and `day-01-docs-parsers`) — passing
- Result: Day 01 completed

### ✅ Day 02 (25.09.2025)
- Removed Axios (no stable RSS) and temporarily excluded Reuters
- Added new RSS sources (CoinDesk, Cointelegraph, Bloomberg Markets, TechCrunch, etc.)
- Moved text cleaning to `utils/clean_text.py`
- Implemented dedup (`uid = sha256(url|title)`, upsert by `uid`)
- Added `tools/show_news.py` for viewing news
- Moved `COUNTRY_MAP`, categories, and tags to `config/constants.py`
- Updated `README.md`, `docs/DEPLOY.md`, `docs/ARCHITECTURE.md` (Mermaid diagram)
- Result: Day 02 completed

### ✅ Day 03 (26.09.2025)
- Added Telegram bot (aiogram 3.x): handlers `/start`, `/digest`, `/digest_ai`, `/events`
- Main menu and navigation via inline buttons (back, categories)
- News and events formatting (emoji, Credibility, Importance, summary)
- Implemented AI digest by categories for the day
- Added fallback for `title` in `db_models.py`, improved `get_latest_events`
- Enhanced `ai_summary.py`: fixed prompt, removed style errors
- Added Investing parser to pipeline (`tools/fetch_and_store_events.py`)
- Updated `DEPLOY.md` (bot deployment) and `README.md` (Telegram section)
- Result: Day 03 completed
- Added **inline keyboards** to Telegram bot:
  - `start_inline_keyboard` — first button «🚀 Start»
  - `main_inline_keyboard` — main menu (📰 News, 🤖 AI Digest, 📅 Events)
  - `back_inline_keyboard` — return to menu
- Architectural decision: bot works entirely through inline navigation, without ReplyKeyboard
- Bot now integrated into project pipeline (manual command testing, CI doesn't run yet)

### ✅ Day 04 (27.09.2025)
- **Улучшение AI-дайджестов** — добавлен выбор категории и периода (сегодня/7д/30д)
- **Фиксы форматирования** — исправлено отображение дайджестов в Telegram
- **Обновление промтов** — улучшены промты для генерации статейного дайджеста в стиле FT/WSJ
- **HTML форматирование** — добавлено HTML форматирование для Telegram
- **Очистка кода** — исправлены flake8 ошибки, удалены дублирующие функции
- **Нормализация дат** — унифицирована обработка datetime с UTC
- Result: Day 04 completed — AI-дайджесты улучшены, код очищен

### ✅ Day 05 (28.09.2025)
- **Рефакторинг промтов** — вынесены промты и clean_for_telegram в отдельные модули
- **Добавлены тесты** — покрытие тестами новых модулей
- **Улучшение генератора** — добавлены тесты для generator.py
- **Фиксы AI-модулей** — исправлены ошибки в ai_digest handler
- **Обновление конфигурации** — исправлен setup.cfg
- **Стабилизация тестов** — все тесты проходят стабильно с unit/integration маркерами
- Result: Day 05 completed — код рефакторинг завершен, тесты стабилизированы

### ✅ Day 06 (30.09.2025)
- **Рефакторинг архитектуры** — переход на Pydantic модели и централизованные сервисы
- **Новые слои** — добавлены `repositories/` и `services/` для разделения ответственности
- **DigestAIService** — централизованный сервис для генерации дайджестов (обычных и AI)
- **Обновление Telegram бота** — исправлены ошибки timeout и "message not modified"
- **Улучшение тестов** — обновлены тесты для работы с новой архитектурой
- **Makefile** — добавлены команды для разработки (`run-bot`, `run-web`, `test`, `lint`)
- **Документация** — полная ревизия всех .md файлов с единым стилем и TOC
- **Использование Cursor** — автоматизация рефакторинга с помощью AI-ассистента
- Result: Day 06 completed — архитектура стабилизирована, документация приведена в порядок

### ✅ Day 07 (01.10.2025)
- **Рефакторинг системы дайджестов** — вынесена логика в `DigestAIService`, упрощён `generator.py`
- **Обработка дат** — `published_at` переведён в `datetime/timestamptz`, добавлен `utils/formatters.format_date`
- **Покрытие тестами** — переписаны `test_digests.py`, `test_generator.py`, создан `test_ai_service.py`
- **Async-тесты** — покрыты позитивные, негативные и edge cases; async-тесты работают через `pytest-asyncio`
- **UX Enhancement** — создана анимация прогресса с визуальным прогресс-баром
- **Система подписок** — добавлены users/subscriptions/notifications, сервисы/хендлеры/клавиатуры
- **CI стабилизация** — CI зелёный, настроены make lint/format/test, pytest.ini с --maxfail=1
- Result: Day 07 completed — система дайджестов рефакторена, тесты покрывают все сценарии

### ✅ Day 08 (02.10.2025)
- **WebApp разработка** — создан webapp.html с tabbed dashboard interface
- **PWA поддержка** — добавлен Web App Manifest для PulseAI
- **Улучшение навигации** — добавлены Lucide icons и улучшенная навигация
- **Обновление стилей** — восстановлен style.css с PWA дополнениями
- **Фиксы .env** — исправлена загрузка .env файла и обновлен requirements.txt
- **Восстановление файлов** — восстановлены все удаленные файлы и наведен порядок
- **Финальная стабилизация** — исправлены все проблемы, наведен порядок в проекте
- Result: Day 08 completed — WebApp создан, PWA настроен, все компоненты стабилизированы

### ✅ Day 09 (04.10.2025)
- **Система управления процессами** — создан Process Manager для автоматического запуска бота и WebApp
- **Исправление WebApp** — решена проблема с занятым портом 8001, добавлены команды `make run-all`, `make stop-all`
- **Улучшение Telegram бота** — исправлены кнопки Dashboard и AI-дайджест, обновлен URL на новый Cloudflare tunnel
- **Система тестирования** — исправлены все упавшие тесты, добавлена автоматическая подготовка окружения
- **Управление портами** — создана система предотвращения конфликтов портов с автоматическим освобождением
- **Документация** — очищена от временных файлов, приведена в соответствие с изначальным планом
- Result: Day 09 completed — система стабилизирована, все компоненты работают стабильно

## Current Status

### ✅ Completed Components
- **News Parser** — работает, собирает новости из RSS
- **Database** — настроена, таблицы созданы
- **AI Summary** — работает, генерирует дайджесты
- **Digest Generator** — работает, создает HTML дайджесты
- **Events Fetcher** — работает, собирает события
- **WebApp** — полностью работает, исправлены проблемы с портами
- **Telegram Bot** — полностью работает, исправлены кнопки Dashboard и AI-дайджест
- **Testing** — все тесты проходят, исправлены упавшие тесты
- **Documentation** — очищена от временных файлов, приведена в порядок
- **Process Management** — создана система автоматического управления процессами

### 🚧 In Progress
- **Deployment** — подготовка к продакшн развертыванию
- **Monitoring** — планирование системы мониторинга

### ❌ Not Started
- **Analytics** — аналитика использования
- **Advanced Features** — расширенная функциональность

## Future Tasks

1. Expand news parser:
   - Save not only `title` and `link`, but also `summary`/`content`
2. Add web interface (admin panel / webapp) for viewing news and calendar
3. Implement events calendar with importance scoring
4. Connect GitHub Actions (CI):
   - Create `.github/workflows/ci.yml`
   - Store `SUPABASE_URL` and `SUPABASE_KEY` in GitHub Secrets
   - Add "CI passing" badge to `README.md`

## Task Context
Briefly document "why" we're doing a task to avoid losing logic.  
Example: "Topic filter needed to form personalized digests"

## Communication Rules
- You are the project architect (set tasks, approve decisions)
- I am the assistant (clarify tasks, format checklists, remind about git)
- Task priorities: 🔴 urgent, 🟡 soon, 🟢 can be postponed
- Work cycle:  
  1. Task → 2. Clarification → 3. Checklist → 4. Git commit → 5. Summary in TASKS.md

## Checklist Format
- Each task formatted as card:
  - Title
  - Priority
  - Context (why)
  - Subtasks (checklist)
  - Acceptance criteria  
