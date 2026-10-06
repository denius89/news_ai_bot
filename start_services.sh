#!/bin/bash

# Скрипт для запуска всех сервисов PulseAI
# Использование:
#   ./start_services.sh              - запуск с проверкой здоровья (safe mode)
#   ./start_services.sh --skip-health-check - быстрый запуск без проверок
#
# Автор: PulseAI Team
# Версия: 2.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Параметры
SKIP_HEALTH_CHECK=false

# Парсинг аргументов
for arg in "$@"; do
    case $arg in
        --skip-health-check)
            SKIP_HEALTH_CHECK=true
            shift
            ;;
        --help|-h)
            echo "Использование: $0 [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "  --skip-health-check    Пропустить проверку здоровья проекта"
            echo "  --help, -h             Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  $0                     # Запуск с проверками (рекомендуется)"
            echo "  $0 --skip-health-check # Быстрый запуск без проверок"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Неизвестный параметр: $arg${NC}"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Создаём директорию для логов скриптов
SCRIPT_LOG_DIR="logs/scripts"
mkdir -p "$SCRIPT_LOG_DIR"

# Файл лога для этого запуска
LOG_FILE="$SCRIPT_LOG_DIR/start_services_$(date +%Y%m%d_%H%M%S).log"

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

log_info "🛡️ ЗАПУСК PULSEAI СЕРВИСОВ"
log_info "==============================="
log_info "Лог файл: $LOG_FILE"
log_info "Health check: $([ "$SKIP_HEALTH_CHECK" = true ] && echo "отключён" || echo "включён")"
echo ""

# Проверяем здоровье проекта (если не отключено)
if [ "$SKIP_HEALTH_CHECK" = false ]; then
    log_info "🔍 Проверка здоровья проекта..."
    if python3 scripts/health_check.py >> "$LOG_FILE" 2>&1; then
        log_success "✅ Проект здоров, продолжаем запуск..."
    else
        log_error "❌ Проверка здоровья не пройдена!"
        log_error "💡 Исправьте ошибки и попробуйте снова"
        log_error "📋 Подробности в логе: $LOG_FILE"
        exit 1
    fi
    echo ""
else
    log_warning "⚠️ Проверка здоровья пропущена (--skip-health-check)"
    echo ""
fi

# Устанавливаем переменные окружения
export PYTHONPATH="/home/user/news_ai_bot:$PYTHONPATH"
log "INFO" "PYTHONPATH установлен: $PYTHONPATH"

# Останавливаем старые процессы
log_info "🔄 Остановка старых процессов..."
pkill -f "python.*webapp.py" 2>/dev/null || true
pkill -f "python.*telegram_bot" 2>/dev/null || true
sleep 2
log_success "✅ Старые процессы остановлены"
echo ""

# Запускаем Flask WebApp
log_info "🌐 Запуск Flask WebApp..."
python3 src/webapp.py > logs/webapp.log 2>&1 &
FLASK_PID=$!
log "INFO" "Flask WebApp запущен с PID: $FLASK_PID"

# Ждем запуска Flask
sleep 3

# Проверяем что Flask запустился
if curl -s http://localhost:8001/webapp > /dev/null 2>&1; then
    log_success "✅ Flask WebApp запущен успешно"
else
    log_error "❌ Flask WebApp не запустился"
    log_error "📋 Логи Flask:"
    tail -10 logs/webapp.log | tee -a "$LOG_FILE"
    exit 1
fi
echo ""

# Запускаем Telegram Bot
log_info "🤖 Запуск Telegram Bot..."
python3 -m telegram_bot.bot > logs/bot.log 2>&1 &
BOT_PID=$!
log "INFO" "Telegram Bot запущен с PID: $BOT_PID"

# Ждем запуска Bot
sleep 3

# Проверяем что Bot запустился
if ps -p $BOT_PID > /dev/null 2>&1; then
    log_success "✅ Telegram Bot запущен успешно"
else
    log_error "❌ Telegram Bot не запустился"
    log_error "📋 Логи Bot:"
    tail -10 logs/bot.log | tee -a "$LOG_FILE"
    exit 1
fi
echo ""

# Получаем URL из конфига
WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/home/user/news_ai_bot')
try:
    from config.core.cloudflare import get_webapp_url
    print(get_webapp_url())
except:
    from config.cloudflare import get_webapp_url
    print(get_webapp_url())
" 2>/dev/null || echo "http://localhost:8001")

log_success "🎉 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================"
echo -e "${CYAN}📱 WebApp:${NC} $WEBAPP_URL"
echo -e "${CYAN}🤖 Telegram Bot:${NC} готов к работе"
echo -e "${CYAN}🌐 Flask:${NC} http://localhost:8001/webapp"
echo -e "${CYAN}📋 Лог запуска:${NC} $LOG_FILE"
echo ""
echo -e "${YELLOW}💡 Для остановки: ./stop_services.sh${NC}"
echo -e "${YELLOW}🔍 Для проверки: ./check_processes.sh${NC}"

# Сохраняем PID для остановки
echo $FLASK_PID > .flask.pid
echo $BOT_PID > .bot.pid
log "INFO" "PID сохранены: Flask (.flask.pid), Bot (.bot.pid)"

log_success "✅ Запуск завершён успешно"
