# Makefile for news_ai_bot — quick dev commands

PY?=python

.PHONY: run-bot run-web run-digests run-events run-news test test-cov lint format check dev

# 1) Run Telegram bot
run-bot:
	ENV=.env $(PY) -m telegram_bot.bot

# 2) Run web app
run-web:
	$(PY) webapp.py

# 3) Run digests generator (AI, category economy, limit 5)
run-digests:
	$(PY) -m digests.generator --ai --limit 5 --category economy

# 4) Fetch and store events
run-events:
	$(PY) tools/fetch_and_store_events.py

# 5) Fetch and store news
run-news:
	$(PY) tools/fetch_and_store_news.py

# 6) Run tests (quiet, no warnings)
test:
	pytest -q --disable-warnings

# 7) Run tests with coverage
test-cov:
	pytest --cov --cov-report=term-missing

# 8) Lint (ruff)
lint:
	ruff check .

# 9) Format (black)
format:
	black .

# 10) Check: lint + tests
check:
	$(MAKE) lint
	$(MAKE) test

# 11) Dev: run bot and web together
dev:
	$(MAKE) run-bot & \
	$(MAKE) run-web

