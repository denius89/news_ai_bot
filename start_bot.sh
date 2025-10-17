#!/bin/bash

# Автоматическое восстановление .env файла
if [ ! -f ".env" ]; then
    echo "⚠️ Файл .env отсутствует"
    
    # Проверяем наличие бэкапов в git stash
    if git stash list | grep -q "env-backup\|production config\|initial backup" 2>/dev/null; then
        echo "📦 Восстанавливаю .env из последнего бэкапа..."
        
        # Восстанавливаем без удаления из стеша
        if git checkout stash@{0} -- .env 2>/dev/null; then
            # Убираем из staged area
            git restore --staged .env 2>/dev/null || true
            echo "✅ Файл .env восстановлен из бэкапа"
        else
            echo "❌ Не удалось восстановить .env"
            echo "💡 Запустите вручную: env-restore или создайте из .env.example"
            exit 1
        fi
    else
        echo "❌ Бэкапы .env не найдены в git stash"
        echo "💡 Создайте .env из .env.example и настройте переменные"
        exit 1
    fi
else
    echo "✅ Файл .env обнаружен"
fi

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Activate virtual environment and start bot
source venv/bin/activate
python -m telegram_bot.bot
