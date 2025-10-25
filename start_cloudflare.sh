#!/bin/bash

# Скрипт для запуска Cloudflare Tunnel
# Использование: ./start_cloudflare.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 ЗАПУСК CLOUDFLARE TUNNEL${NC}"
echo "==============================="

# Проверяем установку cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}❌ cloudflared не установлен!${NC}"
    echo -e "${YELLOW}💡 Установите cloudflared:${NC}"
    echo "   brew install cloudflared"
    echo "   или скачайте с https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
    exit 1
fi

# Проверяем существование .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo -e "${YELLOW}💡 Создайте .env из .env.example${NC}"
    exit 1
fi

# Останавливаем старые процессы cloudflared
echo -e "${BLUE}🔄 Остановка старых процессов Cloudflare Tunnel...${NC}"
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 2

# Проверяем, что Flask запущен
if ! curl -s http://localhost:8001/webapp > /dev/null 2>&1; then
    echo -e "${RED}❌ Flask WebApp не запущен на порту 8001!${NC}"
    echo -e "${YELLOW}💡 Сначала запустите Flask: ./start_services.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Flask WebApp доступен${NC}"

# Запускаем Cloudflare Tunnel
echo -e "${BLUE}🚀 Запуск Cloudflare Tunnel...${NC}"
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &
CLOUDFLARE_PID=$!

echo "INFO" "Cloudflare Tunnel запущен с PID: $CLOUDFLARE_PID" >> logs/cloudflare.log

# Ждем запуска и извлекаем URL
echo -e "${BLUE}⏳ Ожидание получения URL...${NC}"
sleep 5

# Извлекаем URL из логов
NEW_URL=$(grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" logs/cloudflare.log | tail -1)

if [ -z "$NEW_URL" ]; then
    echo -e "${RED}❌ Не удалось получить URL из логов${NC}"
    echo -e "${YELLOW}📋 Логи Cloudflare:${NC}"
    tail -10 logs/cloudflare.log
    exit 1
fi

echo -e "${GREEN}✅ Cloudflare Tunnel запущен${NC}"
echo -e "${CYAN}🌐 URL: $NEW_URL${NC}"

# Обновляем .env файл
echo -e "${BLUE}📝 Обновление .env файла...${NC}"
if grep -q "CLOUDFLARE_TUNNEL_URL=" .env; then
    sed -i '' "s|CLOUDFLARE_TUNNEL_URL=.*|CLOUDFLARE_TUNNEL_URL=$NEW_URL|" .env
else
    echo "CLOUDFLARE_TUNNEL_URL=$NEW_URL" >> .env
fi

# Обновляем WEBAPP_URL
if grep -q "WEBAPP_URL=" .env; then
    sed -i '' "s|WEBAPP_URL=.*|WEBAPP_URL=$NEW_URL|" .env
else
    echo "WEBAPP_URL=$NEW_URL" >> .env
fi

echo -e "${GREEN}✅ .env файл обновлен${NC}"

# Сохраняем PID
echo $CLOUDFLARE_PID > .cloudflare.pid

echo ""
echo -e "${GREEN}🎉 CLOUDFLARE TUNNEL ЗАПУЩЕН!${NC}"
echo "========================"
echo -e "${CYAN}🌐 URL: $NEW_URL${NC}"
echo -e "${CYAN}📱 WebApp: $NEW_URL/webapp${NC}"
echo -e "${CYAN}🔌 API: $NEW_URL/api${NC}"
echo -e "${CYAN}📋 Лог: logs/cloudflare.log${NC}"
echo ""
echo -e "${YELLOW}💡 Для остановки: kill $CLOUDFLARE_PID${NC}"
echo -e "${YELLOW}🔍 Для проверки: ./check_processes.sh${NC}"
