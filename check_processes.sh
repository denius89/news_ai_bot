#!/bin/bash

# Скрипт для проверки статуса всех процессов PulseAI
# Использование:
#   ./check_processes.sh            - детальная проверка (по умолчанию)
#   ./check_processes.sh --brief    - краткая проверка
#   ./check_processes.sh --detailed - детальная проверка (явно)
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

# Параметры
MODE="detailed"

# Парсинг аргументов
for arg in "$@"; do
    case $arg in
        --brief|-b)
            MODE="brief"
            shift
            ;;
        --detailed|-d)
            MODE="detailed"
            shift
            ;;
        --help|-h)
            echo "Использование: $0 [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "  --brief, -b       Краткий вывод статуса"
            echo "  --detailed, -d    Детальная диагностика (по умолчанию)"
            echo "  --help, -h        Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  $0                # Детальная проверка"
            echo "  $0 --brief        # Быстрая проверка статуса"
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

# Файл лога для этой проверки
LOG_FILE="$SCRIPT_LOG_DIR/check_processes_$(date +%Y%m%d_%H%M%S).log"

# Функция логирования
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Функция для проверки процесса (краткий режим)
check_process_brief() {
    local process_name="$1"
    local lock_file="$2"
    
    # Проверяем по имени процесса
    local pid=$(pgrep -f "$process_name" | head -1)
    
    if [ -n "$pid" ]; then
        echo -e "⚠️ Процесс ${CYAN}$process_name${NC} уже запущен (PID: ${YELLOW}$pid${NC})"
        log "INFO" "Процесс $process_name запущен (PID: $pid)"
        
        # Проверяем lock файл
        if [ -f "$lock_file" ]; then
            local lock_pid=$(cat "$lock_file")
            if [ "$lock_pid" = "$pid" ]; then
                echo -e "  ${GREEN}✅ Lock файл соответствует процессу${NC}"
                log "INFO" "Lock файл $lock_file соответствует процессу"
                return 0
            else
                echo -e "  ${RED}❌ Lock файл устарел${NC}"
                log "WARNING" "Lock файл $lock_file устарел (содержит PID: $lock_pid)"
            fi
        fi
        
        return 1
    else
        echo -e "✅ Процесс ${CYAN}$process_name${NC} не запущен"
        log "INFO" "Процесс $process_name не запущен"
        return 0
    fi
}

# Функция для проверки процесса (детальный режим)
check_process_detailed() {
    local process_pattern="$1"
    local process_name="$2"
    local expected_port="$3"
    local check_url="$4"
    
    echo -e "${BLUE}🔍 Проверка $process_name...${NC}"
    log "INFO" "Проверка процесса: $process_name"
    
    if pgrep -f "$process_pattern" > /dev/null; then
        echo -e "${GREEN}✅ $process_name запущен${NC}"
        log "SUCCESS" "$process_name запущен"
        
        # Показываем детали процессов
        pgrep -f "$process_pattern" | while read pid; do
            local cmd=$(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')
            local cpu=$(ps -p $pid -o %cpu= 2>/dev/null || echo 'N/A')
            local mem=$(ps -p $pid -o %mem= 2>/dev/null || echo 'N/A')
            local time=$(ps -p $pid -o etime= 2>/dev/null || echo 'N/A')
            
            echo -e "   ${CYAN}PID:${NC} $pid"
            echo -e "   ${CYAN}CPU:${NC} $cpu%"
            echo -e "   ${CYAN}Memory:${NC} $mem%"
            echo -e "   ${CYAN}Uptime:${NC} $time"
            echo -e "   ${CYAN}Command:${NC} $cmd"
            
            log "INFO" "PID: $pid, CPU: $cpu%, Memory: $mem%, Uptime: $time"
        done
        
        # Проверяем порт если указан
        if [ -n "$expected_port" ]; then
            if lsof -i ":$expected_port" > /dev/null 2>&1; then
                echo -e "   ${GREEN}✅ Порт $expected_port занят${NC}"
                log "SUCCESS" "Порт $expected_port занят"
            else
                echo -e "   ${YELLOW}⚠️ Порт $expected_port свободен${NC}"
                log "WARNING" "Порт $expected_port свободен"
            fi
        fi
        
        # Проверяем доступность если указан URL
        if [ -n "$check_url" ]; then
            if curl -s "$check_url" > /dev/null 2>&1; then
                echo -e "   ${GREEN}✅ Доступен по $check_url${NC}"
                log "SUCCESS" "Доступен по $check_url"
            else
                echo -e "   ${RED}❌ Недоступен по $check_url${NC}"
                log "ERROR" "Недоступен по $check_url"
            fi
        fi
        
        return 0
    else
        echo -e "${RED}❌ $process_name не запущен${NC}"
        log "ERROR" "$process_name не запущен"
        return 1
    fi
}

# Функция для проверки портов
check_ports() {
    echo -e "${BLUE}🔌 Проверка портов...${NC}"
    log "INFO" "Проверка портов"
    
    local ports=("8001:Flask WebApp" "3000:React Dev Server")
    
    for port_info in "${ports[@]}"; do
        local port=$(echo $port_info | cut -d: -f1)
        local service=$(echo $port_info | cut -d: -f2)
        
        if lsof -i ":$port" > /dev/null 2>&1; then
            local pid=$(lsof -i ":$port" | tail -n +2 | awk '{print $2}' | head -1)
            echo -e "   ${GREEN}✅ Порт $port ($service) занят PID: $pid${NC}"
            log "SUCCESS" "Порт $port ($service) занят PID: $pid"
        else
            echo -e "   ${YELLOW}⚠️ Порт $port ($service) свободен${NC}"
            log "WARNING" "Порт $port ($service) свободен"
        fi
    done
}

# Функция для проверки Cloudflare Tunnel
check_cloudflare() {
    echo -e "${BLUE}🌐 Проверка Cloudflare Tunnel...${NC}"
    log "INFO" "Проверка Cloudflare Tunnel"
    
    if pgrep -f "cloudflared" > /dev/null; then
        echo -e "${GREEN}✅ Cloudflare Tunnel запущен${NC}"
        log "SUCCESS" "Cloudflare Tunnel запущен"
        
        pgrep -f "cloudflared" | while read pid; do
            local cmd=$(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')
            local cpu=$(ps -p $pid -o %cpu= 2>/dev/null || echo 'N/A')
            local mem=$(ps -p $pid -o %mem= 2>/dev/null || echo 'N/A')
            local time=$(ps -p $pid -o etime= 2>/dev/null || echo 'N/A')
            
            echo -e "   ${CYAN}PID:${NC} $pid"
            echo -e "   ${CYAN}CPU:${NC} $cpu%"
            echo -e "   ${CYAN}Memory:${NC} $mem%"
            echo -e "   ${CYAN}Uptime:${NC} $time"
            echo -e "   ${CYAN}Command:${NC} $cmd"
            
            log "INFO" "Cloudflare PID: $pid, CPU: $cpu%, Memory: $mem%"
        done
        
        # Получаем URL из конфига
        WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/Users/denisfedko/news_ai_bot')
try:
    from config.core.cloudflare import CLOUDFLARE_TUNNEL_URL
    print(CLOUDFLARE_TUNNEL_URL)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null || echo "ERROR: Cannot load Cloudflare configuration")
        
        echo -e "   ${CYAN}URL:${NC} $WEBAPP_URL"
        log "INFO" "Cloudflare URL: $WEBAPP_URL"
        
        # Проверяем доступность
        if curl -s "$WEBAPP_URL/webapp" > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Cloudflare Tunnel доступен${NC}"
            log "SUCCESS" "Cloudflare Tunnel доступен"
        else
            echo -e "   ${RED}❌ Cloudflare Tunnel недоступен${NC}"
            log "ERROR" "Cloudflare Tunnel недоступен"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Cloudflare Tunnel не запущен${NC}"
        log "ERROR" "Cloudflare Tunnel не запущен"
        return 1
    fi
}

# Функция для показа общей статистики
show_summary() {
    echo ""
    echo -e "${BLUE}📊 ОБЩАЯ СТАТИСТИКА${NC}"
    echo "=================================================="
    
    local flask_count=$(pgrep -f "python3 src/webapp.py" | wc -l)
    local bot_count=$(pgrep -f "telegram_bot" | wc -l)
    local cloudflare_count=$(pgrep -f "cloudflared" | wc -l)
    
    echo -e "${CYAN}Flask WebApp процессов:${NC} $flask_count"
    echo -e "${CYAN}Telegram Bot процессов:${NC} $bot_count"
    echo -e "${CYAN}Cloudflare Tunnel процессов:${NC} $cloudflare_count"
    
    log "INFO" "Статистика - Flask: $flask_count, Bot: $bot_count, Cloudflare: $cloudflare_count"
    
    # Проверяем PID файлы
    echo ""
    echo -e "${BLUE}📁 PID ФАЙЛЫ${NC}"
    echo "=================================================="
    
    if [ -f ".flask.pid" ]; then
        local flask_pid=$(cat .flask.pid)
        if ps -p $flask_pid > /dev/null 2>&1; then
            echo -e "${GREEN}✅ .flask.pid: $flask_pid (активен)${NC}"
            log "SUCCESS" ".flask.pid: $flask_pid (активен)"
        else
            echo -e "${RED}❌ .flask.pid: $flask_pid (неактивен)${NC}"
            log "ERROR" ".flask.pid: $flask_pid (неактивен)"
        fi
    else
        echo -e "${YELLOW}⚠️ .flask.pid не найден${NC}"
        log "WARNING" ".flask.pid не найден"
    fi
    
    if [ -f ".bot.pid" ]; then
        local bot_pid=$(cat .bot.pid)
        if ps -p $bot_pid > /dev/null 2>&1; then
            echo -e "${GREEN}✅ .bot.pid: $bot_pid (активен)${NC}"
            log "SUCCESS" ".bot.pid: $bot_pid (активен)"
        else
            echo -e "${RED}❌ .bot.pid: $bot_pid (неактивен)${NC}"
            log "ERROR" ".bot.pid: $bot_pid (неактивен)"
        fi
    else
        echo -e "${YELLOW}⚠️ .bot.pid не найден${NC}"
        log "WARNING" ".bot.pid не найден"
    fi
    
    # Проверяем lock файлы
    echo ""
    echo -e "${BLUE}🔒 LOCK ФАЙЛЫ${NC}"
    echo "=================================================="
    
    if [ -f ".flask.lock" ]; then
        echo -e "${YELLOW}⚠️ .flask.lock найден${NC}"
        log "WARNING" ".flask.lock найден"
    fi
    
    if [ -f ".bot.lock" ]; then
        echo -e "${YELLOW}⚠️ .bot.lock найден${NC}"
        log "WARNING" ".bot.lock найден"
    fi
    
    if [ ! -f ".flask.lock" ] && [ ! -f ".bot.lock" ]; then
        echo -e "${GREEN}✅ Lock файлы не найдены${NC}"
        log "SUCCESS" "Lock файлы не найдены"
    fi
}

# Краткий режим
run_brief_check() {
    echo -e "${BLUE}🔍 Проверка запущенных процессов PulseAI (краткий режим)${NC}"
    log "INFO" "Запуск краткой проверки"
    echo ""
    
    # Проверяем Flask WebApp
    check_process_brief "python3 src/webapp.py" ".flask.pid"
    flask_running=$?
    
    # Проверяем Telegram Bot
    check_process_brief "python3 -m telegram_bot.bot" ".bot.pid"
    bot_running=$?
    
    # Проверяем другие экземпляры бота
    other_bots=$(pgrep -f "telegram_bot" | wc -l)
    if [ "$other_bots" -gt 1 ]; then
        echo -e "${RED}❌ Обнаружено $other_bots экземпляров Telegram Bot!${NC}"
        echo -e "${CYAN}🔧 Рекомендуется остановить все процессы: ./stop_services.sh${NC}"
        log "ERROR" "Обнаружено $other_bots экземпляров Telegram Bot"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Статус:${NC}"
    echo -e "  Flask WebApp: $([ $flask_running -eq 1 ] && echo "${GREEN}запущен${NC}" || echo "${YELLOW}остановлен${NC}")"
    echo -e "  Telegram Bot: $([ $bot_running -eq 1 ] && echo "${GREEN}запущен${NC}" || echo "${YELLOW}остановлен${NC}")"
    
    if [ $flask_running -eq 1 ] && [ $bot_running -eq 1 ]; then
        echo -e "${GREEN}✅ Все сервисы работают${NC}"
        log "SUCCESS" "Все сервисы работают"
        return 0
    else
        echo -e "${YELLOW}⚠️ Некоторые сервисы не запущены${NC}"
        log "WARNING" "Некоторые сервисы не запущены"
        return 1
    fi
}

# Детальный режим
run_detailed_check() {
    echo -e "${BLUE}🔍 Проверка статуса PulseAI сервисов (детальный режим)${NC}"
    echo "=================================================="
    log "INFO" "Запуск детальной проверки"
    echo ""
    
    # Проверяем основные сервисы
    check_process_detailed "python3 src/webapp.py" "Flask WebApp" "8001" "http://localhost:8001/webapp"
    echo ""
    
    check_process_detailed "telegram_bot" "Telegram Bot" "" ""
    echo ""
    
    check_cloudflare
    echo ""
    
    check_ports
    echo ""
    
    show_summary
    
    echo ""
    echo -e "${BLUE}💡 КОМАНДЫ УПРАВЛЕНИЯ${NC}"
    echo "=================================================="
    echo -e "${CYAN}Запуск:${NC} ./start_services.sh"
    echo -e "${CYAN}Остановка:${NC} ./stop_services.sh"
    echo -e "${CYAN}Проверка:${NC} ./check_processes.sh"
    echo -e "${CYAN}Логи:${NC} tail -f logs/*.log"
    echo -e "${CYAN}Лог проверки:${NC} $LOG_FILE"
}

# Основная функция
main() {
    if [ "$MODE" = "brief" ]; then
        run_brief_check
    else
        run_detailed_check
    fi
}

# Запуск основной функции
main "$@"
