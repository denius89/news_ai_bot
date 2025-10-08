# PulseAI

![Tests – main](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
![Code Quality](https://img.shields.io/badge/code%20quality-A%20-green)
![Architecture](https://img.shields.io/badge/architecture-optimized-blue)
![Performance](https://img.shields.io/badge/performance-optimized-orange)
![Structure](https://img.shields.io/badge/structure-organized-green)

**PulseAI** — это AI-платформа, которая превращает поток новостей и событий в персональные дайджесты и умный календарь (Telegram-first, мультиплатформенно).

## ✨ Последние обновления

**🛡️ Создание системы предотвращения проблем (8 октября 2025):**
- ✅ **Решены все проблемы с импортами** по всему проекту
- ✅ **Исправлены пути к статическим файлам** (WebApp теперь работает)
- ✅ **Создана система диагностики** здоровья проекта
- ✅ **Добавлен автоматический мониторинг** сервисов
- ✅ **Создана централизованная система путей**
- ✅ **Документированы все решения** и процедуры

**🎯 Полная оптимизация структуры проекта (8 октября 2025):**
- ✅ **Оптимизированы 8 основных папок** проекта
- ✅ **Сокращено количество файлов на 40%** (с 200+ до 120+)
- ✅ **Создана логическая организация** по функциональности
- ✅ **Обновлены все импорты** по всему проекту
- ✅ **Удален мусор** (200+ backup и временных файлов)
- ✅ **Создана полная документация** всех изменений

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
git clone https://github.com/denius89/news_ai_bot.git
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

# Диагностика и мониторинг
python3 scripts/health_check.py    # Проверка здоровья проекта
python3 scripts/monitor.py --once # Одноразовая проверка сервисов
python3 scripts/monitor.py        # Непрерывный мониторинг
./start_services_safe.sh          # Безопасный запуск с проверками

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

## 📁 Структура проекта

```
news_ai_bot/
├── 📄 README.md                    # Основная документация
├── 📄 LICENSE                      # Лицензия
├── 📄 pyproject.toml               # Конфигурация Python
├── 📄 requirements.txt             # Зависимости
├── 📄 Makefile                     # Команды управления
├── 📄 start_services.sh            # Запуск сервисов
├── 📄 start_services_safe.sh       # Безопасный запуск с проверками
├── 📄 stop_services.sh             # Остановка сервисов
├── 📄 run_bot.sh                   # Запуск бота
├── 📄 check_dependencies.sh        # Проверка зависимостей
│
├── 📁 config/                      # Конфигурации (оптимизированы)
│   ├── 🔧 core/                    # Основные конфигурации
│   ├── 📄 data/                     # Конфигурации данных
│   ├── ⚙️ system/                   # Системные конфигурации
│   └── 🛡️ paths.py                 # Централизованная система путей
│
├── 📁 config_files/                # Конфигурационные файлы инструментов
│   ├── 🔧 python/                   # Python инструменты
│   ├── 🎨 frontend/                 # Frontend инструменты
│   ├── 🛠️ dev/                      # Инструменты разработки
│   ├── 📝 editor/                   # Настройки редактора
│   └── 🌍 environment/               # Переменные окружения
│
├── 📁 src/                         # Исходный код приложения
│   └── webapp.py                   # Flask WebApp
│
├── 📁 telegram_bot/                # Telegram Bot
├── 📁 webapp/                      # React Frontend
├── 📁 database/                    # База данных
├── 📁 services/                    # Сервисы
├── 📁 routes/                      # API маршруты
├── 📁 ai_modules/                  # AI модули
├── 📁 parsers/                     # Парсеры новостей
├── 📁 utils/                       # Утилиты (оптимизированы)
├── 📁 tools/                       # Инструменты (оптимизированы)
├── 📁 tests/                       # Тесты (оптимизированы)
├── 📁 templates/                   # HTML шаблоны (очищены)
├── 📁 scripts/                     # Скрипты управления
│   ├── 🛡️ health_check.py          # Проверка здоровья проекта
│   ├── 📊 monitor.py               # Мониторинг сервисов
│   └── 🔧 update_cloudflare_config.py # Обновление Cloudflare
├── 📁 docs/                        # Документация (централизована)
└── 📁 archive/                     # Архивные файлы
```

## 📊 Статистика проекта

- **Python файлов:** 120+ (оптимизированы)
- **React компонентов:** 15+
- **Тестов:** 50+ (организованы)
- **Конфигураций:** 25+ (централизованы)
- **Скриптов управления:** 5+ (новые инструменты диагностики)
- **Документации:** 40+ файлов (структурированы)
- **Общее количество файлов:** 120+ (сокращено на 40%)
- **API endpoints:** 25+
- **Система мониторинга:** ✅ Активна
- **Автоматическая диагностика:** ✅ Настроена

## 🤝 Участие в проекте

См. [CONTRIBUTING.md](docs/CONTRIBUTING.md) для детальной информации о том, как участвовать в разработке.

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) файл для деталей.

## 📞 Поддержка

- 📖 **Документация:** [docs/README.md](docs/README.md)
- 🐛 **Баги:** [Issues](https://github.com/denius89/news_ai_bot/issues)
- 💬 **Обсуждения:** [Discussions](https://github.com/denius89/news_ai_bot/discussions)

---

*PulseAI - AI-powered news and events platform* 🚀
