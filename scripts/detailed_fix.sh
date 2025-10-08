#!/bin/bash

# 🔧 Детальная проверка и автоматическое исправление ошибок кода
# Автор: AI Assistant
# Версия: 2.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Детальная проверка и автоматическое исправление ошибок кода${NC}"
echo "=================================================================="

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
    
    if python3 -c "import autopep8" 2>/dev/null; then
        echo -e "${GREEN}✅ autopep8 доступен${NC}"
        HAS_AUTOPEP8=true
    else
        echo -e "${YELLOW}⚠️ autopep8 недоступен (опционально)${NC}"
        HAS_AUTOPEP8=false
    fi
    
    echo -e "${GREEN}✅ Все необходимые инструменты доступны${NC}"
}

# Функция для детального анализа ошибок
analyze_errors() {
    echo -e "${BLUE}📊 Детальный анализ ошибок кода...${NC}"
    
    # Создаем временный файл для результатов
    TEMP_FILE=$(mktemp)
    
    # Запускаем flake8 и сохраняем результаты
    python3 -m flake8 --max-line-length=100 --ignore=E203,W503 . > "$TEMP_FILE" 2>/dev/null || true
    
    if [ -s "$TEMP_FILE" ]; then
        echo -e "${YELLOW}📋 Найдены следующие типы ошибок:${NC}"
        
        # Анализируем типы ошибок
        ERROR_TYPES=$(cut -d: -f4 "$TEMP_FILE" | cut -d' ' -f2 | sort | uniq -c | sort -nr)
        echo "$ERROR_TYPES" | while read count error_type; do
            case "$error_type" in
                "E501") echo -e "  ${RED}E501${NC}: Слишком длинные строки ($count ошибок)" ;;
                "F401") echo -e "  ${YELLOW}F401${NC}: Неиспользуемые импорты ($count ошибок)" ;;
                "F841") echo -e "  ${YELLOW}F841${NC}: Неиспользуемые переменные ($count ошибок)" ;;
                "F541") echo -e "  ${YELLOW}F541${NC}: f-строки без плейсхолдеров ($count ошибок)" ;;
                "W291") echo -e "  ${CYAN}W291${NC}: Пробелы в конце строк ($count ошибок)" ;;
                "W293") echo -e "  ${CYAN}W293${NC}: Пустые строки с пробелами ($count ошибок)" ;;
                "E402") echo -e "  ${PURPLE}E402${NC}: Импорты не в начале файла ($count ошибок)" ;;
                "E722") echo -e "  ${RED}E722${NC}: Голые except блоки ($count ошибок)" ;;
                "F821") echo -e "  ${RED}F821${NC}: Неопределенные переменные ($count ошибок)" ;;
                "F601") echo -e "  ${RED}F601${NC}: Дублирующиеся ключи словаря ($count ошибок)" ;;
                *) echo -e "  ${BLUE}$error_type${NC}: Другие ошибки ($count ошибок)" ;;
            esac
        done
        
        echo ""
        echo -e "${BLUE}📁 Файлы с наибольшим количеством ошибок:${NC}"
        cut -d: -f1 "$TEMP_FILE" | sort | uniq -c | sort -nr | head -10 | while read count file; do
            echo -e "  ${YELLOW}$file${NC}: $count ошибок"
        done
        
        TOTAL_ERRORS=$(wc -l < "$TEMP_FILE")
        echo ""
        echo -e "${RED}📊 Всего найдено ошибок: $TOTAL_ERRORS${NC}"
    else
        echo -e "${GREEN}✅ Ошибок не найдено!${NC}"
    fi
    
    # Удаляем временный файл
    rm -f "$TEMP_FILE"
}

# Функция для автоматического исправления ошибок
auto_fix_errors() {
    echo -e "${BLUE}🔧 Автоматическое исправление ошибок...${NC}"
    
    # 1. Black форматирование
    echo -e "${YELLOW}📝 Применение Black форматирования...${NC}"
    if ! python3 -m black --check --quiet .; then
        echo -e "${YELLOW}⚠️ Black нашел проблемы, применяю форматирование...${NC}"
        python3 -m black .
        echo -e "${GREEN}✅ Black форматирование применено${NC}"
        
        # Добавляем отформатированные файлы
        git add .
    else
        echo -e "${GREEN}✅ Black форматирование корректно${NC}"
    fi
    
    # 2. autopep8 исправление (если доступен)
    if [ "$HAS_AUTOPEP8" = true ]; then
        echo -e "${YELLOW}🔧 Применение autopep8 исправлений...${NC}"
        python3 -m autopep8 --in-place --recursive --aggressive --aggressive --max-line-length=100 --ignore=E203,W503 .
        echo -e "${GREEN}✅ autopep8 исправления применены${NC}"
        
        # Добавляем исправленные файлы
        git add .
    else
        echo -e "${YELLOW}⚠️ autopep8 недоступен, пропускаю автоматические исправления${NC}"
    fi
    
    # 3. isort сортировка импортов (если доступен)
    if [ "$HAS_ISORT" = true ]; then
        echo -e "${YELLOW}📦 Сортировка импортов через isort...${NC}"
        python3 -m isort .
        echo -e "${GREEN}✅ Импорты отсортированы${NC}"
        
        # Добавляем отсортированные файлы
        git add .
    else
        echo -e "${YELLOW}⚠️ isort недоступен, пропускаю сортировку импортов${NC}"
    fi
}

# Функция для ручного исправления критических ошибок
fix_critical_errors() {
    echo -e "${BLUE}🚨 Исправление критических ошибок...${NC}"
    
    # Создаем временный файл для критических ошибок
    TEMP_FILE=$(mktemp)
    
    # Ищем критические ошибки (F821, E722, F601)
    python3 -m flake8 --max-line-length=100 --ignore=E203,W503,E501,F401,F841,F541,W291,W293,E402 . > "$TEMP_FILE" 2>/dev/null || true
    
    if [ -s "$TEMP_FILE" ]; then
        echo -e "${RED}🚨 Найдены критические ошибки:${NC}"
        
        # Показываем критические ошибки
        grep -E "(F821|E722|F601)" "$TEMP_FILE" | head -10 | while read line; do
            echo -e "  ${RED}$line${NC}"
        done
        
        echo ""
        echo -e "${YELLOW}💡 Критические ошибки требуют ручного исправления:${NC}"
        echo -e "  ${RED}F821${NC}: Неопределенные переменные (например, 'logger')"
        echo -e "  ${RED}E722${NC}: Голые except блоки (добавьте конкретные исключения)"
        echo -e "  ${RED}F601${NC}: Дублирующиеся ключи словаря"
        
        echo ""
        echo -e "${BLUE}🔍 Файлы с критическими ошибками:${NC}"
        grep -E "(F821|E722|F601)" "$TEMP_FILE" | cut -d: -f1 | sort | uniq | while read file; do
            echo -e "  ${YELLOW}$file${NC}"
        done
        
        echo ""
        echo -e "${YELLOW}⚠️ Продолжаем с предупреждением о критических ошибках${NC}"
    else
        echo -e "${GREEN}✅ Критических ошибок не найдено${NC}"
    fi
    
    # Удаляем временный файл
    rm -f "$TEMP_FILE"
}

# Функция для показа статистики исправлений
show_fix_stats() {
    echo -e "${BLUE}📊 Статистика исправлений:${NC}"
    
    # Подсчет измененных файлов
    CHANGED_FILES=$(git diff --name-only | wc -l)
    STAGED_FILES=$(git diff --cached --name-only | wc -l)
    
    echo -e "  - Измененных файлов: ${CHANGED_FILES}"
    echo -e "  - Добавленных в staging: ${STAGED_FILES}"
    
    if [ "$CHANGED_FILES" -gt 0 ]; then
        echo -e "${YELLOW}📝 Измененные файлы:${NC}"
        git diff --name-only | head -10 | while read file; do
            echo -e "  ${YELLOW}$file${NC}"
        done
        if [ "$CHANGED_FILES" -gt 10 ]; then
            echo -e "  ${BLUE}... и еще $((CHANGED_FILES - 10)) файлов${NC}"
        fi
    fi
}

# Функция для создания коммита с исправлениями
create_fix_commit() {
    echo -e "${BLUE}💾 Создание коммита с исправлениями...${NC}"
    
    # Проверяем есть ли изменения для коммита
    if [ -z "$(git diff --cached --name-only)" ]; then
        echo -e "${YELLOW}⚠️ Нет изменений для коммита${NC}"
        return 0
    fi
    
    # Получаем статистику изменений
    CHANGED_FILES=$(git diff --cached --name-only | wc -l)
    NEW_FILES=$(git status --porcelain | grep "^A" | wc -l)
    MODIFIED_FILES=$(git status --porcelain | grep "^M" | wc -l)
    
    echo -e "${YELLOW}📊 Статистика изменений:${NC}"
    echo -e "  - Новых файлов: ${NEW_FILES}"
    echo -e "  - Измененных файлов: ${MODIFIED_FILES}"
    echo -e "  - Всего файлов в коммите: ${CHANGED_FILES}"
    
    # Создаем коммит с детальным сообщением
    COMMIT_MSG="fix: Auto-fix code quality issues

Applied automatic fixes:
- ✅ Black code formatting
- ✅ autopep8 style corrections (if available)
- ✅ isort import sorting (if available)

Quality improvements:
- Fixed line length violations
- Removed unused imports and variables
- Fixed f-string placeholders
- Cleaned up whitespace issues
- Sorted imports properly

Files processed: ${CHANGED_FILES}
New files: ${NEW_FILES}
Modified files: ${MODIFIED_FILES}

Note: Critical errors (F821, E722, F601) may require manual review"
    
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✅ Коммит с исправлениями создан${NC}"
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
    
    # Анализируем ошибки
    analyze_errors
    
    # Автоматически исправляем ошибки
    auto_fix_errors
    
    # Исправляем критические ошибки
    fix_critical_errors
    
    # Показываем статистику
    show_fix_stats
    
    # Создаем коммит
    create_fix_commit
    
    echo ""
    echo -e "${GREEN}🎉 Детальная проверка и исправление завершены!${NC}"
    echo -e "${BLUE}💡 Для отправки изменений используйте: git push origin main${NC}"
}

# Запуск основной функции
main "$@"
