# 📝 TASKS (last updated: 2025-10-04 18:50:50)

_Last updated: 2025-10-04 18:00:00_

## Table of Contents

- [Priority Legend](#priority-legend)
- [Completed Days](#completed-days)
- [Current Tasks](#current-tasks)
- [Backlog](#backlog)
- [Change History](#change-history)

## Priority Legend

- 🔴 Urgent (blocks work)
- 🟡 Important (should be done in coming days)
- 🟢 Can be postponed

## Task Template

### [Task Title]
**Priority:** 🔴/🟡/🟢  
**Context (why):**  
Brief explanation of why the task is needed.

**Subtasks:**
- [ ] step 1
- [ ] step 2

**Acceptance Criteria:**
- Condition 1
- Condition 2

**Related Decisions:** (link to Decision History in MASTER_FILE.md)

---

## Completed Days

### Day 01 — Docs + Parsers + CI ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Prepare basic documentation, fix parsers, and connect CI.

**Completed:**
- Written `README.md`, `VISION.md`, `ARCHITECTURE.md`, `ROADMAP.md`
- Added RSS parser (`rss_parser.py`)
- Added events parser (`events_parser.py`)
- Set up CI (pytest)

**Acceptance Criteria:**  
- ✅ Documentation exists
- ✅ Parsers work
- ✅ Tests run in CI

---

### Day 02 — Sources and Data Cleaning ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Expand sources, clean data, fight duplicates, improve utilities.

**Completed:**
- Added new sources (CoinDesk, Cointelegraph, Bloomberg, TechCrunch, etc.)
- Removed problematic sources (Axios, Reuters)
- Moved HTML cleaning to `utils/clean_text.py`
- Added duplicate filter (`make_uid`)
- Added parser tests
- Created `tools/show_news.py` for viewing news
- Updated `README.md`, `DEPLOY.md`, `ARCHITECTURE.md` (Mermaid diagram)

**Acceptance Criteria:**  
- ✅ No duplicates in DB
- ✅ Tests pass
- ✅ Documentation updated

---

### Day 03 — AI + Events + Telegram ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Added Telegram bot, AI digest, Investing events.

**Completed:**
- Added Telegram bot (`telegram_bot/`) on aiogram
- Handlers `/start`, `/digest`, `/digest_ai`, `/events`
- Inline navigation: main menu, AI digest categories, "Back" button
- News and events formatting (emoji, credibility/importance metrics, summary)
- AI digest by categories for current day
- Investing integration (events) → `tools/fetch_and_store_events.py`
- Fixed `db_models.py` (title fallback, get_latest_events)
- Enhanced `ai_summary.py` (prompt, bug fixes)
- Updated DEPLOY.md (added bot deployment)

**Acceptance Criteria:**
- ✅ Bot starts, all commands work
- ✅ News, events, AI digest display with buttons
- ✅ Webapp + ETL stable

---

### Day 04 — AI Digests Enhancement ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Improve AI digests with category selection, period options, and better formatting.

**Completed:**
- Added category and period selection (today/7d/30d) for AI digests
- Fixed digest formatting issues in Telegram
- Updated prompts for FT/WSJ-style article generation
- Added HTML formatting for Telegram
- Fixed flake8 errors and removed duplicate functions
- Unified datetime handling with UTC normalization

**Acceptance Criteria:**
- ✅ AI digests work with category and period selection
- ✅ Formatting issues resolved
- ✅ Code cleaned and linted

---

### Day 05 — Prompts Refactoring + Tests ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Refactor prompts into separate modules and add comprehensive test coverage.

**Completed:**
- Extracted prompts and clean_for_telegram into separate modules
- Added tests for new modules
- Enhanced generator tests
- Fixed AI module errors in ai_digest handler
- Updated setup.cfg configuration
- Stabilized all tests with unit/integration markers

**Acceptance Criteria:**
- ✅ Prompts refactored into separate modules
- ✅ All tests pass with proper markers
- ✅ Code is clean and maintainable

---

### Day 06 — Architecture Refactoring + Documentation ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Complete refactoring to Pydantic models, centralized services, and comprehensive documentation update.

**Completed:**
- Refactored to **Pydantic models** (`NewsItem`, `EventItem`) with proper datetime handling
- Added **repositories layer** (`news_repository.py`, `events_repository.py`) for data access
- Implemented **services layer** (`digest_service.py`, `digest_ai_service.py`) for business logic
- Created **DigestAIService** — centralized service for both regular and AI digests
- Fixed **Telegram bot** callback query timeout errors and "message not modified" issues
- Updated **tests** to work with new architecture using proper mocking
- Added **Makefile** with development commands (`run-bot`, `run-web`, `test`, `lint`)
- **Complete documentation overhaul** — updated all .md files with consistent style and TOC
- Used **Cursor AI** for automated refactoring and code improvements

**Acceptance Criteria:**
- ✅ All tests pass with new architecture
- ✅ Telegram bot works without errors
- ✅ Documentation is clean and consistent
- ✅ Architecture is maintainable and scalable

---

### Day 07 — Digest System Refactoring + Date Handling + Test Coverage + UX Enhancement ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Complete refactoring of digest system, proper datetime handling, comprehensive test coverage with async support, and enhanced UX with progress animation.

**Completed:**
- **Refactor**: вынесена логика в `DigestAIService`, упрощён `generator.py`, 
  добавлен shim `digest_service.py`
- **Dates**: `published_at` переведён в `datetime/timestamptz`, добавлен 
  `utils/formatters.format_date`, обновлены модели и шаблоны
- **Tests**: переписаны `test_digests.py`, `test_generator.py`, создан `test_ai_service.py`; 
  покрыты позитивные, негативные и edge cases; async-тесты работают 
  через `pytest-asyncio`; CI зелёный
- **Architecture**: создан `digests/ai_service.py` с централизованной AI-логикой
- **Database**: добавлена миграция для конвертации `published_at` в `timestamptz`
- **Formatting**: исправлено форматирование дат с ведущими нулями 
  (`%d` вместо `%-d`)
- **Documentation**: обновлены `README.md` с Quick Start и `ARCHITECTURE.md` 
  с диаграммой потоков данных
- **DevOps**: настроены make lint/format/test, pytest.ini с --maxfail=1, 
  GitHub Actions с make lint
- **UX Enhancement**: создана анимация прогресса с визуальным прогресс-баром, 
  мгновенная обратная связь, персонализированные результаты
- **Growth**: добавлены users/subscriptions/notifications, сервисы/хендлеры/клавиатуры, 
  исправлен upsert для дублирования ключей

**Acceptance Criteria:**
- ✅ Digest system uses centralized `DigestAIService`
- ✅ All dates properly handled as `datetime` objects
- ✅ Comprehensive test coverage with async support
- ✅ Enhanced UX with progress animation and action buttons
- ✅ Subscriptions and notifications system implemented
- ✅ All tests pass including edge cases
- ✅ Documentation updated with architecture diagrams

---

### Day 08 — WebApp Development + PWA Support ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Create modern WebApp with PWA support and clean UI.

**Completed:**
- Created webapp.html with tabbed dashboard interface
- Added Web App Manifest for PulseAI PWA support
- Enhanced navigation with Lucide icons
- Restored and updated style.css with PWA additions
- Fixed .env file loading and updated requirements.txt
- Restored all deleted files and organized project structure
- Final stabilization of all components

**Acceptance Criteria:**
- ✅ WebApp created with modern interface
- ✅ PWA support configured
- ✅ All components working stable

---

### Day 09 — Process Management + System Stabilization ✅ (Closed)
**Priority:** 🔴  
**Context:**  
Create process management system and stabilize all components.

**Completed:**
- Created Process Manager for automatic bot and WebApp startup
- Fixed WebApp port conflict issues, added make run-all/stop-all commands
- Improved Telegram bot Dashboard and AI-digest buttons, updated Cloudflare tunnel URL
- Fixed all failing tests, added automatic environment preparation
- Created port management system to prevent conflicts with automatic cleanup
- Cleaned documentation from temporary files, aligned with original plan

**Acceptance Criteria:**
- ✅ Process management system working
- ✅ All tests passing
- ✅ Documentation clean and organized

---

## Current Tasks

### Subscriptions Integration 🟡
**Priority:** 🟡  
**Context:**  
Интегрировать систему подписок и уведомлений с реальной логикой бота.

**Subtasks:**
- [ ] Подключить SubscriptionService к обработчикам подписок
- [ ] Реализовать автоматическую отправку дайджестов через tools/send_daily_digests.py
- [ ] Добавить cron-задачи для регулярных уведомлений
- [ ] Протестировать полный цикл: подписка → генерация → отправка

**Acceptance Criteria:**
- Пользователи могут подписываться на категории
- Автоматические дайджесты отправляются по расписанию
- Система уведомлений работает стабильно

---

### Performance Optimization 🟢
**Priority:** 🟢  
**Context:**  
Оптимизировать производительность системы для масштабирования.

**Subtasks:**
- [ ] Добавить кэширование для часто запрашиваемых данных
- [ ] Оптимизировать запросы к Supabase
- [ ] Реализовать rate limiting для Telegram API
- [ ] Добавить мониторинг производительности

**Acceptance Criteria:**
- Система выдерживает высокую нагрузку
- Время ответа бота < 2 секунд
- Нет утечек памяти

### Documentation Cleanup
**Priority:** 🟡  
**Context:**  
Bring all documentation to consistent style and structure.

**Subtasks:**
- [x] Update README.md with proper structure and TOC
- [x] Update CODEMAP.md with organized sections
- [ ] Update MASTER_FILE.md with clean structure
- [ ] Update docs/ files with consistent formatting
- [ ] Add TOC to files with more than 3 headings

**Acceptance Criteria:**
- All .md files follow consistent style
- TOC present in large files
- No duplicates or outdated information

---

### Test Coverage Expansion
**Priority:** 🟡  
**Context:**  
Increase stability of ETL and AI modules.

**Subtasks:**
- [ ] Tests for ETL: date normalization, upsert in DB without duplicates
- [ ] Tests for AI modules: `importance`, `credibility`
- [ ] Mark integration tests and exclude from CI

**Acceptance Criteria:**  
- Key modules coverage increased (ETL and AI modules covered by tests)
- Integration tests can be run with separate marker

---

### Topic Filter Implementation
**Priority:** 🟡  
**Context:**  
Allow users to form personalized digests.

**Subtasks:**
- [ ] Extend DB model (topics table)
- [ ] Add topic selection in config/sources.yaml
- [ ] Add filter in webapp.py

**Acceptance Criteria:**
- Topic selection available in webapp
- Only topic-related news appear in digest

---

## Backlog

### Events Calendar Enhancement
**Priority:** 🟡  
**Context:**  
Events should have priorities for analytics and display.

**Subtasks:**
- [ ] Extend `events` model in DB (priority field)
- [ ] Display priority badge in webapp

**Current Status:**  
- ✅ Investing events parsing works
- ⏳ Priorities/badges not yet implemented

---

### Logging and Configuration
**Priority:** 🟡  
**Context:**  
Unified log format for parsers/DB and reduce noise.

**Subtasks:**
- [ ] Centralize named loggers parsers.rss / parsers.events / database
- [ ] Add ability to control log levels from config/logging.yaml

---

### Telegram Bot Notifications
**Priority:** 🟢  
**Context:**  
Deliver digests and events directly to Telegram.

**Subtasks:**
- [x] Write bot on aiogram/pyTelegramBotAPI
- [x] Connect to DB (digest retrieval)
- [ ] Test notifications

---

### White-label Integrations for Media
**Priority:** 🟢  
**Context:**  
Give media ready solution for embedding digests.

**Subtasks:**
- [ ] Define API/export format
- [ ] Create white-label frontend template

---

### Automatic Digests
**Priority:** 🟢  
**Context:**  
Digests should arrive automatically morning/evening.

**Subtasks:**
- [ ] Set up cron (morning and evening)
- [ ] Add auto-generation option in webapp

---

## Change History

- ✅ 2025-09-23 — Monetization documented in README.md
- ✅ 2025-09-24 — Day 1 closed
- ✅ 2025-09-25 — Day 2 closed (sources, cleaning, tests, utilities, documentation)
- ✅ 2025-09-26 — Day 3 (AI + Events + Telegram) — added Telegram bot, AI digest, Investing events
- ✅ 2025-09-27 — Day 4 closed (AI digests enhancement, formatting fixes)
- ✅ 2025-09-28 — Day 5 closed (prompts refactoring, tests coverage)
- ✅ 2025-09-30 — Day 6 closed (architecture refactoring, Pydantic models, centralized services)
- ✅ 2025-10-01 — Day 7 closed (DigestAIService, date handling, tests, UX enhancement, subscriptions)
- ✅ 2025-10-02 — Day 8 closed (WebApp development, PWA support)
- ✅ 2025-10-04 — Day 9 closed (process management, system stabilization, documentation cleanup)