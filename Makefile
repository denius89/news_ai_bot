# Makefile for news_ai_bot — quick dev commands

PY?=python3

.PHONY: run-bot run-web run-digests run-events run-news test test-cov lint format check dev run-tests-bot check-db

# 1) Run Telegram bot
run-bot:
	$(PY) -m telegram_bot.bot

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

# 6) Run tests
test:
	$(PY) -m pytest

# 7) Run tests with coverage
test-cov:
	$(PY) -m pytest --cov --cov-report=term-missing

# 8) Lint
lint:
	flake8 .

# 9) Format (black)
format:
	black .

# 10) Check: lint + tests
check:
	$(MAKE) lint
	$(MAKE) test

# 11) Run tests then bot
run-tests-bot:
	$(MAKE) test
	$(MAKE) run-bot

# 12) Check database schema
check-db:
	$(PY) tools/check_database.py

# 13) Dev: run bot and web together
dev:
	$(MAKE) run-bot & \
	$(MAKE) run-web

