# 📝 TASKS (last updated: 2025-10-01 14:26:32)

_Last updated: 2025-09-30 16:30:00_

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

## Current Tasks

### Data Model Refinement 🟡
**Priority:** 🟡  
**Context:**  
Уточнить модель данных для NewsItem и EventItem, особенно обработку published_at как datetime.

**Subtasks:**
- [ ] Проверить корректность парсинга ISO 8601 дат в Pydantic моделях
- [ ] Убедиться, что published_at_fmt и event_time_fmt работают правильно
- [ ] Добавить валидацию для edge cases (некорректные даты, null значения)

**Acceptance Criteria:**
- Все даты корректно парсятся и форматируются
- Нет ошибок валидации в тестах
- Fallback для некорректных дат работает

---

### Test Coverage Enhancement 🟡
**Priority:** 🟡  
**Context:**  
Доработать тесты: покрыть кейсы с пустыми данными и ошибками Supabase.

**Subtasks:**
- [ ] Добавить тесты для пустых результатов из Supabase
- [ ] Покрыть кейсы ошибок подключения к базе данных
- [ ] Добавить тесты для edge cases в репозиториях
- [ ] Улучшить моки для интеграционных тестов

**Acceptance Criteria:**
- Покрытие тестами > 80%
- Все edge cases покрыты
- Интеграционные тесты стабильны

---

### Documentation Final Review 🟢
**Priority:** 🟢  
**Context:**  
Пройтись по всем .md файлам ещё раз для финальной проверки.

**Subtasks:**
- [ ] Проверить актуальность всех ссылок
- [ ] Убедиться в консистентности стиля
- [ ] Проверить корректность TOC во всех файлах
- [ ] Обновить примеры кода, если нужно

**Acceptance Criteria:**
- Все ссылки работают
- Стиль единообразен
- TOC корректны

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
- ✅ 2025-09-27-30 — Days 4-6 (Architecture Refactoring) — Pydantic models, centralized services, repositories