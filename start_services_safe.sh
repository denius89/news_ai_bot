#!/bin/bash

# Улучшенный скрипт запуска с проверками
# Предотвращает проблемы с импортами и путями

set -e  # Остановка при ошибке

echo "🛡️ ЗАПУСК PULSEAI С ПРОВЕРКАМИ"
echo "==============================="

# Проверяем здоровье проекта
echo "🔍 Проверка здоровья проекта..."
python3 scripts/health_check.py || {
    echo "❌ Проверка здоровья не пройдена!"
    echo "💡 Исправьте ошибки и попробуйте снова"
    exit 1
}

echo ""
echo "✅ Проект здоров, продолжаем запуск..."

# Устанавливаем переменные окружения
export PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH"

# Останавливаем старые процессы
echo "🔄 Остановка старых процессов..."
pkill -f "python.*webapp.py" 2>/dev/null || true
pkill -f "python.*telegram_bot" 2>/dev/null || true
sleep 2

# Запускаем Flask WebApp
echo "🌐 Запуск Flask WebApp..."
python3 src/webapp.py > logs/webapp.log 2>&1 &
FLASK_PID=$!

# Ждем запуска Flask
sleep 3

# Проверяем что Flask запустился
if curl -s http://localhost:8001/webapp > /dev/null; then
    echo "✅ Flask WebApp запущен успешно"
else
    echo "❌ Flask WebApp не запустился"
    echo "📋 Логи Flask:"
    tail -10 logs/webapp.log
    exit 1
fi

# Запускаем Telegram Bot
echo "🤖 Запуск Telegram Bot..."
python3 -m telegram_bot.bot > logs/bot.log 2>&1 &
BOT_PID=$!

# Ждем запуска Bot
sleep 3

# Проверяем что Bot запустился
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Telegram Bot запущен успешно"
else
    echo "❌ Telegram Bot не запустился"
    echo "📋 Логи Bot:"
    tail -10 logs/bot.log
    exit 1
fi

# Получаем URL из конфига
WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/Users/denisfedko/news_ai_bot')
from config.core.cloudflare import get_webapp_url
print(get_webapp_url())
")

echo ""
echo "🎉 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================"
echo "📱 WebApp: $WEBAPP_URL"
echo "🤖 Telegram Bot: готов к работе"
echo "🌐 Flask: http://localhost:8001/webapp"
echo ""
echo "💡 Для остановки: ./stop_services.sh"

# Сохраняем PID для остановки
echo $FLASK_PID > .flask.pid
echo $BOT_PID > .bot.pid