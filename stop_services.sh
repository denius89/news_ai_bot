#!/bin/bash

# Скрипт для остановки всех сервисов PulseAI

echo "🛑 Остановка PulseAI сервисов..."

# Останавливаем по PID файлам
if [ -f .flask.pid ]; then
    FLASK_PID=$(cat .flask.pid)
    if ps -p $FLASK_PID > /dev/null; then
        echo "🔄 Остановка Flask WebApp (PID: $FLASK_PID)..."
        kill $FLASK_PID
        rm .flask.pid
    fi
fi

if [ -f .bot.pid ]; then
    BOT_PID=$(cat .bot.pid)
    if ps -p $BOT_PID > /dev/null; then
        echo "🔄 Остановка Telegram Bot (PID: $BOT_PID)..."
        kill $BOT_PID
        rm .bot.pid
    fi
fi

# Принудительная остановка по имени процесса
pkill -f "python3 webapp.py" 2>/dev/null
pkill -f "python3 telegram_bot/bot.py" 2>/dev/null
pkill -f "python3 -m telegram_bot.bot" 2>/dev/null

# Очищаем lock файлы
echo "🧹 Очистка lock файлов..."
rm -f .flask.lock .bot.lock .flask.pid .bot.pid

echo "✅ Все сервисы остановлены"
echo "💡 Cloudflare Tunnel продолжает работать"

