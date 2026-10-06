#!/usr/bin/env python3
"""
🗂️ Скрипт реорганизации структуры MD файлов PulseAI
Автор: AI Assistant
Версия: 2.0

Создает красивую структуру, убирая все MD файлы из корня проекта
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class StructureReorganizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.guides_dir = self.docs_dir / "guides"
        self.technical_dir = self.docs_dir / "technical"
        self.archive_dir = self.docs_dir / "archive"

    def create_directories(self):
        """Создает новую структуру директорий"""
        self.docs_dir.mkdir(exist_ok=True)
        self.guides_dir.mkdir(exist_ok=True)
        self.technical_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        print("✅ Создана новая структура директорий")

    def create_main_docs_readme(self):
        """Создает главный README.md для docs/"""
        content = f"""# 📚 PulseAI Documentation

*Центральная документация проекта PulseAI*
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

### 📖 Основные файлы
- [MASTER_FILE.md](MASTER_FILE.md) - Основные правила и архитектура проекта
- [TASKS.md](TASKS.md) - Актуальные задачи и приоритеты
- [CODEMAP.md](CODEMAP.md) - Структура проекта (автогенерируемая)
- [CONTRIBUTING.md](CONTRIBUTING.md) - Руководство для контрибьюторов

### 📁 Руководства (guides/)
- [🛠️ DEVELOPMENT.md](guides/DEVELOPMENT.md) - Разработка и развертывание
- [🔧 CODE_QUALITY.md](guides/CODE_QUALITY.md) - Качество кода и автоматизация
- [🎨 FRONTEND.md](guides/FRONTEND.md) - Фронтенд и CSS система
- [🌐 INFRASTRUCTURE.md](guides/INFRASTRUCTURE.md) - Инфраструктура и конфигурация

### 📁 Техническая документация (technical/)
- [🏗️ ARCHITECTURE.md](technical/ARCHITECTURE.md) - Архитектура системы
- [🗄️ DATABASE_MAINTENANCE.md](technical/DATABASE_MAINTENANCE.md) - Обслуживание БД
- [🔑 TOKENS.md](technical/TOKENS.md) - Токены и API ключи
- [📰 DIGESTS.md](technical/DIGESTS.md) - Система дайджестов
- [🔍 PARSERS.md](technical/PARSERS.md) - Парсеры новостей
- [📡 SOURCES.md](technical/SOURCES.md) - Источники новостей
- [🚀 DEPLOY.md](technical/DEPLOY.md) - Развертывание
- [🎯 VISION.md](technical/VISION.md) - Видение проекта
- [💬 COMMUNICATION.md](technical/COMMUNICATION.md) - Коммуникации
- [🧠 AI_OPTIMIZATION.md](technical/AI_OPTIMIZATION.md) - AI оптимизация
- [🌐 CLOUDFLARE_CONFIG.md](technical/CLOUDFLARE_CONFIG.md) - Конфигурация Cloudflare

### 📁 Архив (archive/)
- [📊 REPORTS.md](archive/REPORTS.md) - Архив всех исторических отчетов

## 🚀 Быстрый старт

### Для разработчиков:
1. Прочитайте [MASTER_FILE.md](MASTER_FILE.md) для понимания проекта
2. Изучите [TASKS.md](TASKS.md) для текущих задач
3. Следуйте [DEVELOPMENT.md](guides/DEVELOPMENT.md) для настройки среды

### Для контрибьюторов:
1. Прочитайте [CONTRIBUTING.md](CONTRIBUTING.md)
2. Изучите [CODE_QUALITY.md](guides/CODE_QUALITY.md)
3. Следуйте процессу разработки

### Для деплоя:
1. Изучите [DEVELOPMENT.md](guides/DEVELOPMENT.md)
2. Настройте [INFRASTRUCTURE.md](guides/INFRASTRUCTURE.md)
3. Следуйте [DEPLOY.md](technical/DEPLOY.md)

## 📊 Статистика документации

- **Основных файлов:** 4
- **Руководств:** 4
- **Технических документов:** 11
- **Архивных отчетов:** 1
- **Всего файлов:** 20

---

*Эта документация организована для удобства навигации и поиска информации*
"""

        with open(self.docs_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создан главный README.md для docs/")

    def create_infrastructure_guide(self):
        """Создает объединенное руководство по инфраструктуре"""
        content = f"""# 🌐 PulseAI Infrastructure Guide

*Объединенное руководство по инфраструктуре и конфигурации*
*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Содержание

- [Cloudflare Configuration](#cloudflare-configuration)
- [Deployment](#deployment)
- [Database Maintenance](#database-maintenance)
- [Monitoring](#monitoring)
- [Security](#security)

## 🌐 Cloudflare Configuration

### Централизованная конфигурация
Все настройки Cloudflare Tunnel управляются через единый файл `config/cloudflare.py`.

### Основные компоненты:
- **CLOUDFLARE_TUNNEL_URL** - Публичный URL туннеля
- **CLOUDFLARE_LOCAL_URL** - Локальный URL для разработки
- **Автоматическое обновление** конфигураций

### Команды управления:
```bash
# Показать текущую конфигурацию
make cloudflare-config

# Обновить все конфигурации
make update-config
```

## 🚀 Deployment

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

### Архитектура развертывания:
```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

## 🗄️ Database Maintenance

### Миграции:
- Автоматические миграции при запуске
- Ручные миграции через скрипты
- Откат изменений при необходимости

### Бэкапы:
- Регулярные автоматические бэкапы
- Ручные бэкапы перед важными изменениями
- Восстановление из бэкапов

### Мониторинг:
- Отслеживание производительности
- Мониторинг использования ресурсов
- Алерты при проблемах

## 📊 Monitoring

### Метрики:
- Производительность API
- Использование ресурсов
- Ошибки и исключения
- Пользовательская активность

### Логирование:
- Структурированные логи
- Различные уровни логирования
- Централизованный сбор логов

## 🔒 Security

### API Keys:
- Безопасное хранение токенов
- Ротация ключей
- Мониторинг использования

### Доступ:
- Контроль доступа к API
- Аутентификация пользователей
- Авторизация операций

---

*Это руководство объединяет информацию из CLOUDFLARE_CONFIG.md, DEPLOY.md и DATABASE_MAINTENANCE.md*
"""

        with open(self.guides_dir / "INFRASTRUCTURE.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Создано guides/INFRASTRUCTURE.md")

    def move_files_to_structure(self):
        """Перемещает файлы в новую структуру"""

        # Основные файлы в docs/
        main_files = ["MASTER_FILE.md", "TASKS.md", "CODEMAP.md", "CONTRIBUTING.md"]

        for file_name in main_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.docs_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"✅ Перемещен {file_name} в docs/")

        # Руководства в docs/guides/
        guide_files = ["DEVELOPMENT.md", "CODE_QUALITY.md", "FRONTEND.md"]

        for file_name in guide_files:
            src = self.docs_dir / file_name
            if src.exists():
                dst = self.guides_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"✅ Перемещен {file_name} в docs/guides/")

        # Техническая документация в docs/technical/
        technical_files = [
            "ARCHITECTURE.md",
            "DATABASE_MAINTENANCE.md",
            "TOKENS.md",
            "DIGESTS.md",
            "PARSERS.md",
            "SOURCES.md",
            "DEPLOY.md",
            "VISION.md",
            "COMMUNICATION.md",
            "AI_OPTIMIZATION.md",
            "CLOUDFLARE_CONFIG.md",
        ]

        for file_name in technical_files:
            src = self.docs_dir / file_name
            if src.exists():
                dst = self.technical_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"✅ Перемещен {file_name} в docs/technical/")

        # Архив уже создан
        print("✅ Архив уже в правильном месте")

    def backup_root_files(self):
        """Создает резервную копию файлов из корня"""
        backup_dir = self.project_root / "backup_root_md_files"
        backup_dir.mkdir(exist_ok=True)

        # Находим все MD файлы в корне
        root_md_files = list(self.project_root.glob("*.md"))

        for file_path in root_md_files:
            dst = backup_dir / file_path.name
            shutil.copy2(file_path, dst)

        print(f"✅ Создана резервная копия {len(root_md_files)} файлов в {backup_dir}")

    def update_main_readme(self):
        """Обновляет основной README.md в корне"""
        content = f"""# PulseAI

![Tests – main](https://github.com/repository-owner/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
![Code Quality](https://img.shields.io/badge/code%20quality-A%20-green)
![Architecture](https://img.shields.io/badge/architecture-unified-blue)
![Performance](https://img.shields.io/badge/performance-optimized-orange)

**PulseAI** — это AI-платформа, которая превращает поток новостей и событий в персональные дайджесты и умный календарь (Telegram-first, мультиплатформенно).

## 📚 Документация

**Вся документация находится в папке [`docs/`](docs/):**

- 📖 **[Документация](docs/README.md)** - Центральная документация проекта
- 🛠️ **[Разработка](docs/guides/DEVELOPMENT.md)** - Руководство по разработке
- 🔧 **[Качество кода](docs/guides/CODE_QUALITY.md)** - Система качества кода
- 🎨 **[Фронтенд](docs/guides/FRONTEND.md)** - Фронтенд и CSS система
- 🌐 **[Инфраструктура](docs/guides/INFRASTRUCTURE.md)** - Инфраструктура и конфигурация

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/repository-owner/news_ai_bot.git
cd news_ai_bot

# Установить зависимости
pip install -r requirements.txt
npm install --prefix webapp

# Запустить все сервисы
make start

# Проверить статус
make status
```

## 📋 Основные команды

```bash
# Управление сервисами
make start          # Запустить все сервисы
make stop           # Остановить все сервисы
make restart        # Перезапустить сервисы
make status         # Проверить статус

# Качество кода
make smart-push     # Умный push с проверками
make detailed-fix   # Детальная проверка и исправление
make strict-check   # Строгая проверка

# Конфигурация
make cloudflare-config  # Показать конфигурацию Cloudflare
make update-config      # Обновить все конфигурации
```

## 🏗️ Архитектура

```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

### Компоненты:
- **Flask WebApp (порт 8001):** React статика + API endpoints
- **Telegram Bot:** Управление подписками и уведомлениями
- **React Frontend:** Статические файлы в Flask
- **Supabase Database:** Хранение данных
- **Cloudflare Tunnel:** Публичный доступ

## 📊 Статистика проекта

- **Python файлов:** 200+
- **React компонентов:** 15+
- **API endpoints:** 25+
- **Тестов:** 50+
- **Документации:** 20+ файлов

## 🤝 Участие в проекте

См. [CONTRIBUTING.md](docs/CONTRIBUTING.md) для детальной информации о том, как участвовать в разработке.

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) файл для деталей.

## 📞 Поддержка

- 📖 **Документация:** [docs/README.md](docs/README.md)
- 🐛 **Баги:** [Issues](https://github.com/repository-owner/news_ai_bot/issues)
- 💬 **Обсуждения:** [Discussions](https://github.com/repository-owner/news_ai_bot/discussions)

---

*PulseAI - AI-powered news and events platform* 🚀
"""

        with open(self.project_root / "README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Обновлен основной README.md")

    def reorganize_structure(self):
        """Основная функция реорганизации"""
        print("🗂️ Начинаем реорганизацию структуры PulseAI...")

        # Создаем структуру директорий
        self.create_directories()

        # Создаем резервную копию
        self.backup_root_files()

        # Создаем новые файлы
        self.create_main_docs_readme()
        self.create_infrastructure_guide()

        # Перемещаем файлы
        self.move_files_to_structure()

        # Обновляем основной README
        self.update_main_readme()

        print("\n✅ Реорганизация завершена!")
        print("📁 Новая структура:")
        print("  - docs/README.md - Главная документация")
        print("  - docs/guides/ - Руководства")
        print("  - docs/technical/ - Техническая документация")
        print("  - docs/archive/ - Архив отчетов")
        print("  - README.md - Обновленный основной файл")
        print("\n💡 Следующие шаги:")
        print("  1. Проверьте новую структуру")
        print("  2. Обновите ссылки в коде")
        print("  3. Удалите избыточные файлы")
        print("  4. Протестируйте навигацию")


if __name__ == "__main__":
    reorganizer = StructureReorganizer()
    reorganizer.reorganize_structure()
