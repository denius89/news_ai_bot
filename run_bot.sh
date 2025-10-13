#!/bin/bash

# Wrapper скрипт для запуска Telegram Bot с защитой от множественного запуска
# Использование:
#   ./run_bot.sh    - запустить Telegram Bot с проверками
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

# Устанавливаем рабочую директорию
cd /Users/denisfedko/news_ai_bot

# Создаём директорию для логов скриптов
SCRIPT_LOG_DIR="logs/scripts"
mkdir -p "$SCRIPT_LOG_DIR"

# Файл лога для этого запуска
LOG_FILE="$SCRIPT_LOG_DIR/run_bot_$(date +%Y%m%d_%H%M%S).log"

# Lock файл для предотвращения множественного запуска
LOCK_FILE=".bot.lock"
PID_FILE=".bot.pid"

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

log_info "🤖 Запуск Telegram Bot"
log_info "Лог файл: $LOG_FILE"
echo ""

# Проверяем, не запущен ли уже бот
if [ -f "$LOCK_FILE" ]; then
    lock_pid=$(cat "$LOCK_FILE")
    if ps -p "$lock_pid" > /dev/null 2>&1; then
        log_error "❌ Telegram Bot уже запущен (PID: $lock_pid)"
        echo -e "${CYAN}💡 Для остановки: ./stop_services.sh${NC}"
        exit 1
    else
        log_warning "🧹 Удаляем устаревший lock файл"
        rm -f "$LOCK_FILE"
    fi
fi

# Проверяем по имени процесса
if pgrep -f "python3 -m telegram_bot.bot" > /dev/null; then
    log_error "❌ Telegram Bot уже запущен (найден по имени процесса)"
    echo -e "${CYAN}💡 Для остановки: ./stop_services.sh${NC}"
    exit 1
fi

# Устанавливаем PYTHONPATH
export PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH"
log "INFO" "PYTHONPATH установлен: $PYTHONPATH"

# Проверяем, что все зависимости доступны
log_info "🔍 Проверка зависимостей..."

if python3 -c "import utils.ai.ai_client; print('✅ utils.ai.ai_client OK')" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "✅ utils.ai.ai_client OK"
else
    log_error "❌ Ошибка импорта utils.ai.ai_client"
    exit 1
fi

if python3 -c "import config.core.settings; print('✅ config.core.settings OK')" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "✅ config.core.settings OK"
else
    # Пробуем старый путь
    if python3 -c "import config.settings; print('✅ config.settings OK')" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "✅ config.settings OK (старый путь)"
    else
        log_error "❌ Ошибка импорта config.settings"
        exit 1
    fi
fi

if python3 -c "import telegram_bot.handlers; print('✅ telegram_bot.handlers OK')" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "✅ telegram_bot.handlers OK"
else
    log_error "❌ Ошибка импорта telegram_bot.handlers"
    exit 1
fi

echo ""

# Создаем lock файл
echo $$ > "$LOCK_FILE"
log "INFO" "Lock файл создан: $LOCK_FILE"

# Функция очистки при выходе
cleanup() {
    log_info "🧹 Очистка lock файлов..."
    rm -f "$LOCK_FILE"
    rm -f "$PID_FILE"
    log "INFO" "Завершение работы бота"
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGTERM SIGINT

log_success "🚀 Запуск Telegram Bot..."
PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH" python3 -m telegram_bot.bot &
BOT_PID=$!

# Сохраняем PID
echo $BOT_PID > "$PID_FILE"
log "INFO" "Bot запущен с PID: $BOT_PID"
log_success "✅ Telegram Bot успешно запущен"
echo ""
echo -e "${CYAN}📋 Лог запуска: $LOG_FILE${NC}"
echo -e "${CYAN}💡 Для остановки: ./stop_services.sh${NC}"

# Ждем завершения процесса
wait $BOT_PID

# Очистка при завершении
cleanup
