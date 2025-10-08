#!/bin/bash

# Улучшенный скрипт для запуска всех сервисов PulseAI с контролем дубликатов
# Автор: AI Assistant
# Версия: 2.1

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для проверки запущен ли процесс
check_process() {
    local process_pattern="$1"
    local process_name="$2"
    
    if pgrep -f "$process_pattern" > /dev/null; then
        echo -e "${YELLOW}⚠️ $process_name уже запущен!${NC}"
        echo -e "${BLUE}🔍 Найденные процессы:${NC}"
        pgrep -f "$process_pattern" | while read pid; do
            echo "   PID: $pid - $(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')"
        done
        return 0
    else
        echo -e "${GREEN}✅ $process_name не запущен${NC}"
        return 1
    fi
}

# Функция для проверки порта
check_port() {
    local port="$1"
    local service_name="$2"
    
    if lsof -i ":$port" > /dev/null 2>&1; then
        local pid=$(lsof -i ":$port" | tail -n +2 | awk '{print $2}' | head -1)
        echo -e "${YELLOW}⚠️ Порт $port ($service_name) занят PID: $pid${NC}"
        return 0
    else
        echo -e "${GREEN}✅ Порт $port ($service_name) свободен${NC}"
        return 1
    fi
}

# Функция для безопасной остановки процессов
safe_stop_process() {
    local process_pattern="$1"
    local process_name="$2"
    local max_wait=10
    
    echo -e "${BLUE}🔄 Остановка $process_name...${NC}"
    
    # Мягкая остановка
    pkill -f "$process_pattern" 2>/dev/null || true
    
    # Ждем завершения
    local count=0
    while pgrep -f "$process_pattern" > /dev/null && [ $count -lt $max_wait ]; do
        sleep 1
        count=$((count + 1))
        echo -e "${YELLOW}⏳ Ожидание завершения $process_name... ($count/$max_wait)${NC}"
    done
    
    # Принудительная остановка если нужно
    if pgrep -f "$process_pattern" > /dev/null; then
        echo -e "${RED}⚠️ Принудительная остановка $process_name...${NC}"
        pkill -9 -f "$process_pattern" 2>/dev/null || true
        sleep 2
    fi
    
    # Финальная проверка
    if pgrep -f "$process_pattern" > /dev/null; then
        echo -e "${RED}❌ Не удалось остановить $process_name${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $process_name остановлен${NC}"
        return 0
    fi
}

# Функция для запуска процесса с контролем дубликатов
start_process_safe() {
    local process_pattern="$1"
    local process_name="$2"
    local start_command="$3"
    local check_url="$4"
    local pid_file="$5"
    local port="$6"
    
    echo -e "${BLUE}🚀 Запуск $process_name...${NC}"
    
    # Проверяем процесс
    local process_running=false
    if check_process "$process_pattern" "$process_name"; then
        process_running=true
    fi
    
    # Проверяем порт
    local port_occupied=false
    if [ -n "$port" ] && check_port "$port" "$process_name"; then
        port_occupied=true
    fi
    
    # Если процесс или порт заняты
    if [ "$process_running" = true ] || [ "$port_occupied" = true ]; then
        echo -e "${YELLOW}❓ Что делать с уже запущенным $process_name?${NC}"
        echo "1) Остановить и перезапустить"
        echo "2) Пропустить запуск"
        echo "3) Принудительно остановить все и перезапустить"
        read -p "Выберите опцию (1-3): " choice
        
        case $choice in
            1)
                safe_stop_process "$process_pattern" "$process_name"
                ;;
            2)
                echo -e "${YELLOW}⏭️ Пропускаем запуск $process_name${NC}"
                return 0
                ;;
            3)
                echo -e "${RED}💀 Принудительная остановка всех процессов $process_name...${NC}"
                pkill -9 -f "$process_pattern" 2>/dev/null || true
                sleep 2
                ;;
            *)
                echo -e "${RED}❌ Неверный выбор. Пропускаем запуск $process_name${NC}"
                return 0
                ;;
        esac
    fi
    
    # Запускаем процесс
    echo -e "${BLUE}▶️ Выполняем: $start_command${NC}"
    eval "$start_command" &
    local pid=$!
    
    # Сохраняем PID
    echo $pid > "$pid_file"
    echo -e "${GREEN}📝 PID сохранен в $pid_file: $pid${NC}"
    
    # Ждем запуска
    sleep 3
    
    # Проверяем что процесс запустился
    if ! ps -p $pid > /dev/null; then
        echo -e "${RED}❌ $process_name не запустился (PID $pid не найден)${NC}"
        rm -f "$pid_file"
        return 1
    fi
    
    # Проверяем доступность (если указан URL)
    if [ -n "$check_url" ]; then
        echo -e "${BLUE}🔍 Проверка доступности $process_name...${NC}"
        local count=0
        local max_checks=10
        
        while [ $count -lt $max_checks ]; do
            if curl -s "$check_url" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ $process_name доступен по адресу $check_url${NC}"
                return 0
            fi
            sleep 2
            count=$((count + 1))
            echo -e "${YELLOW}⏳ Ожидание $process_name... ($count/$max_checks)${NC}"
        done
        
        echo -e "${RED}❌ $process_name не отвечает на $check_url${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ $process_name запущен успешно (PID: $pid)${NC}"
    return 0
}

# Основная функция
main() {
    echo -e "${BLUE}🚀 Запуск PulseAI сервисов с контролем дубликатов...${NC}"
    echo "=================================================="
    
    # Устанавливаем PYTHONPATH
    export PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH"
    echo -e "${GREEN}✅ PYTHONPATH установлен${NC}"
    
    # Проверяем зависимости
    echo -e "${BLUE}🔍 Проверка зависимостей...${NC}"
    if ! command -v python3 > /dev/null; then
        echo -e "${RED}❌ Python3 не найден${NC}"
        exit 1
    fi
    
    if ! command -v curl > /dev/null; then
        echo -e "${RED}❌ curl не найден${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Все зависимости найдены${NC}"
    
    # Запускаем Flask WebApp
    start_process_safe \
        "python3 src/webapp.py" \
        "Flask WebApp" \
        "PYTHONPATH=\"/Users/denisfedko/news_ai_bot:\$PYTHONPATH\" python3 src/webapp.py" \
        "http://localhost:8001/webapp" \
        ".flask.pid" \
        "8001"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Не удалось запустить Flask WebApp${NC}"
        exit 1
    fi
    
    # Запускаем Telegram Bot
    start_process_safe \
        "python3 telegram_bot/bot.py\|python3 -m telegram_bot.bot" \
        "Telegram Bot" \
        "./run_bot.sh" \
        "" \
        ".bot.pid" \
        ""
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Не удалось запустить Telegram Bot${NC}"
        exit 1
    fi
    
    # Получаем URL из конфига
    echo -e "${BLUE}🌐 Получение Cloudflare URL...${NC}"
    WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/Users/denisfedko/news_ai_bot')
from config.cloudflare import get_webapp_url
print(get_webapp_url())
" 2>/dev/null || echo "https://immunology-restructuring-march-same.trycloudflare.com")
    
    # Финальный статус
    echo ""
    echo -e "${GREEN}🎉 Все сервисы запущены успешно!${NC}"
    echo "=================================================="
    echo -e "${BLUE}📱 WebApp:${NC} $WEBAPP_URL/webapp"
    echo -e "${BLUE}🔗 API:${NC} http://localhost:8001/api"
    echo -e "${BLUE}🤖 Telegram Bot:${NC} @PulseAIDigest_bot"
    echo ""
    echo -e "${YELLOW}💡 Для остановки: ./stop_services.sh${NC}"
    echo -e "${YELLOW}💡 Для проверки статуса: ./check_processes_safe.sh${NC}"
    
    # Показываем текущие процессы
    echo ""
    echo -e "${BLUE}📊 Текущие процессы PulseAI:${NC}"
    echo "=================================================="
    
    if pgrep -f "python3 src/webapp.py" > /dev/null; then
        echo -e "${GREEN}✅ Flask WebApp:${NC}"
        pgrep -f "python3 src/webapp.py" | while read pid; do
            echo "   PID: $pid - $(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')"
        done
    fi
    
    if pgrep -f "telegram_bot" > /dev/null; then
        echo -e "${GREEN}✅ Telegram Bot:${NC}"
        pgrep -f "telegram_bot" | while read pid; do
            echo "   PID: $pid - $(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')"
        done
    fi
    
    if pgrep -f "cloudflared" > /dev/null; then
        echo -e "${GREEN}✅ Cloudflare Tunnel:${NC}"
        pgrep -f "cloudflared" | while read pid; do
            echo "   PID: $pid - $(ps -p $pid -o command= 2>/dev/null || echo 'Процесс не найден')"
        done
    fi
}

# Запуск основной функции
main "$@"