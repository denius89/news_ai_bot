#!/bin/bash

# Скрипт для запуска Flask с Admin Panel

echo "🚀 Запуск PulseAI с Admin Panel..."

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


