# PulseAI Development Roadmap

PulseAI — **AI-Driven News & Events Platform** that transforms chaotic news and events streams into personalized digests, smart calendars, and automated content management for Telegram and WebApp.

## Table of Contents

- [Completed Days](#completed-days)
- [Current Week](#current-week)
- [Upcoming Weeks](#upcoming-weeks)
- [Backlog](#backlog)

## Completed Days

### ✅ Day 1 — Documentation & Parser Review
- Created: `VISION.md`, `ROADMAP.md`, `COMMUNICATION.md`
- Reviewed parsers (`rss_parser.py`, `events_parser.py`)
- CI setup (`.github/workflows/tests.yml`)
- Verified `db_models.py` and logging
- Test run: sources → DB

### ✅ Day 2 — Sources & Data Cleaning
- Added 2-3 new sources to `config/sources.yaml`
- Fixed parsing of problematic RSS (Axios, Reuters)
- Moved HTML cleaning to `utils/clean_text.py`
- Tests for new sources (`tests/test_parsers.py`)
- Fixed duplicates in DB (`make_uid`)

### ✅ Day 3 — AI Modules & Telegram Bot
- Ran AI modules on real data
- Added AI error logging (fallback)
- Unit tests for `ai_modules/`
- AI version marking in news
- Updated `README.md` (AI modules section)
- **Added Telegram bot** with full navigation

### ✅ Day 4 — AI Summary & Events
- Extended `digests/ai_summary.py` (styles: analytical, business, meme)
- Added "why important" to digests
- Tests for `generate_digest()` (different styles)
- WebApp: updated `digest.html`
- Added logging for digest generation time
- **Added events parsing** from Investing.com

### ✅ Day 5 — Architecture Refactoring
- Refactored to **Pydantic models** (`NewsItem`, `EventItem`)
- Centralized **DigestAIService** for both regular and AI digests
- Added **repositories** layer for data access
- Implemented **services** layer for business logic
- Added **utils/formatters** for consistent HTML formatting

### ✅ Day 6 — Testing & Documentation
- Fixed **Telegram bot** callback query timeout errors
- Updated **tests** to work with new architecture
- Added **Makefile** for development commands
- **Complete documentation overhaul** — updated all .md files with consistent style and TOC
- Used **Cursor AI** for automated refactoring and code improvements

---

## ✅ Week 1 Complete (Day 1-6)

**Summary:** Successfully completed the foundation phase with:
- ✅ Complete documentation and project structure
- ✅ Working parsers for RSS and events
- ✅ AI modules for credibility and importance scoring
- ✅ Telegram bot with full navigation
- ✅ Web application with responsive design
- ✅ Pydantic models and centralized services architecture
- ✅ Comprehensive testing suite
- ✅ Development tools and automation

**Next Phase:** Week 2 focuses on subscriptions, Telegram enhancements, and automated digests.

---

## Current Week

### Week 2 — Subscriptions & Telegram Enhancement

**Day 7 — Subscriptions System**
- [ ] `subscriptions` table in DB
- [ ] `subscribe/unsubscribe` methods
- [ ] WebApp UI: subscription management
- [ ] Tests for subscriptions
- [ ] Update `MASTER_FILE.md`

**Day 8 — Telegram Bot Advanced Features**
- [ ] Inline filters in bot
- [ ] `/subscribe` command
- [ ] Webhook or polling setup
- [ ] Bot message logging
- [ ] Tests with mock Telegram API

**Day 9 — Automated Digests**
- [ ] Auto-digests via cron (morning/evening)
- [ ] Logging of sent digests
- [ ] Export events calendar to `.ics`
- [ ] UI: "Week ahead"
- [ ] Tests for auto-digests

**Day 10 — ETL Pipeline Enhancement**
- [ ] HTML cleaning, fallback for empty fields
- [ ] Deduplication (by `uid`)
- [ ] Error logging with trace_id
- [ ] E2E test: news → DB → digest → Telegram
- [ ] Update `docs/ARCHITECTURE.md`

---

## Upcoming Weeks

### Week 3 — Growth & Value

**Day 11 — New Sources**
- [ ] Add categories: technology, regulation
- [ ] Parse Twitter/X, LinkedIn (MVP)
- [ ] Support new categories in DB
- [ ] UI: category selection
- [ ] Social media tests

**Day 12 — Event Priorities**
- [ ] Support priorities (low/med/high)
- [ ] Parse from Investing (priority mapping)
- [ ] Display priority badge in UI
- [ ] Filter by priority
- [ ] Normalization tests

**Day 13 — Calendar Enhancement**
- [ ] Improved calendar (sorting, search)
- [ ] Event subscriptions by keywords
- [ ] Export calendar to Google Calendar API
- [ ] Unit tests for export
- [ ] Documentation in `docs/ARCHITECTURE.md`

**Day 14 — Analytics**
- [ ] Analytics in WebApp (charts, activity)
- [ ] Usage logging (events log)
- [ ] Store statistics in DB
- [ ] Analytics tests
- [ ] Update `ROADMAP.md`

**Day 15 — Real-time Features**
- [ ] Real-time notifications (important events)
- [ ] Push via Telegram
- [ ] Subscription validation
- [ ] Real-time tests
- [ ] Week summary report

### Week 4 — AI, White-Label & Launch

**Day 16-17 — AI Annotations**
- [ ] Compare models (GPT-4, LLaMA, Mistral)
- [ ] Model tests (BLEU/ROUGE)
- [ ] Choose best-of
- [ ] Documentation: model comparison
- [ ] Update `README.md`

**Day 18-19 — White-label**
- [ ] API `/api/digest`
- [ ] White-label frontend templates
- [ ] Brand customization (colors, logo)
- [ ] Unit tests for API
- [ ] White-label documentation

**Day 20-22 — B2B Monetization**
- [ ] SaaS plans (Basic/Pro/Enterprise)
- [ ] User authorization (Supabase Auth)
- [ ] Billing MVP (Stripe/crypto)
- [ ] Authorization and billing tests
- [ ] Update `VISION.md`

**Day 23-24 — Freemium B2C**
- [ ] Limited digest (free)
- [ ] Premium features (filters, calendars)
- [ ] Pricing tests
- [ ] Update `README.md`

**Day 25-27 — Growth Hooks**
- [ ] Referral system
- [ ] Partnerships (brokers, analytics)
- [ ] Partner click logging
- [ ] Referral tests
- [ ] Update `docs/COMMUNICATION.md`

**Day 28-30 — Finalization**
- [ ] MVP finalization
- [ ] E2E tests: news → Telegram → report
- [ ] Complete documentation (`README.md`, `DEPLOY.md`)
- [ ] Product presentation
- [ ] Release preparation

---

## Backlog

### Technical Improvements
- Increase test coverage ≥ 70%
- CI: linters (flake8, black, isort, mypy)
- Performance optimization
- Error handling improvements
- Monitoring and alerting

### Growth & Multi-platform
- Slack integration
- Discord bot
- Mobile app (React Native)
- Browser extension
- API rate limiting

### Monetization
- Advanced pricing tiers
- Enterprise features
- White-label solutions
- Partner integrations
- Revenue analytics

### AI Enhancements
- Custom model training
- Sentiment analysis
- Trend detection
- Content summarization
- Multi-language support