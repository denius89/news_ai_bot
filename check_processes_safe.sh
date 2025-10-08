#!/bin/bash

# Скрипт для проверки статуса всех процессов PulseAI
# Автор: AI Assistant
# Версия: 2.0

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для проверки процесса
check_process_status() {
    local process_pattern="$1"
    local process_name="$2"
    local expected_port="$3"
    local check_url="$4"
    
    echo -e "${BLUE}🔍 Проверка $process_name...${NC}"
    
    if pgrep -f "$process_pattern" > /dev/null; then
        echo -e "${GREEN}✅ $process_name запущен${NC}"
        
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
        done
        
        # Проверяем порт если указан
        if [ -n "$expected_port" ]; then
            if lsof -i ":$expected_port" > /dev/null 2>&1; then
                echo -e "   ${GREEN}✅ Порт $expected_port занят${NC}"
            else
                echo -e "   ${YELLOW}⚠️ Порт $expected_port свободен${NC}"
            fi
        fi
        
        # Проверяем доступность если указан URL
        if [ -n "$check_url" ]; then
            if curl -s "$check_url" > /dev/null 2>&1; then
                echo -e "   ${GREEN}✅ Доступен по $check_url${NC}"
            else
                echo -e "   ${RED}❌ Недоступен по $check_url${NC}"
            fi
        fi
        
        return 0
    else
        echo -e "${RED}❌ $process_name не запущен${NC}"
        return 1
    fi
}

# Функция для проверки портов
check_ports() {
    echo -e "${BLUE}🔌 Проверка портов...${NC}"
    
    local ports=("8001:Flask WebApp" "3000:React Dev Server")
    
    for port_info in "${ports[@]}"; do
        local port=$(echo $port_info | cut -d: -f1)
        local service=$(echo $port_info | cut -d: -f2)
        
        if lsof -i ":$port" > /dev/null 2>&1; then
            local pid=$(lsof -i ":$port" | tail -n +2 | awk '{print $2}' | head -1)
            echo -e "   ${GREEN}✅ Порт $port ($service) занят PID: $pid${NC}"
        else
            echo -e "   ${YELLOW}⚠️ Порт $port ($service) свободен${NC}"
        fi
    done
}

# Функция для проверки Cloudflare Tunnel
check_cloudflare() {
    echo -e "${BLUE}🌐 Проверка Cloudflare Tunnel...${NC}"
    
    if pgrep -f "cloudflared" > /dev/null; then
        echo -e "${GREEN}✅ Cloudflare Tunnel запущен${NC}"
        
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
        done
        
        # Получаем URL из конфига
        WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/Users/denisfedko/news_ai_bot')
from config.cloudflare import get_webapp_url
print(get_webapp_url())
" 2>/dev/null || echo "https://immunology-restructuring-march-same.trycloudflare.com")
        
        echo -e "   ${CYAN}URL:${NC} $WEBAPP_URL"
        
        # Проверяем доступность
        if curl -s "$WEBAPP_URL/webapp" > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Cloudflare Tunnel доступен${NC}"
        else
            echo -e "   ${RED}❌ Cloudflare Tunnel недоступен${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Cloudflare Tunnel не запущен${NC}"
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
    
    # Проверяем PID файлы
    echo ""
    echo -e "${BLUE}📁 PID ФАЙЛЫ${NC}"
    echo "=================================================="
    
    if [ -f ".flask.pid" ]; then
        local flask_pid=$(cat .flask.pid)
        if ps -p $flask_pid > /dev/null 2>&1; then
            echo -e "${GREEN}✅ .flask.pid: $flask_pid (активен)${NC}"
        else
            echo -e "${RED}❌ .flask.pid: $flask_pid (неактивен)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ .flask.pid не найден${NC}"
    fi
    
    if [ -f ".bot.pid" ]; then
        local bot_pid=$(cat .bot.pid)
        if ps -p $bot_pid > /dev/null 2>&1; then
            echo -e "${GREEN}✅ .bot.pid: $bot_pid (активен)${NC}"
        else
            echo -e "${RED}❌ .bot.pid: $bot_pid (неактивен)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ .bot.pid не найден${NC}"
    fi
    
    # Проверяем lock файлы
    echo ""
    echo -e "${BLUE}🔒 LOCK ФАЙЛЫ${NC}"
    echo "=================================================="
    
    if [ -f ".flask.lock" ]; then
        echo -e "${YELLOW}⚠️ .flask.lock найден${NC}"
    fi
    
    if [ -f ".bot.lock" ]; then
        echo -e "${YELLOW}⚠️ .bot.lock найден${NC}"
    fi
    
    if [ ! -f ".flask.lock" ] && [ ! -f ".bot.lock" ]; then
        echo -e "${GREEN}✅ Lock файлы не найдены${NC}"
    fi
}

# Основная функция
main() {
    echo -e "${BLUE}🔍 Проверка статуса PulseAI сервисов${NC}"
    echo "=================================================="
    
    # Проверяем основные сервисы
    check_process_status "python3 src/webapp.py" "Flask WebApp" "8001" "http://localhost:8001/webapp"
    echo ""
    
    check_process_status "telegram_bot" "Telegram Bot" "" ""
    echo ""
    
    check_cloudflare
    echo ""
    
    check_ports
    echo ""
    
    show_summary
    
    echo ""
    echo -e "${BLUE}💡 КОМАНДЫ УПРАВЛЕНИЯ${NC}"
    echo "=================================================="
    echo -e "${CYAN}Запуск:${NC} ./start_services_safe.sh"
    echo -e "${CYAN}Остановка:${NC} ./stop_services.sh"
    echo -e "${CYAN}Проверка:${NC} ./check_processes.sh"
    echo -e "${CYAN}Логи:${NC} tail -f logs/*.log"
}

# Запуск основной функции
main "$@"
