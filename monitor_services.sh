#!/bin/bash

# Скрипт для мониторинга и автоматического восстановления сервисов
# Автор: PulseAI System
# Дата: 2025-10-09

echo "🔍 МОНИТОРИНГ СЕРВИСОВ PULSEAI"
echo "==============================="

# Функция проверки Flask
check_flask() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health)
    if [ "$response" = "200" ]; then
        echo "✅ Flask WebApp: работает (HTTP $response)"
        return 0
    else
        echo "❌ Flask WebApp: не работает (HTTP $response)"
        return 1
    fi
}

# Функция проверки Telegram Bot
check_telegram_bot() {
    local processes=$(ps aux | grep "telegram_bot" | grep -v grep | wc -l)
    if [ "$processes" -gt 0 ]; then
        echo "✅ Telegram Bot: работает ($processes процессов)"
        return 0
    else
        echo "❌ Telegram Bot: не работает"
        return 1
    fi
}

# Функция проверки Cloudflare туннеля
check_cloudflare() {
    local processes=$(ps aux | grep "cloudflared" | grep -v grep | wc -l)
    if [ "$processes" -gt 0 ]; then
        echo "✅ Cloudflare Tunnel: работает ($processes процессов)"
        return 0
    else
        echo "❌ Cloudflare Tunnel: не работает"
        return 1
    fi
}

# Функция перезапуска Flask
restart_flask() {
    echo "🔄 Перезапуск Flask WebApp..."
    pkill -f "src/webapp.py" 2>/dev/null
    sleep 3
    python3 src/webapp.py &
    sleep 5
    
    if check_flask; then
        echo "✅ Flask WebApp успешно перезапущен"
        return 0
    else
        echo "❌ Не удалось перезапустить Flask WebApp"
        return 1
    fi
}

# Функция перезапуска Telegram Bot
restart_telegram_bot() {
    echo "🔄 Перезапуск Telegram Bot..."
    pkill -f "telegram_bot" 2>/dev/null
    sleep 3
    python3 telegram_bot/main.py &
    sleep 5
    
    if check_telegram_bot; then
        echo "✅ Telegram Bot успешно перезапущен"
        return 0
    else
        echo "❌ Не удалось перезапустить Telegram Bot"
        return 1
    fi
}

# Основная функция мониторинга
monitor_services() {
    echo "📊 Статус сервисов на $(date):"
    echo "-------------------------------"
    
    local flask_ok=0
    local telegram_ok=0
    local cloudflare_ok=0
    
    # Проверяем все сервисы
    if check_flask; then
        flask_ok=1
    fi
    
    if check_telegram_bot; then
        telegram_ok=1
    fi
    
    if check_cloudflare; then
        cloudflare_ok=1
    fi
    
    echo "-------------------------------"
    
    # Автоматическое восстановление
    if [ "$flask_ok" -eq 0 ]; then
        echo "⚠️ Flask WebApp недоступен, пытаемся восстановить..."
        restart_flask
    fi
    
    if [ "$telegram_ok" -eq 0 ]; then
        echo "⚠️ Telegram Bot недоступен, пытаемся восстановить..."
        restart_telegram_bot
    fi
    
    if [ "$cloudflare_ok" -eq 0 ]; then
        echo "⚠️ Cloudflare Tunnel недоступен"
        echo "💡 Запустите вручную: cloudflared tunnel --url http://localhost:8001"
    fi
    
    # Финальный статус
    echo ""
    if [ "$flask_ok" -eq 1 ] && [ "$telegram_ok" -eq 1 ] && [ "$cloudflare_ok" -eq 1 ]; then
        echo "🎉 Все сервисы работают нормально!"
    else
        echo "⚠️ Некоторые сервисы требуют внимания"
    fi
}

# Запуск мониторинга
monitor_services
