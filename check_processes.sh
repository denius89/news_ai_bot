#!/bin/bash

# Скрипт проверки запущенных процессов PulseAI

check_process() {
    local process_name="$1"
    local lock_file="$2"
    
    # Проверяем по имени процесса
    local pid=$(pgrep -f "$process_name" | head -1)
    
    if [ -n "$pid" ]; then
        echo "⚠️ Процесс $process_name уже запущен (PID: $pid)"
        
        # Проверяем lock файл
        if [ -f "$lock_file" ]; then
            local lock_pid=$(cat "$lock_file")
            if [ "$lock_pid" = "$pid" ]; then
                echo "✅ Lock файл соответствует процессу"
                return 0
            else
                echo "❌ Lock файл устарел, удаляем"
                rm -f "$lock_file"
            fi
        fi
        
        return 1
    else
        echo "✅ Процесс $process_name не запущен"
        return 0
    fi
}

echo "🔍 Проверка запущенных процессов PulseAI..."

# Проверяем Flask WebApp
check_process "python3 webapp.py" ".flask.pid"
flask_running=$?

# Проверяем Telegram Bot
check_process "python3 -m telegram_bot.bot" ".bot.pid"
bot_running=$?

# Проверяем другие экземпляры бота
other_bots=$(pgrep -f "telegram_bot" | wc -l)
if [ "$other_bots" -gt 1 ]; then
    echo "❌ Обнаружено $other_bots экземпляров Telegram Bot!"
    echo "🔧 Рекомендуется остановить все процессы: ./stop_services.sh"
    exit 1
fi

echo "📊 Статус:"
echo "  Flask WebApp: $([ $flask_running -eq 1 ] && echo "запущен" || echo "остановлен")"
echo "  Telegram Bot: $([ $bot_running -eq 1 ] && echo "запущен" || echo "остановлен")"

if [ $flask_running -eq 1 ] && [ $bot_running -eq 1 ]; then
    echo "✅ Все сервисы работают"
    exit 0
else
    echo "⚠️ Некоторые сервисы не запущены"
    exit 1
fi
