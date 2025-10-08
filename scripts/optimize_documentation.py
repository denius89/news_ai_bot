#!/usr/bin/env python3
"""
📚 Скрипт оптимизации MD файлов PulseAI
Автор: AI Assistant
Версия: 1.0

Объединяет избыточные MD файлы в логичную структуру
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class DocumentationOptimizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.archive_dir = self.project_root / "archive"

    def create_directories(self):
        """Создает необходимые директории"""
        self.docs_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        print("✅ Директории созданы")

    def create_development_guide(self):
        """Создает объединенное руководство по разработке"""
        content = f"""# 🛠️ PulseAI Development Guide

*Объединенное руководство по разработке и развертыванию*  
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [Развертывание](#развертывание)
- [Порты и сервисы](#порты-и-сервисы)
- [Отладка](#отладка)
- [Команды Makefile](#команды-makefile)

## 🚀 Быстрый старт

```bash
# Запустить все сервисы
make start

# Проверить статус
make status

# Остановить все сервисы
make stop
```

## 🏗️ Архитектура

### Production Ready Architecture

**Архитектура:**
```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

### Компоненты:
- **Flask WebApp (порт 8001):** React статика + API endpoints
- **Telegram Bot:** Управление подписками и уведомлениями
- **React Frontend:** Статические файлы в Flask
- **Supabase Database:** Хранение данных
- **Cloudflare Tunnel:** Публичный доступ

## 🚀 Развертывание

### Локальная разработка:
```bash
# Установка зависимостей
pip install -r requirements.txt
npm install --prefix webapp

# Запуск сервисов
make start
```

### Production развертывание:
```bash
# Настройка Cloudflare Tunnel
make cloudflare-config

# Обновление конфигураций
make update-config

# Запуск в production режиме
APP_ENV=production make start
```

## 🔌 Порты и сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| Flask WebApp | 8001 | React статика + API |
| Telegram Bot | - | Polling режим |
| Cloudflare Tunnel | - | Публичный доступ |

## 🐛 Отладка

### Проверка процессов:
```bash
make check-ports
make logs
```

### Проверка качества кода:
```bash
make detailed-fix
make strict-check
```

## 📋 Команды Makefile

### Основные команды:
- `make start` - Запустить все сервисы
- `make stop` - Остановить все сервисы
- `make restart` - Перезапустить сервисы
- `make status` - Проверить статус

### Качество кода:
- `make smart-push` - Умный push с проверками
- `make detailed-fix` - Детальная проверка и исправление
- `make strict-check` - Строгая проверка

### Конфигурация:
- `make cloudflare-config` - Показать конфигурацию Cloudflare
- `make update-config` - Обновить все конфигурации

---

*Это руководство объединяет информацию из DEVELOPMENT_GUIDE.md, DEPLOYMENT_GUIDE.md и PORTS.md*
"""

        with open(self.docs_dir / "DEVELOPMENT.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создано docs/DEVELOPMENT.md")

    def create_code_quality_guide(self):
        """Создает объединенное руководство по качеству кода"""
        content = f"""# 🔧 PulseAI Code Quality Guide

*Объединенное руководство по качеству кода и автоматизации*  
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

- [Система качества кода](#система-качества-кода)
- [Автоматические исправления](#автоматические-исправления)
- [Git workflow](#git-workflow)
- [Инструменты](#инструменты)
- [Статистика](#статистика)

## 🔧 Система качества кода

### Детальная проверка и исправление

```bash
# Автоматическое исправление всех ошибок
make detailed-fix

# Умный push с проверками
make smart-push

# Строгая проверка
make strict-check
```

### Что исправляется автоматически:
- ✅ **Black форматирование** - длина строк, отступы, пробелы
- ✅ **autopep8 исправления** - импорты, переменные, f-строки
- ✅ **isort сортировка** - порядок импортов
- ✅ **Критические ошибки** - с руководством по исправлению

## 🚀 Git Workflow

### Умный push:
```bash
make smart-push
```

**Процесс:**
1. 🔍 Анализ всех ошибок
2. 🔧 Автоматическое исправление
3. 📊 Детальная статистика
4. 💾 Создание коммита
5. 🚀 Отправка изменений

### Детальная проверка:
```bash
make detailed-fix
```

**Результат:**
- Анализ ошибок по типам
- Автоматическое исправление
- Статистика по файлам
- Руководство по критическим ошибкам

## 🛠️ Инструменты

### Обязательные:
```bash
pip install black flake8 autopep8
```

### Опциональные:
```bash
pip install isort  # Для сортировки импортов
```

## 📊 Статистика

### Исправлено автоматически:
- **845+ ошибок** качества кода
- **544 ошибки** длины строк (E501)
- **109 ошибок** неиспользуемых импортов (F401)
- **81 ошибка** порядка импортов (E402)
- **67 ошибок** f-строк без плейсхолдеров (F541)
- **18 ошибок** неиспользуемых переменных (F841)
- **10 ошибок** голых except блоков (E722)

### Критические исправления:
- ✅ Исправлены logger переменные
- ✅ Исправлены дублирующиеся ключи словаря
- ✅ Исправлены проблемы с отступами
- ✅ Удалены дублирующиеся переменные

---

*Это руководство объединяет информацию из SMART_PUSH_GUIDE.md и DETAILED_CODE_QUALITY_GUIDE.md*
"""

        with open(self.docs_dir / "CODE_QUALITY.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создано docs/CODE_QUALITY.md")

    def create_frontend_guide(self):
        """Создает объединенное руководство по фронтенду"""
        content = f"""# 🎨 PulseAI Frontend Guide

*Объединенное руководство по фронтенду и CSS системе*  
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

- [CSS система](#css-система)
- [Компоненты](#компоненты)
- [Темы](#темы)
- [Оптимизация](#оптимизация)
- [Исправления](#исправления)

## 🎨 CSS система

### Структура стилей:
```
static/css/
├── components/     # Компоненты
├── layouts/        # Макеты
├── themes/         # Темы
└── utilities/      # Утилиты
```

### Основные компоненты:
- **Button** - Кнопки с различными стилями
- **Card** - Карточки контента
- **Modal** - Модальные окна
- **Form** - Формы и элементы ввода

## 🧩 Компоненты

### React компоненты:
- **NewsPage** - Страница новостей с infinite scroll
- **DigestPage** - Страница дайджестов
- **EventsPage** - Страница событий
- **SettingsPage** - Настройки

### TypeScript интерфейсы:
- Строгая типизация всех компонентов
- Интерфейсы для API ответов
- Типы для состояний

## 🎭 Темы

### Доступные темы:
- **Light** - Светлая тема
- **Dark** - Темная тема
- **Auto** - Автоматическое переключение

### Переменные CSS:
```css
:root {{
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --background-color: #ffffff;
  --text-color: #1e293b;
}}
```

## ⚡ Оптимизация

### Производительность:
- **CSS минификация** - Сжатие стилей
- **Tree shaking** - Удаление неиспользуемого кода
- **Lazy loading** - Ленивая загрузка компонентов
- **Code splitting** - Разделение кода

### Результаты оптимизации:
- **Сокращение размера CSS** на 40%
- **Улучшение времени загрузки** на 25%
- **Оптимизация компонентов** React

## 🔧 Исправления

### Исправленные проблемы:
- ✅ **Swipe-to-load** функциональность
- ✅ **Infinite scroll** оптимизация
- ✅ **TypeScript ошибки** исправлены
- ✅ **CSS конфликты** устранены
- ✅ **Responsive design** улучшен

### Улучшения UI/UX:
- **Лучшая навигация** между страницами
- **Улучшенные анимации** и переходы
- **Оптимизированные формы** ввода
- **Адаптивный дизайн** для мобильных устройств

---

*Это руководство объединяет информацию из CSS_SYSTEM_GUIDE.md, CSS_REFACTOR_FINAL_REPORT.md, CSS_OPTIMIZATION_REPORT.md, CSS_AUDIT_REPORT.md, README_CSS.md и FRONTEND_FIX_REPORT.md*
"""

        with open(self.docs_dir / "FRONTEND.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создано docs/FRONTEND.md")

    def create_archive_reports(self):
        """Создает архив всех отчетов"""
        content = f"""# 📊 PulseAI Development Reports Archive

*Архив всех отчетов о разработке и оптимизации*  
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

- [AI Optimization](#ai-optimization)
- [News Optimization](#news-optimization)
- [Light/Premium Implementation](#lightpremium-implementation)
- [Day 13-14 Completion](#day-13-14-completion)
- [Production Refactor](#production-refactor)
- [WebSocket Migration](#websocket-migration)
- [Data Loading](#data-loading)
- [Self-Tuning Systems](#self-tuning-systems)

## 🧠 AI Optimization

### AI_OPTIMIZATION_REPORT.md
**Снижение AI вызовов на 70-90%** через трехэтапную фильтрацию:
1. **Pre-filter** - Легкая фильтрация по правилам
2. **Cache** - Переиспользование предыдущих оценок
3. **Local Predictor** - Локальная модель для предварительной оценки

### AUTO_LEARNING_FILTER_REPORT.md
**Самообучающийся фильтр** для автоматического улучшения качества новостей.

### SELF_TUNING_PREDICTOR_REPORT.md
**Самообучающийся предиктор** для предсказания важности и достоверности.

### ADAPTIVE_THRESHOLDS_TTL_REPORT.md
**Адаптивные пороги и TTL** для динамической оптимизации кэша.

## 📰 News Optimization

### NEWS_OPTIMIZATION_REPORT.md
**Оптимизация системы новостей** с улучшенным распределением по категориям.

### DATA_LOADING_REPORT.md
**Оптимизация загрузки данных** с улучшенной производительностью.

## 💎 Light/Premium Implementation

### PULSEAI_LIGHT_PREMIUM_REPORT.md
**Реализация тарифных планов** Light и Premium с разделением функциональности.

## 🎯 Completion Reports

### DAY13_FINAL_REPORT.md
**Финальный отчет 13-го дня** разработки с завершенными задачами.

### DAY14_COMPLETION_REPORT.md
**Отчет о завершении 14-го дня** с полным списком достижений.

## 🚀 Production Refactor

### PRODUCTION_REFACTOR_REPORT.md
**Рефакторинг для продакшена** с подготовкой к развертыванию.

### INLINE_REFACTOR_REPORT.md
**Inline рефакторинг** без изменения архитектуры.

## 🔄 Migration Reports

### WS_MIGRATION_REPORT.md
**Миграция на WebSocket** для real-time обновлений.

---

*Этот архив содержит все исторические отчеты о разработке PulseAI. Для актуальной информации см. основные руководства в docs/*
"""

        with open(self.archive_dir / "REPORTS.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создано archive/REPORTS.md")

    def backup_files(self):
        """Создает резервную копию файлов перед удалением"""
        backup_dir = self.project_root / "backup_md_files"
        backup_dir.mkdir(exist_ok=True)

        files_to_backup = [
            "DEVELOPMENT_GUIDE.md",
            "DEPLOYMENT_GUIDE.md",
            "PORTS.md",
            "docs/SMART_PUSH_GUIDE.md",
            "docs/DETAILED_CODE_QUALITY_GUIDE.md",
            "CSS_SYSTEM_GUIDE.md",
            "CSS_REFACTOR_FINAL_REPORT.md",
            "CSS_OPTIMIZATION_REPORT.md",
            "CSS_AUDIT_REPORT.md",
            "README_CSS.md",
            "FRONTEND_FIX_REPORT.md",
            "AI_OPTIMIZATION_REPORT.md",
            "NEWS_OPTIMIZATION_REPORT.md",
            "PULSEAI_LIGHT_PREMIUM_REPORT.md",
            "DAY13_FINAL_REPORT.md",
            "DAY14_COMPLETION_REPORT.md",
            "PRODUCTION_REFACTOR_REPORT.md",
            "WS_MIGRATION_REPORT.md",
            "INLINE_REFACTOR_REPORT.md",
            "DATA_LOADING_REPORT.md",
            "SELF_TUNING_PREDICTOR_REPORT.md",
            "AUTO_LEARNING_FILTER_REPORT.md",
            "ADAPTIVE_THRESHOLDS_TTL_REPORT.md",
        ]

        for file_path in files_to_backup:
            src = self.project_root / file_path
            if src.exists():
                dst = backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        print(f"✅ Создана резервная копия в {backup_dir}")

    def optimize_documentation(self):
        """Основная функция оптимизации"""
        print("🚀 Начинаем оптимизацию документации PulseAI...")

        # Создаем директории
        self.create_directories()

        # Создаем резервную копию
        self.backup_files()

        # Создаем объединенные руководства
        self.create_development_guide()
        self.create_code_quality_guide()
        self.create_frontend_guide()
        self.create_archive_reports()

        print("\n✅ Оптимизация завершена!")
        print("📁 Созданы объединенные руководства:")
        print("  - docs/DEVELOPMENT.md")
        print("  - docs/CODE_QUALITY.md")
        print("  - docs/FRONTEND.md")
        print("  - archive/REPORTS.md")
        print("\n💡 Следующие шаги:")
        print("  1. Проверьте новые файлы")
        print("  2. Обновите ссылки в коде")
        print("  3. Удалите избыточные файлы")
        print("  4. Обновите README.md")


if __name__ == "__main__":
    optimizer = DocumentationOptimizer()
    optimizer.optimize_documentation()
