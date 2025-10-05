# Makefile for news_ai_bot — quick dev commands

PY?=python3

.PHONY: run-bot run-web run-digests run-events run-news test test-cov lint format check dev run-tests-bot check-db run-all stop-all restart-all status logs

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

# 6) Run tests (с автоматической подготовкой окружения)
test:
	@echo "🧪 Запуск тестов с автоматической подготовкой окружения..."
	@$(MAKE) prepare-test-env
	$(PY) -m pytest

# 7) Run tests with coverage (с автоматической подготовкой окружения)
test-cov:
	@echo "🧪 Запуск тестов с покрытием и подготовкой окружения..."
	@$(MAKE) prepare-test-env
	$(PY) -m pytest --cov --cov-report=term-missing

# 8) Подготовка окружения для тестов
prepare-test-env:
	@echo "🔧 Подготовка окружения для тестов..."
	@$(PY) tools/port_manager.py --prepare
	@if [ $$? -ne 0 ]; then \
		echo "❌ Ошибка подготовки окружения"; \
		echo "💡 Попробуйте: make cleanup-env"; \
		exit 1; \
	fi

# 9) Очистка окружения
cleanup-env:
	@echo "🧹 Очистка окружения..."
	@$(PY) tools/port_manager.py --cleanup

# 10) Проверка состояния окружения
check-env:
	@echo "🔍 Проверка состояния окружения..."
	@$(PY) tools/port_manager.py --check

# 11) Lint (только критические ошибки)
lint:
	flake8 . \
		--exclude=venv,__pycache__,.git,tools,parsers/advanced_parser.py \
		--max-line-length=120 \
		--ignore=E402,E501,W293,F401,F841,F541,E722 \
		--select=F821,F811

# 12) Format (black)
format:
	black .

# 13) Pre-push checks (Black + Flake8 + Tests)
pre-push:
	@echo "🔍 Running pre-push checks..."
	@$(MAKE) format
	@$(MAKE) lint
	@echo "✅ Pre-push checks completed"

# 14) Check: lint + tests (с подготовкой окружения)
check:
	@echo "🔍 Проверка кода и тестов..."
	@$(MAKE) prepare-test-env
	@$(MAKE) pre-push
	@$(MAKE) test

# 14) Run tests then bot (с подготовкой окружения)
run-tests-bot:
	@$(MAKE) prepare-test-env
	$(MAKE) test
	$(MAKE) run-bot

# 15) Check database schema
check-db:
	$(PY) tools/check_database.py

# 16) Dev: run bot and web together
dev:
	$(MAKE) run-bot & \
	$(MAKE) run-web

# === Управление всеми процессами ===

# 14) Запустить все процессы (бот + WebApp)
run-all:
	$(PY) tools/run_all.py start

# 15) Остановить все процессы
stop-all:
	$(PY) tools/run_all.py stop

# 16) Перезапустить все процессы
restart-all:
	$(PY) tools/run_all.py restart

# 17) Показать статус процессов
status:
	$(PY) tools/run_all.py status

# 18) Показать логи процессов
logs:
	@if command -v tail >/dev/null 2>&1; then \
		tail -n 100 -f logs/bot.log logs/webapp.log; \
	else \
		echo "💡 Для просмотра логов откройте файлы:"; \
		echo "   - logs/bot.log"; \
		echo "   - logs/webapp.log"; \
		echo ""; \
		echo "Или используйте: python tools/run_all.py logs"; \
	fi

# === Управление портами ===

# 19) Проверить занятые порты
check-ports:
	@echo "🔍 Проверка портов 8001 и 5000..."
	@if lsof -i :8001 >/dev/null 2>&1; then \
		echo "⚠️  Порт 8001 занят:"; \
		lsof -i :8001; \
	else \
		echo "✅ Порт 8001 свободен"; \
	fi
	@if lsof -i :5000 >/dev/null 2>&1; then \
		echo "⚠️  Порт 5000 занят:"; \
		lsof -i :5000; \
	else \
		echo "✅ Порт 5000 свободен"; \
	fi

# 20) Освободить порты
free-ports:
	@echo "🛑 Освобождаем порты..."
	@if lsof -i :8001 >/dev/null 2>&1; then \
		echo "Убиваем процессы на порту 8001..."; \
		lsof -ti :8001 | xargs kill -9 2>/dev/null || true; \
	fi
	@if lsof -i :5000 >/dev/null 2>&1; then \
		echo "Убиваем процессы на порту 5000..."; \
		lsof -ti :5000 | xargs kill -9 2>/dev/null || true; \
	fi
	@echo "✅ Порты освобождены"

# 21) Безопасный запуск WebApp
run-web-safe:
	@echo "🚀 Безопасный запуск WebApp..."
	@$(MAKE) check-ports
	@if lsof -i :8001 >/dev/null 2>&1; then \
		echo "⚠️  Порт 8001 занят, освобождаем..."; \
		$(MAKE) free-ports; \
		sleep 2; \
	fi
	@$(MAKE) run-web

# 22) Безопасный запуск всех сервисов
dev-safe:
	@echo "🚀 Безопасный запуск всех сервисов..."
	@$(MAKE) free-ports
	@sleep 2
	@$(MAKE) run-all

# === Обслуживание базы данных ===

# 23) Полное обслуживание базы данных
db-maintenance:
	@echo "🏗️  Полное обслуживание базы данных..."
	$(PY) tools/database_maintenance.py

# 24) Очистка базы данных
db-cleanup:
	@echo "🧹 Очистка базы данных..."
	$(PY) tools/cleanup_database.py

# 25) Оптимизация базы данных
db-optimize:
	@echo "⚡ Оптимизация базы данных..."
	$(PY) tools/optimize_database.py

# 26) Проверка структуры базы данных
db-check:
	@echo "🔍 Проверка структуры базы данных..."
	$(PY) tools/check_all_columns.py
	$(PY) tools/check_users_table.py

# === Проверка источников RSS ===

# 27) Проверка всех RSS источников
check-sources:
	@echo "🔍 Проверка RSS источников..."
	$(PY) tools/check_sources.py

# 28) Показать отчеты источников
sources-report:
	@echo "📊 Отчеты источников:"
	@echo "   📄 CSV: logs/sources_check.csv"
	@echo "   📄 Markdown: logs/sources_check.md"
	@echo "   📄 JSON: logs/sources_check.json"

