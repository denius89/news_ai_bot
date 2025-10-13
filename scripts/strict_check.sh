#!/bin/bash

# 🔍 Строгая проверка качества кода
# Автор: AI Assistant
# Версия: 1.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Строгая проверка качества кода${NC}"
echo "=========================================="

# Функция для проверки доступности инструментов
check_tools() {
    echo -e "${BLUE}🔍 Проверка доступности инструментов...${NC}"
    
    if ! python3 -c "import black" 2>/dev/null; then
        echo -e "${RED}❌ Black недоступен. Установите: pip install black${NC}"
        exit 1
    fi
    
    if ! python3 -c "import flake8" 2>/dev/null; then
        echo -e "${RED}❌ Flake8 недоступен. Установите: pip install flake8${NC}"
        exit 1
    fi
    
    if python3 -c "import isort" 2>/dev/null; then
        echo -e "${GREEN}✅ isort доступен${NC}"
        HAS_ISORT=true
    else
        echo -e "${YELLOW}⚠️ isort недоступен (опционально)${NC}"
        HAS_ISORT=false
    fi
    
    echo -e "${GREEN}✅ Все необходимые инструменты доступны${NC}"
}

# Функция для строгой проверки качества кода
strict_code_check() {
    echo -e "${BLUE}🧹 Строгая проверка качества кода...${NC}"
    
    # 1. Black форматирование
    echo -e "${YELLOW}📝 Проверка Black форматирования...${NC}"
    if ! python3 -m black --check --quiet .; then
        echo -e "${RED}❌ Black нашел проблемы форматирования${NC}"
        echo -e "${YELLOW}💡 Примените форматирование: python3 -m black .${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Black форматирование корректно${NC}"
    
    # 2. Строгая Flake8 проверка стиля
    echo -e "${YELLOW}🔍 Строгая проверка Flake8...${NC}"
    if ! python3 -m flake8 --config=.flake8 .; then
        echo -e "${RED}❌ Flake8 нашел критические проблемы в коде${NC}"
        echo -e "${YELLOW}💡 Исправьте ошибки перед коммитом:${NC}"
        python3 -m flake8 --config=.flake8 .
        exit 1
    fi
    echo -e "${GREEN}✅ Flake8 строгая проверка пройдена${NC}"
    
    # 3. Проверка импортов (если isort доступен)
    if [ "$HAS_ISORT" = true ]; then
        echo -e "${YELLOW}📦 Проверка сортировки импортов...${NC}"
        if ! python3 -m isort --check-only --quiet .; then
            echo -e "${RED}❌ isort нашел проблемы с импортами${NC}"
            echo -e "${YELLOW}💡 Отсортируйте импорты: python3 -m isort .${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ Импорты отсортированы корректно${NC}"
    else
        echo -e "${YELLOW}⚠️ isort недоступен, пропускаю проверку импортов${NC}"
    fi
}

# Функция для показа статистики
show_stats() {
    echo -e "${BLUE}📊 Статистика кода:${NC}"
    
    # Подсчет строк кода
    PYTHON_FILES=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
    TOTAL_LINES=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "./node_modules/*" -exec wc -l {} + | tail -1 | awk '{print $1}')
    
    echo -e "  - Python файлов: ${PYTHON_FILES}"
    echo -e "  - Всего строк кода: ${TOTAL_LINES}"
    
    # Проверка сложности (если доступен radon)
    if python3 -c "import radon" 2>/dev/null; then
        echo -e "${YELLOW}📈 Анализ сложности кода...${NC}"
        python3 -m radon cc . --min B 2>/dev/null || echo -e "${YELLOW}⚠️ Некоторые функции имеют высокую сложность${NC}"
    fi
}

# Основная функция
main() {
    # Проверяем что мы в git репозитории
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Это не git репозиторий${NC}"
        exit 1
    fi
    
    # Проверяем инструменты
    check_tools
    
    # Строгая проверка качества кода
    strict_code_check
    
    # Показываем статистику
    show_stats
    
    echo ""
    echo -e "${GREEN}🎉 Все проверки пройдены успешно!${NC}"
    echo -e "${BLUE}💡 Код готов к коммиту${NC}"
}

# Запуск основной функции
main "$@"
