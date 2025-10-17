#!/bin/bash

# Скрипт для запуска Flask с Admin Panel

echo "🚀 Запуск PulseAI с Admin Panel..."

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

# Проверяем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его: python -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем, что React собран
if [ ! -d "webapp/dist" ]; then
    echo "⚠️  React приложение не собрано"
    echo "Собираем..."
    cd webapp
    npm run build
    cd ..
fi

# Запускаем Flask
echo "✅ Запуск Flask на http://localhost:8001"
echo "✅ Admin Panel: http://localhost:8001/admin/dashboard"
echo ""
python src/webapp.py


