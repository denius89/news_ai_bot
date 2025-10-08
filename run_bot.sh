#!/bin/bash

# Wrapper скрипт для запуска Telegram Bot с защитой от множественного запуска

# Устанавливаем рабочую директорию
cd /Users/denisfedko/news_ai_bot

# Lock файл для предотвращения множественного запуска
LOCK_FILE=".bot.lock"
PID_FILE=".bot.pid"

# Проверяем, не запущен ли уже бот
if [ -f "$LOCK_FILE" ]; then
    lock_pid=$(cat "$LOCK_FILE")
    if ps -p "$lock_pid" > /dev/null 2>&1; then
        echo "❌ Telegram Bot уже запущен (PID: $lock_pid)"
        echo "💡 Для остановки: ./stop_services.sh"
        exit 1
    else
        echo "🧹 Удаляем устаревший lock файл"
        rm -f "$LOCK_FILE"
    fi
fi

# Проверяем по имени процесса
if pgrep -f "python3 -m telegram_bot.bot" > /dev/null; then
    echo "❌ Telegram Bot уже запущен (найден по имени процесса)"
    echo "💡 Для остановки: ./stop_services.sh"
    exit 1
fi

# Устанавливаем PYTHONPATH
export PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH"

# Проверяем, что все зависимости доступны
echo "🔍 Проверка зависимостей..."
python3 -c "import utils.ai.ai_client; print('✅ utils.ai.ai_client OK')" || {
    echo "❌ Ошибка импорта utils.ai.ai_client"
    exit 1
}

python3 -c "import config.core.settings; print('✅ config.core.settings OK')" || {
    echo "❌ Ошибка импорта config.core.settings"
    exit 1
}

python3 -c "import telegram_bot.handlers; print('✅ telegram_bot.handlers OK')" || {
    echo "❌ Ошибка импорта telegram_bot.handlers"
    exit 1
}

# Создаем lock файл
echo $$ > "$LOCK_FILE"

# Функция очистки при выходе
cleanup() {
    echo "🧹 Очистка lock файлов..."
    rm -f "$LOCK_FILE"
    rm -f "$PID_FILE"
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGTERM SIGINT

echo "🚀 Запуск Telegram Bot..."
PYTHONPATH="/Users/denisfedko/news_ai_bot:$PYTHONPATH" python3 -m telegram_bot.bot &
BOT_PID=$!

# Сохраняем PID
echo $BOT_PID > "$PID_FILE"

# Ждем завершения процесса
wait $BOT_PID

# Очистка при завершении
cleanup
