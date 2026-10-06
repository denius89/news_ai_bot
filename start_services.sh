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

# Автоматическое восстановление .env файла
if [ ! -f ".env" ]; then
    log_warning "⚠️ Файл .env отсутствует"

    # Проверяем наличие бэкапов в git stash
    if git stash list | grep -q "env-backup\|production config\|initial backup" 2>/dev/null; then
        log_info "📦 Восстанавливаю .env из последнего бэкапа..."

        # Восстанавливаем без удаления из стеша
        if git checkout stash@{0} -- .env >> "$LOG_FILE" 2>&1; then
            # Убираем из staged area
            git restore --staged .env 2>> "$LOG_FILE" || true
            log_success "✅ Файл .env восстановлен из бэкапа"
        else
            log_error "❌ Не удалось восстановить .env"
            log_error "💡 Запустите вручную: env-restore"
            exit 1
        fi
    else
        log_error "❌ Бэкапы .env не найдены в git stash"
        log_error "💡 Создайте .env из .env.example и настройте переменные"
        exit 1
    fi
else
    log_success "✅ Файл .env обнаружен"
fi
echo ""

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    log_error "❌ Виртуальное окружение не найдено!"
    log_error "💡 Создайте виртуальное окружение: python3 -m venv venv"
    exit 1
fi

# Проверяем здоровье проекта (если не отключено)
if [ "$SKIP_HEALTH_CHECK" = false ]; then
    log_info "🔍 Проверка здоровья проекта..."
    if venv/bin/python scripts/health_check.py >> "$LOG_FILE" 2>&1; then
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

# Функция принудительной очистки всех процессов
force_kill_all_instances() {
    log_info "🧹 Принудительная очистка всех экземпляров сервисов..."

    # Убиваем все Flask процессы
    if pkill -9 -f "Python.*src/webapp.py" 2>/dev/null; then
        log_warning "⚠️ Принудительно остановлены Flask процессы"
        sleep 1
    fi

    # Убиваем все Telegram Bot процессы
    if pkill -9 -f "Python.*telegram_bot" 2>/dev/null; then
        log_warning "⚠️ Принудительно остановлены Telegram Bot процессы"
        sleep 1
    fi

    # Проверяем что всё убито
    FLASK_COUNT=$(ps aux | grep -E "Python.*src/webapp.py" | grep -v grep | wc -l)
    BOT_COUNT=$(ps aux | grep -E "Python.*telegram_bot" | grep -v grep | wc -l)

    if [ "$FLASK_COUNT" -eq 0 ] && [ "$BOT_COUNT" -eq 0 ]; then
        log_success "✅ Все процессы успешно остановлены"
    else
        log_error "❌ Остались процессы: Flask=$FLASK_COUNT, Bot=$BOT_COUNT"
        log_error "Запуск прерван для безопасности"
        exit 1
    fi
}

# Вызвать функцию перед запуском
force_kill_all_instances
echo ""

# Останавливаем старые процессы
log_info "🔄 Остановка старых процессов..."
pkill -f "venv/bin/python.*src/webapp.py" 2>/dev/null || true
pkill -f "venv/bin/python.*-m telegram_bot.bot" 2>/dev/null || true
pkill -f "python3.*src/webapp.py" 2>/dev/null || true
pkill -f "python3.*telegram_bot" 2>/dev/null || true
sleep 2
log_success "✅ Старые процессы остановлены"
echo ""

# Запускаем Flask WebApp
log_info "🌐 Запуск Flask WebApp..."
venv/bin/python src/webapp.py > logs/webapp.log 2>&1 &
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
venv/bin/python -m telegram_bot.bot > logs/bot.log 2>&1 &
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
WEBAPP_URL=$(venv/bin/python -c "
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
