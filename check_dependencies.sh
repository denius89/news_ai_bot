#!/bin/bash

# Скрипт проверки зависимостей PulseAI

echo "🔍 Проверка зависимостей PulseAI..."

# Устанавливаем PYTHONPATH
export PYTHONPATH="/home/user/news_ai_bot:$PYTHONPATH"

# Переходим в рабочую директорию
cd /home/user/news_ai_bot

# Проверяем основные модули
echo "📦 Проверка основных модулей..."

python3 -c "import utils.ai_client; print('✅ utils.ai_client')" || echo "❌ utils.ai_client"
python3 -c "import config.settings; print('✅ config.settings')" || echo "❌ config.settings"
python3 -c "import database.service; print('✅ database.service')" || echo "❌ database.service"
python3 -c "import services.unified_digest_service; print('✅ services.unified_digest_service')" || echo "❌ services.unified_digest_service"
python3 -c "import telegram_bot.handlers; print('✅ telegram_bot.handlers')" || echo "❌ telegram_bot.handlers"

# Проверяем переменные окружения
echo "🔧 Проверка переменных окружения..."
python3 -c "from config.settings import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY; print('✅ TELEGRAM_BOT_TOKEN:', 'OK' if TELEGRAM_BOT_TOKEN else 'MISSING'); print('✅ OPENAI_API_KEY:', 'OK' if OPENAI_API_KEY else 'MISSING')"

# Проверяем подключение к базе данных
echo "🗄️ Проверка подключения к БД..."
python3 -c "from database.service import get_sync_service; service = get_sync_service(); print('✅ База данных доступна')" || echo "❌ Проблемы с БД"

echo "✅ Проверка завершена!"
