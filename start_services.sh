#!/bin/bash

# Скрипт для запуска всех сервисов PulseAI

echo "🚀 Запуск PulseAI сервисов..."

# Убиваем старые процессы
echo "🔄 Остановка старых процессов..."
pkill -f "python3 src/webapp.py" 2>/dev/null
pkill -f "python3 telegram_bot/bot.py" 2>/dev/null
sleep 2

# Устанавливаем PYTHONPATH
export PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH"

# Запускаем Flask
echo "🌐 Запуск Flask WebApp..."
PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH" python3 src/webapp.py &
FLASK_PID=$!

# Ждем запуска Flask
sleep 3

# Проверяем что Flask запустился
if curl -s http://localhost:8001/webapp > /dev/null; then
    echo "✅ Flask WebApp запущен успешно"
else
    echo "❌ Flask WebApp не запустился"
    exit 1
fi

# Запускаем Telegram Bot
echo "🤖 Запуск Telegram Bot..."
./run_bot.sh &
BOT_PID=$!

# Ждем запуска Bot
sleep 3

# Проверяем что Bot запустился
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Telegram Bot запущен успешно"
else
    echo "❌ Telegram Bot не запустился"
    exit 1
fi

# Получаем URL из конфига
WEBAPP_URL=$(python3 -c "
import sys
sys.path.append('/Users/denisfedko/news_ai_bot')
from config.cloudflare import get_webapp_url
print(get_webapp_url())
")

echo "🎉 Все сервисы запущены!"
echo "📱 WebApp: $WEBAPP_URL"
echo "🤖 Telegram Bot готов к работе"

# Сохраняем PID для остановки
echo $FLASK_PID > .flask.pid
echo $BOT_PID > .bot.pid

echo "💡 Для остановки: ./stop_services.sh"

