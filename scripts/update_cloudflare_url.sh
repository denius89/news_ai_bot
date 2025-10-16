#!/bin/bash

# Скрипт автоматического обновления Cloudflare URL
# Использование: ./scripts/update_cloudflare_url.sh OLD_URL NEW_URL
# Пример: ./scripts/update_cloudflare_url.sh old-url-example new-url-example

set -e  # Остановка при ошибке

OLD_URL=$1
NEW_URL=$2

if [ -z "$OLD_URL" ] || [ -z "$NEW_URL" ]; then
    echo "❌ Использование: $0 OLD_URL NEW_URL"
    echo "   Пример: $0 old-url-example new-url-example"
    echo ""
    echo "   OLD_URL - часть старого URL (без https:// и .trycloudflare.com)"
    echo "   NEW_URL - часть нового URL (без https:// и .trycloudflare.com)"
    exit 1
fi

echo "🔄 Обновление Cloudflare URL в PulseAI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Старый URL: https://$OLD_URL.trycloudflare.com"
echo "   Новый URL:  https://$NEW_URL.trycloudflare.com"
echo ""
echo "Нажмите Enter для продолжения или Ctrl+C для отмены..."
read

cd "$(dirname "$0")/.."

# 1. Обновить Python конфигурацию
echo ""
echo "📝 [1/7] Обновление config/core/cloudflare.py..."
if [ -f "config/core/cloudflare.py" ]; then
    sed -i '' "s|$OLD_URL|$NEW_URL|g" config/core/cloudflare.py
    echo "   ✅ config/core/cloudflare.py"
else
    echo "   ⚠️ Файл не найден: config/core/cloudflare.py"
fi

# 2. Обновить .env файлы (КРИТИЧНО!)
echo ""
echo "📝 [2/7] Обновление .env файлов..."
if [ -f ".env" ]; then
    sed -i '' "s|https://$OLD_URL.trycloudflare.com|https://$NEW_URL.trycloudflare.com|g" .env
    echo "   ✅ .env (корневой)"
else
    echo "   ⚠️ Файл не найден: .env"
fi

if [ -f "config_files/environment/.env" ]; then
    sed -i '' "s|https://$OLD_URL.trycloudflare.com|https://$NEW_URL.trycloudflare.com|g" config_files/environment/.env
    echo "   ✅ config_files/environment/.env"
else
    echo "   ⚠️ Файл не найден: config_files/environment/.env"
fi

# 3. Обновить cloudflare-tunnel.yaml
echo ""
echo "📝 [3/7] Обновление cloudflare-tunnel.yaml..."
if [ -f "cloudflare-tunnel.yaml" ]; then
    sed -i '' "s|$OLD_URL|$NEW_URL|g" cloudflare-tunnel.yaml
    echo "   ✅ cloudflare-tunnel.yaml"
else
    echo "   ⚠️ Файл не найден: cloudflare-tunnel.yaml"
fi

# 4. Обновить README.md
echo ""
echo "📝 [4/7] Обновление README.md..."
if [ -f "README.md" ]; then
    sed -i '' "s|$OLD_URL|$NEW_URL|g" README.md
    echo "   ✅ README.md"
fi

# 5. Обновить остальную документацию
echo ""
echo "📝 [5/7] Обновление документации..."
FILES=(
    "DEPLOYMENT_STATUS.md"
    "CLOUDFLARE_URL_AUDIT_REPORT.md"
    "CHANGELOG.md"
    "FINAL_SESSION_SUMMARY.md"
    "CURRENT_SERVICES_STATUS.md"
    "WEBAPP_FIX_CYRILLIC_HEADERS.md"
    "docs/reports/FINAL_TODO_REPORT.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        sed -i '' "s|$OLD_URL|$NEW_URL|g" "$file"
        echo "   ✅ $file"
    fi
done

# 6. Перезапустить Flask WebApp
echo ""
echo "🔄 [6/7] Перезапуск Flask WebApp..."
pkill -f "src/webapp.py" 2>/dev/null || echo "   ℹ️ Flask не был запущен"
sleep 2
python3 src/webapp.py > logs/webapp.log 2>&1 &
sleep 5

if ps aux | grep "src/webapp.py" | grep -v grep > /dev/null; then
    FLASK_PID=$(ps aux | grep "src/webapp.py" | grep -v grep | head -1 | awk '{print $2}')
    echo "   ✅ Flask перезапущен (PID: $FLASK_PID)"
else
    echo "   ❌ Flask не запустился! Проверьте logs/webapp.log"
    exit 1
fi

# 7. Перезапустить Telegram Bot
echo ""
echo "🔄 [7/7] Перезапуск Telegram Bot..."
pkill -f "telegram_bot/bot.py" 2>/dev/null || echo "   ℹ️ Bot не был запущен"
sleep 2
PYTHONPATH=$(pwd):$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &
sleep 5

if ps aux | grep "telegram_bot/bot.py" | grep -v grep > /dev/null; then
    BOT_PID=$(ps aux | grep "telegram_bot/bot.py" | grep -v grep | head -1 | awk '{print $2}')
    echo "   ✅ Telegram Bot перезапущен (PID: $BOT_PID)"
else
    echo "   ❌ Bot не запустился! Проверьте logs/bot.log"
    exit 1
fi

# 8. Финальная проверка
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Проверка результата..."
echo ""

# Проверить загруженный URL
LOADED_URL=$(python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)" 2>/dev/null)
if [ "$LOADED_URL" = "https://$NEW_URL.trycloudflare.com" ]; then
    echo "✅ WEBAPP_URL загружен правильно:"
    echo "   $LOADED_URL"
else
    echo "❌ ОШИБКА: WEBAPP_URL загружен неправильно!"
    echo "   Ожидалось: https://$NEW_URL.trycloudflare.com"
    echo "   Получено:  $LOADED_URL"
    exit 1
fi

echo ""

# Проверить локальный API
if curl -s "http://localhost:8001/api/health" | grep -q "success"; then
    echo "✅ Flask API отвечает локально"
else
    echo "⚠️ Flask API не отвечает локально"
fi

# Проверить через Cloudflare
echo ""
echo "🌐 Проверка доступности через Cloudflare..."
sleep 2
if curl -s "https://$NEW_URL.trycloudflare.com/api/health" | grep -q "success"; then
    echo "✅ API доступен через Cloudflare Tunnel"
else
    echo "⚠️ API пока не доступен через Cloudflare (может потребоваться время)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Обновление завершено успешно!"
echo ""
echo "📊 Статус сервисов:"
echo "   • Flask WebApp: PID $FLASK_PID"
echo "   • Telegram Bot: PID $BOT_PID"
echo "   • Cloudflare URL: https://$NEW_URL.trycloudflare.com"
echo ""
echo "🔗 Endpoints для проверки:"
echo "   • WebApp:  https://$NEW_URL.trycloudflare.com/webapp"
echo "   • Admin:   https://$NEW_URL.trycloudflare.com/admin"
echo "   • Health:  https://$NEW_URL.trycloudflare.com/api/health"
echo ""
echo "📱 Telegram Bot:"
echo "   • Отправьте /dashboard боту @PulseAIDigest_bot"
echo "   • Проверьте, что WebApp открывается с нового URL"
echo ""
echo "💡 Создан отчет: CLOUDFLARE_UPDATE_REPORT.md"
echo ""

