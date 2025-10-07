# PulseAI Development Makefile
# 🚀 Централизованное управление сервисами

# =============================================================================
# 🎯 КОНФИГУРАЦИЯ ПОРТОВ
# =============================================================================

REACT_PORT = 3000
FLASK_PORT = 8001
FASTAPI_PORT = 8000

# =============================================================================
# 🎯 ЦВЕТА И ФОРМАТИРОВАНИЕ
# =============================================================================

GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

# =============================================================================
# 🎯 ОСНОВНЫЕ КОМАНДЫ
# =============================================================================

.PHONY: help start stop restart check-ports logs clean

# Показать справку
help:
	@echo "$(BLUE)🚀 PulseAI Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  $(YELLOW)make start$(NC)        - Запустить все сервисы"
	@echo "  $(YELLOW)make stop$(NC)         - Остановить все сервисы"
	@echo "  $(YELLOW)make restart$(NC)      - Перезапустить все сервисы"
	@echo "  $(YELLOW)make check-ports$(NC)  - Проверить доступность портов"
	@echo "  $(YELLOW)make logs$(NC)         - Показать логи всех сервисов"
	@echo "  $(YELLOW)make clean$(NC)        - Очистить процессы и порты"
	@echo ""
	@echo "$(GREEN)Индивидуальные сервисы:$(NC)"
	@echo "  $(YELLOW)make react$(NC)        - Запустить только React (порт $(REACT_PORT))"
	@echo "  $(YELLOW)make flask$(NC)        - Запустить только Flask API (порт $(FLASK_PORT))"
	@echo "  $(YELLOW)make bot$(NC)          - Запустить только Telegram Bot"
	@echo ""
	@echo "$(GREEN)Схема портов:$(NC)"
	@echo "  $(YELLOW)React Frontend:$(NC)   http://localhost:$(REACT_PORT)"
	@echo "  $(YELLOW)Flask API:$(NC)        http://localhost:$(FLASK_PORT)"
	@echo "  $(YELLOW)FastAPI:$(NC)          http://localhost:$(FASTAPI_PORT)"

# =============================================================================
# 🎯 ПРОВЕРКА ПОРТОВ
# =============================================================================

check-ports:
	@echo "$(BLUE)🔍 Проверка портов...$(NC)"
	@echo ""
	@$(MAKE) check-port-react
	@$(MAKE) check-port-flask
	@$(MAKE) check-port-fastapi
	@echo ""

check-port-react:
	@if lsof -Pi :$(REACT_PORT) -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Порт $(REACT_PORT) занят$(NC)"; \
		lsof -Pi :$(REACT_PORT) -sTCP:LISTEN; \
	else \
		echo "$(GREEN)✅ Порт $(REACT_PORT) свободен$(NC)"; \
	fi

check-port-flask:
	@if lsof -Pi :$(FLASK_PORT) -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Порт $(FLASK_PORT) занят$(NC)"; \
		lsof -Pi :$(FLASK_PORT) -sTCP:LISTEN; \
	else \
		echo "$(GREEN)✅ Порт $(FLASK_PORT) свободен$(NC)"; \
	fi

check-port-fastapi:
	@if lsof -Pi :$(FASTAPI_PORT) -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Порт $(FASTAPI_PORT) занят$(NC)"; \
		lsof -Pi :$(FASTAPI_PORT) -sTCP:LISTEN; \
	else \
		echo "$(GREEN)✅ Порт $(FASTAPI_PORT) свободен$(NC)"; \
	fi

# =============================================================================
# 🎯 ЗАПУСК СЕРВИСОВ
# =============================================================================

start: check-ports
	@echo "$(BLUE)🚀 Запуск PulseAI сервисов...$(NC)"
	@echo ""
	@$(MAKE) start-flask
	@sleep 2
	@$(MAKE) start-react
	@echo ""
	@echo "$(GREEN)✅ Все сервисы запущены!$(NC)"
	@echo "$(YELLOW)React Frontend:$(NC) http://localhost:$(REACT_PORT)"
	@echo "$(YELLOW)Flask API:$(NC) http://localhost:$(FLASK_PORT)"

start-react:
	@echo "$(BLUE)⚛️  Запуск React (Vite)...$(NC)"
	@cd webapp && npm run dev > ../logs/react.log 2>&1 &
	@echo "$$!" > logs/react.pid
	@sleep 3
	@if curl -s http://localhost:$(REACT_PORT) > /dev/null; then \
		echo "$(GREEN)✅ React запущен на порту $(REACT_PORT)$(NC)"; \
	else \
		echo "$(RED)❌ React не запустился$(NC)"; \
	fi

start-flask:
	@echo "$(BLUE)🐍 Запуск Flask API...$(NC)"
	@python3 webapp.py > logs/flask.log 2>&1 &
	@echo "$$!" > logs/flask.pid
	@sleep 3
	@if curl -s http://localhost:$(FLASK_PORT)/api/health > /dev/null; then \
		echo "$(GREEN)✅ Flask API запущен на порту $(FLASK_PORT)$(NC)"; \
	else \
		echo "$(RED)❌ Flask API не запустился$(NC)"; \
	fi

start-bot:
	@echo "$(BLUE)🤖 Запуск Telegram Bot...$(NC)"
	@python3 main.py > logs/bot.log 2>&1 &
	@echo "$$!" > logs/bot.pid
	@sleep 2
	@echo "$(GREEN)✅ Telegram Bot запущен$(NC)"

# =============================================================================
# 🎯 ИНДИВИДУАЛЬНЫЕ КОМАНДЫ
# =============================================================================

react: check-port-react
	@$(MAKE) start-react

flask: check-port-flask
	@$(MAKE) start-flask

bot:
	@$(MAKE) start-bot

# =============================================================================
# 🎯 ОСТАНОВКА СЕРВИСОВ
# =============================================================================

stop:
	@echo "$(BLUE)🛑 Остановка сервисов...$(NC)"
	@$(MAKE) stop-react
	@$(MAKE) stop-flask
	@$(MAKE) stop-bot
	@echo "$(GREEN)✅ Все сервисы остановлены$(NC)"

stop-react:
	@if [ -f logs/react.pid ]; then \
		kill $$(cat logs/react.pid) 2>/dev/null || true; \
		rm -f logs/react.pid; \
		echo "$(YELLOW)🛑 React остановлен$(NC)"; \
	fi

stop-flask:
	@if [ -f logs/flask.pid ]; then \
		kill $$(cat logs/flask.pid) 2>/dev/null || true; \
		rm -f logs/flask.pid; \
		echo "$(YELLOW)🛑 Flask остановлен$(NC)"; \
	fi

stop-bot:
	@if [ -f logs/bot.pid ]; then \
		kill $$(cat logs/bot.pid) 2>/dev/null || true; \
		rm -f logs/bot.pid; \
		echo "$(YELLOW)🛑 Bot остановлен$(NC)"; \
	fi

# =============================================================================
# 🎯 ПЕРЕЗАПУСК И ОЧИСТКА
# =============================================================================

restart: stop start

clean: stop
	@echo "$(BLUE)🧹 Очистка...$(NC)"
	@# Убиваем все процессы на наших портах
	@lsof -ti:$(REACT_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti:$(FLASK_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti:$(FASTAPI_PORT) | xargs kill -9 2>/dev/null || true
	@# Очищаем логи
	@rm -f logs/*.pid
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# =============================================================================
# 🎯 ЛОГИ И МОНИТОРИНГ
# =============================================================================

logs:
	@echo "$(BLUE)📋 Логи сервисов:$(NC)"
	@echo ""
	@echo "$(YELLOW)=== React (последние 10 строк) ===$(NC)"
	@tail -10 logs/react.log 2>/dev/null || echo "Нет логов React"
	@echo ""
	@echo "$(YELLOW)=== Flask (последние 10 строк) ===$(NC)"
	@tail -10 logs/flask.log 2>/dev/null || echo "Нет логов Flask"
	@echo ""
	@echo "$(YELLOW)=== Bot (последние 10 строк) ===$(NC)"
	@tail -10 logs/bot.log 2>/dev/null || echo "Нет логов Bot"

logs-react:
	@tail -f logs/react.log

logs-flask:
	@tail -f logs/flask.log

logs-bot:
	@tail -f logs/bot.log

# =============================================================================
# 🎯 РАЗРАБОТКА
# =============================================================================

install:
	@echo "$(BLUE)📦 Установка зависимостей...$(NC)"
	@pip3 install -r requirements.txt
	@cd webapp && npm install
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

dev: install start

# =============================================================================
# 🎯 ТЕСТИРОВАНИЕ
# =============================================================================

test-api:
	@echo "$(BLUE)🧪 Тестирование API...$(NC)"
	@curl -s http://localhost:$(FLASK_PORT)/api/health | jq .
	@curl -s http://localhost:$(FLASK_PORT)/api/latest?limit=3 | jq '.data | length'

test-react:
	@echo "$(BLUE)🧪 Тестирование React...$(NC)"
	@curl -s http://localhost:$(REACT_PORT) | grep -o '<title>.*</title>'

test: test-api test-react

# =============================================================================
# 🎯 СТАТУС
# =============================================================================

status:
	@echo "$(BLUE)📊 Статус сервисов:$(NC)"
	@echo ""
	@$(MAKE) check-ports
	@echo ""
	@if [ -f logs/react.pid ]; then echo "$(GREEN)✅ React: запущен$(NC)"; else echo "$(RED)❌ React: остановлен$(NC)"; fi
	@if [ -f logs/flask.pid ]; then echo "$(GREEN)✅ Flask: запущен$(NC)"; else echo "$(RED)❌ Flask: остановлен$(NC)"; fi
	@if [ -f logs/bot.pid ]; then echo "$(GREEN)✅ Bot: запущен$(NC)"; else echo "$(RED)❌ Bot: остановлен$(NC)"; fi

# =============================================================================
# 🎯 ДЕФОЛТНАЯ КОМАНДА
# =============================================================================

.DEFAULT_GOAL := help