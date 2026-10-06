#!/bin/bash

# Скрипт для мониторинга и автоматического восстановления сервисов
# Использование:
#   ./monitor_services.sh          - проверить и восстановить упавшие сервисы
#   */5 * * * * ./monitor_services.sh  - добавить в crontab для автомониторинга
#
# Автор: PulseAI Team
# Версия: 2.0

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Создаём директорию для логов скриптов
SCRIPT_LOG_DIR="logs/scripts"
mkdir -p "$SCRIPT_LOG_DIR"

# Файл лога для этого мониторинга
LOG_FILE="$SCRIPT_LOG_DIR/monitor_services_$(date +%Y%m%d_%H%M%S).log"

# Функция логирования
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Функция для вывода с цветом и логированием
log_info() {
    echo -e "${BLUE}$@${NC}"
    log "INFO" "$@"
}

log_success() {
    echo -e "${GREEN}$@${NC}"
    log "SUCCESS" "$@"
}

log_warning() {
    echo -e "${YELLOW}$@${NC}"
    log "WARNING" "$@"
}

log_error() {
    echo -e "${RED}$@${NC}"
    log "ERROR" "$@"
}

log_info "🔍 МОНИТОРИНГ СЕРВИСОВ PULSEAI"
log_info "==============================="
log_info "Лог файл: $LOG_FILE"
echo ""

# Функция проверки Flask
check_flask() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null)
    if [ "$response" = "200" ]; then
        log_success "✅ Flask WebApp: работает (HTTP $response)"
        return 0
    else
        log_error "❌ Flask WebApp: не работает (HTTP $response)"
        return 1
    fi
}

# Функция проверки Telegram Bot
check_telegram_bot() {
    local processes=$(ps aux | grep "telegram_bot" | grep -v grep | wc -l)
    if [ "$processes" -gt 0 ]; then
        log_success "✅ Telegram Bot: работает ($processes процессов)"
        return 0
    else
        log_error "❌ Telegram Bot: не работает"
        return 1
    fi
}

# Функция проверки Cloudflare туннеля
check_cloudflare() {
    local processes=$(ps aux | grep "cloudflared" | grep -v grep | wc -l)
    if [ "$processes" -gt 0 ]; then
        log_success "✅ Cloudflare Tunnel: работает ($processes процессов)"
        return 0
    else
        log_error "❌ Cloudflare Tunnel: не работает"
        return 1
    fi
}

# Функция перезапуска Flask
restart_flask() {
    log_info "🔄 Перезапуск Flask WebApp..."
    
    pkill -f "src/webapp.py" 2>/dev/null
    sleep 3
    
    export PYTHONPATH="/home/user/news_ai_bot:$PYTHONPATH"
    python3 src/webapp.py > logs/webapp.log 2>&1 &
    FLASK_PID=$!
    
    echo $FLASK_PID > .flask.pid
    log "INFO" "Flask WebApp запущен с PID: $FLASK_PID"
    
    sleep 5
    
    if check_flask; then
        log_success "✅ Flask WebApp успешно перезапущен"
        return 0
    else
        log_error "❌ Не удалось перезапустить Flask WebApp"
        return 1
    fi
}

# Функция перезапуска Telegram Bot
restart_telegram_bot() {
    log_info "🔄 Перезапуск Telegram Bot..."
    
    pkill -f "telegram_bot" 2>/dev/null
    sleep 3
    
    export PYTHONPATH="/home/user/news_ai_bot:$PYTHONPATH"
    python3 -m telegram_bot.bot > logs/bot.log 2>&1 &
    BOT_PID=$!
    
    echo $BOT_PID > .bot.pid
    log "INFO" "Telegram Bot запущен с PID: $BOT_PID"
    
    sleep 5
    
    if check_telegram_bot; then
        log_success "✅ Telegram Bot успешно перезапущен"
        return 0
    else
        log_error "❌ Не удалось перезапустить Telegram Bot"
        return 1
    fi
}

# Основная функция мониторинга
monitor_services() {
    log_info "📊 Статус сервисов на $(date):"
    log_info "-------------------------------"
    echo ""
    
    local flask_ok=0
    local telegram_ok=0
    local cloudflare_ok=0
    
    # Проверяем все сервисы
    if check_flask; then
        flask_ok=1
    fi
    
    if check_telegram_bot; then
        telegram_ok=1
    fi
    
    if check_cloudflare; then
        cloudflare_ok=1
    fi
    
    echo ""
    log_info "-------------------------------"
    echo ""
    
    # Автоматическое восстановление
    if [ "$flask_ok" -eq 0 ]; then
        log_warning "⚠️ Flask WebApp недоступен, пытаемся восстановить..."
        restart_flask
    fi
    
    if [ "$telegram_ok" -eq 0 ]; then
        log_warning "⚠️ Telegram Bot недоступен, пытаемся восстановить..."
        restart_telegram_bot
    fi
    
    if [ "$cloudflare_ok" -eq 0 ]; then
        log_warning "⚠️ Cloudflare Tunnel недоступен"
        echo -e "${CYAN}💡 Запустите вручную: cloudflared tunnel --url http://localhost:8001${NC}"
        log "INFO" "Cloudflare Tunnel требует ручного запуска"
    fi
    
    # Финальный статус
    echo ""
    if [ "$flask_ok" -eq 1 ] && [ "$telegram_ok" -eq 1 ] && [ "$cloudflare_ok" -eq 1 ]; then
        log_success "🎉 Все сервисы работают нормально!"
    else
        log_warning "⚠️ Некоторые сервисы требуют внимания"
    fi
    
    echo ""
    echo -e "${CYAN}📋 Лог мониторинга: $LOG_FILE${NC}"
}

# Запуск мониторинга
monitor_services
