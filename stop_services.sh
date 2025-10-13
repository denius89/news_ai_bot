#!/bin/bash

# Скрипт для остановки всех сервисов PulseAI
# Использование:
#   ./stop_services.sh    - остановить все сервисы
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

# Файл лога для этой остановки
LOG_FILE="$SCRIPT_LOG_DIR/stop_services_$(date +%Y%m%d_%H%M%S).log"

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

log_info "🛑 Остановка PulseAI сервисов..."
log_info "Лог файл: $LOG_FILE"
echo ""

# Останавливаем по PID файлам
if [ -f .flask.pid ]; then
    FLASK_PID=$(cat .flask.pid)
    if ps -p $FLASK_PID > /dev/null 2>&1; then
        log_info "🔄 Остановка Flask WebApp (PID: $FLASK_PID)..."
        kill $FLASK_PID
        log_success "✅ Flask WebApp остановлен"
    else
        log_warning "⚠️ Flask процесс с PID $FLASK_PID не найден"
    fi
    rm .flask.pid
    log "INFO" "Удалён .flask.pid"
else
    log_warning "⚠️ .flask.pid не найден"
fi

if [ -f .bot.pid ]; then
    BOT_PID=$(cat .bot.pid)
    if ps -p $BOT_PID > /dev/null 2>&1; then
        log_info "🔄 Остановка Telegram Bot (PID: $BOT_PID)..."
        kill $BOT_PID
        log_success "✅ Telegram Bot остановлен"
    else
        log_warning "⚠️ Bot процесс с PID $BOT_PID не найден"
    fi
    rm .bot.pid
    log "INFO" "Удалён .bot.pid"
else
    log_warning "⚠️ .bot.pid не найден"
fi

echo ""
log_info "🔍 Принудительная остановка по имени процесса..."

# Принудительная остановка по имени процесса
KILLED_PROCESSES=false

if pkill -f "python3 src/webapp.py" 2>/dev/null; then
    log_warning "⚠️ Остановлены дополнительные процессы Flask"
    KILLED_PROCESSES=true
fi

if pkill -f "python3 telegram_bot/bot.py" 2>/dev/null; then
    log_warning "⚠️ Остановлены дополнительные процессы Bot (telegram_bot/bot.py)"
    KILLED_PROCESSES=true
fi

if pkill -f "python3 -m telegram_bot.bot" 2>/dev/null; then
    log_warning "⚠️ Остановлены дополнительные процессы Bot (telegram_bot.bot)"
    KILLED_PROCESSES=true
fi

if [ "$KILLED_PROCESSES" = false ]; then
    log_success "✅ Дополнительных процессов не найдено"
fi

# Очищаем lock файлы
echo ""
log_info "🧹 Очистка lock файлов..."
rm -f .flask.lock .bot.lock .flask.pid .bot.pid
log_success "✅ Lock и PID файлы очищены"

echo ""
log_success "✅ Все сервисы остановлены"
echo -e "${YELLOW}💡 Cloudflare Tunnel продолжает работать${NC}"
echo -e "${CYAN}📋 Лог остановки: $LOG_FILE${NC}"

log "INFO" "Остановка завершена успешно"
