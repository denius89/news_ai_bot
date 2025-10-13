# PulseAI

![Tests – main](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
![Code Quality](https://img.shields.io/badge/code%20quality-A%20-green)
![Architecture](https://img.shields.io/badge/architecture-optimized-blue)
![Performance](https://img.shields.io/badge/performance-optimized-orange)
![Structure](https://img.shields.io/badge/structure-organized-green)

**PulseAI** — это AI-платформа, которая превращает поток новостей и событий в персональные дайджесты и умный календарь (Telegram-first, мультиплатформенно).

## ✨ Последние обновления

**🔔 Day 17 - Event Intelligence & Notifications (11 января 2025):**
- ✅ **Rate Limit Manager** - умное управление API лимитами для всех провайдеров
- ✅ **Event Intelligence Layer** - кеширование и throttling с учетом лимитов
- ✅ **Notification System** - полноценная система уведомлений Telegram + WebApp
- ✅ **User Preferences** - персональные настройки категорий и важности
- ✅ **SSE Real-time Stream** - обновления событий в реальном времени
- ✅ **Smart Scheduler** - планировщик фетчей с учетом rate limits
- ✅ **Telegram Sender** - интеграция отправки уведомлений через бота
- ✅ **WebApp Settings UI** - React компонент для настройки уведомлений
- ✅ **CLI Tools** - `events_scheduler.py` и `send_notifications.py`
- ✅ **API Endpoints** - `/user/preferences` (GET/POST) и `/user/notifications/test`

**🚀 Day 16 - Event Expansion & AI Calendar Part 2 (11 января 2025):**
- ✅ **ML-фильтрация v2** - улучшенная оценка важности без дорогих AI вызовов
- ✅ **Smart Sync система** - инкрементальное обновление только изменившихся событий
- ✅ **CoinMarketCal провайдер** - интеграция крупнейшего крипто-календаря
- ✅ **OECD провайдер** - экономические события ОЭСР
- ✅ **Enhanced API** - флаг `important=true` для фильтрации важных событий
- ✅ **Notification Service** - заглушка для будущих уведомлений (Part 3)
- ✅ **Новые поля БД** - importance_score, credibility_score, sync_status, last_synced_at
- ✅ **Полное тестирование** - unit тесты для ML v2 и Smart Sync

**🚀 Day 15 - Event Expansion & AI Calendar (11 января 2025):**
- ✅ **20+ новых провайдеров событий** - crypto, sports, markets, tech, world
- ✅ **AI фильтрация событий** - importance ≥ 0.6, автоматическая дедупликация
- ✅ **Расширенная база данных** - поля status, result_data, unique_hash, metadata
- ✅ **Динамическая загрузка провайдеров** - конфигурация через YAML
- ✅ **Новые API endpoints** - /upcoming, /categories, /result
- ✅ **Реальный календарь событий** - подключение к live API вместо mock данных
- ✅ **Инструменты обновления** - автоматическое обновление результатов событий
- ✅ **Полное тестирование** - unit и integration тесты для всех компонентов

**🎉 Версия v2.2 - Digest UI/UX Improvements (10 октября 2025):**
- ✅ **Улучшенные карточки дайджестов** - убрано дублирование, добавлены цветные бейджи
- ✅ **HTML-рендеринг в preview** - корректное отображение форматированного текста
- ✅ **Компактная модалка создания** - оптимизирована высота и отступы
- ✅ **Персистентность отзывов** - отзывы сохраняются при навигации между страницами
- ✅ **Исправлено дублирование текста** - умное извлечение заголовков из HTML
- ✅ **API расширен** - добавлены поля feedback_score и feedback_count
- ✅ **UX оптимизация** - улучшена структура и читаемость интерфейса

**🎉 Стабильная версия v2.1 - Готовность к продакшену (9 октября 2025):**
- ✅ **Персонализированное приветствие** - стабильная работа с Telegram WebApp API
- ✅ **AI Дайджесты v2** - 4 новых стиля (newsroom, analytical, magazine, casual)
- ✅ **Система отзывов** - кнопки 👍/👎 с предотвращением дублирования
- ✅ **Безопасная аутентификация** - HMAC SHA256 + нормализация имен
- ✅ **Стабильная база данных** - миграции, индексы, retry логика
- ✅ **Полное тестирование** - 52 теста, все сценарии покрыты
- ✅ **Готовность к продакшену** - мониторинг, логирование, документация

**🔒 Secure Telegram Authentication System - Безопасная аутентификация (6 января 2025):**
- ✅ **HMAC SHA256 проверка** - криптографическая проверка данных Telegram WebApp
- ✅ **Name Normalization System** - защита от emoji-only имён, невидимых символов, стилизованных Unicode
- ✅ **Flask Session Security** - защищённые куки, CSRF защита, HTTPS-only в production
- ✅ **CORS Configuration** - ограничение доступа по доменам Telegram
- ✅ **Security Monitoring** - логирование всех попыток аутентификации
- ✅ **Fallback Compatibility** - плавная миграция со старой системы
- ✅ **Complete Test Coverage** - 52 теста для нормализации имён и аутентификации
- ✅ **Production Ready** - готова к использованию

**🚀 AI Digest Journalistic System v2 - Профессиональная журналистика (9 октября 2025):**
- ✅ **4 новых стиля** - newsroom, analytical, magazine, casual
- ✅ **4 тона подачи** - neutral, insightful, critical, optimistic  
- ✅ **3 длины дайджестов** - short (100 слов), medium (250 слов), long (500 слов)
- ✅ **2 аудитории** - general (широкая), pro (профессионалы)
- ✅ **Строгая валидация** - importance ≥ 0.6, credibility ≥ 0.7
- ✅ **Запрет галлюцинаций** - только факты из источников
- ✅ **Few-shot примеры** - реалистичные образцы для каждого стиля
- ✅ **Обратная совместимость** - fallback к v1 при ошибках
- ✅ **CLI утилита** - tools/show_news.py для тестирования
- ✅ **Конфигурация** - config/styles.yaml с дефолтами по категориям
- ✅ **Полное покрытие тестами** - 15+ новых тестов
- ✅ **Frontend интеграция** - новые иконки и анимации
- ✅ **Production Ready** - готово к использованию

**📊 AI Digest Quality & Metrics System - Система качества и метрик (9 октября 2025):**
- ✅ **Метрики качества** - confidence, generation_time_sec, feedback_score
- ✅ **Система обратной связи** - 👍/👎 кнопки в UI для оценки дайджестов
- ✅ **Аналитика дайджестов** - ежедневная агрегация метрик в digest_analytics
- ✅ **API для метрик** - /metrics и /metrics/history endpoints
- ✅ **Отслеживание времени** - автоматическое измерение времени генерации
- ✅ **CLI поддержка** - tools/show_news.py с --feedback параметром
- ✅ **Showcase дайджесты** - tools/showcase_digest.py для демонстрации
- ✅ **Полное покрытие тестами** - test_metrics.py и test_showcase.py
- ✅ **Production Ready** - готова к использованию

**🎨 Dark Mode Optimization - Полная поддержка тёмной темы (9 октября 2025):**
- ✅ **Исправлен контраст** во всех компонентах для тёмной темы
- ✅ **Оптимизированы модальные окна** - устранена проблема "белое на белом"
- ✅ **Улучшены цвета статистики** - читаемые тренды и показатели
- ✅ **Обновлена десктопная навигация** - корректные темные стили
- ✅ **Исправлены уведомления** - правильные цвета успеха/ошибки
- ✅ **Проверены все UI компоненты** - полная поддержка dark mode
- ✅ **Создан детальный отчёт** - DARK_MODE_AUDIT_REPORT.md
- ✅ **Production Ready** - идеальный контраст в обеих темах

**🤖 AI Digest System - Полная интеграция (8 января 2025):**
- ✅ **AI Digest WebApp Integration** - полная интеграция в WebApp
- ✅ **Персонализированные темы** - аналитический/бизнес/мемный стили
- ✅ **User Management System** - персональные дайджесты для каждого пользователя
- ✅ **Telegram WebApp Authentication** - автоматическое получение user_id
- ✅ **Soft Delete & Archive System** - управление дайджестами
- ✅ **News-style UI** - карточки дайджестов как новости с модальными окнами
- ✅ **Database Integration** - полная интеграция с Supabase
- ✅ **👤 Автосоздание пользователей** - новые пользователи создаются автоматически
- ✅ **🎯 Персонализированное приветствие** - обращение по имени с учетом времени суток
- ✅ **Production Ready** - готово к использованию

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
- 🔗 **[Git Hooks](docs/GIT_HOOKS.md)** - Автоматические проверки качества кода

## 🤖 AI Digest Journalistic System v2

PulseAI теперь поддерживает профессиональную журналистскую генерацию дайджестов с 4 стилями, 4 тонами, 3 длинами и 2 аудиториями.

### **Стили (Style Profiles):**
- **newsroom** — Reuters/Bloomberg стиль, факты, 1-2 абзаца
- **analytical** — глубокий анализ с причинно-следственными связями
- **magazine** — storytelling, engaging тон, метафоры
- **casual** — разговорный стиль для Telegram

### **Тоны (Tone):**
- **neutral** — сбалансированная подача
- **insightful** — акцент на инсайты и контекст
- **critical** — критический анализ
- **optimistic** — позитивный фокус

### **Длина (Length):**
- **short** — до 100 слов, 1-2 абзаца
- **medium** — до 250 слов, 2-3 абзаца
- **long** — до 500 слов, 3-5 абзацев

### **Аудитория (Audience):**
- **general** — широкая аудитория
- **pro** — профессионалы в теме

### **Примеры использования:**

```bash
# CLI утилита для тестирования
python tools/show_news.py --category tech --ai --style analytical --tone insightful --length medium
python tools/show_news.py --category crypto --ai --style newsroom --tone neutral --length short --use-v2

# Программное использование
from digests.ai_summary import generate_summary_journalistic_v2

result = generate_summary_journalistic_v2(
    news_items=news_items,
    category="tech",
    style_profile="analytical",
    tone="insightful",
    length="medium",
    audience="general"
)
```

## 📊 Quality & Metrics System

PulseAI включает комплексную систему оценки качества и метрик для AI-дайджестов:

### Метрики качества
- **Confidence Score** (0.0-1.0) — оценка уверенности AI в качестве дайджеста
- **Generation Time** — время генерации дайджеста в секундах
- **Feedback Score** — средняя оценка пользователей (0.0-1.0)
- **Feedback Count** — количество полученных оценок

### Система обратной связи
- **UI Integration** — кнопки 👍/👎 в карточках дайджестов и модальных окнах
- **API Endpoint** — `/api/feedback` для отправки оценок
- **Real-time Updates** — мгновенное обновление метрик после получения отзыва

### Аналитика и мониторинг
- **Daily Analytics** — автоматическая агрегация метрик по дням
- **Metrics API** — `/metrics` и `/metrics/history` для получения статистики
- **Health Check** — интеграция метрик в `/api/health` endpoint

### CLI инструменты
- **Feedback Support** — `tools/show_news.py --feedback SCORE --digest-id ID`
- **Showcase Generation** — `make showcase` для создания демонстрационных дайджестов
- **Quality Testing** — автоматизированное тестирование качества генерации

### База данных
- **Extended Schema** — новые поля в таблице `digests`
- **Analytics Table** — `digest_analytics` для агрегированных метрик
- **Indexes** — оптимизированные индексы для быстрого доступа

---

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

# Генерация дайджеста дня
make showcase         # Генерация дайджеста дня
```

## 🔧 Shell-скрипты управления

PulseAI включает набор shell-скриптов для управления сервисами с поддержкой логирования и гибкой настройкой.

### Запуск сервисов

```bash
# Запуск с проверкой здоровья (рекомендуется)
./start_services.sh

# Быстрый запуск без проверок
./start_services.sh --skip-health-check

# Обратная совместимость (симлинк на start_services.sh)
./start_services_safe.sh

# Справка по параметрам
./start_services.sh --help
```

**Что делает скрипт:**
- Проверяет здоровье проекта (опционально)
- Останавливает старые процессы
- Запускает Flask WebApp (порт 8001)
- Запускает Telegram Bot
- Сохраняет PID в `.flask.pid` и `.bot.pid`
- Логирует всё в `logs/scripts/start_services_YYYYMMDD_HHMMSS.log`

### Проверка статуса

```bash
# Детальная проверка (по умолчанию)
./check_processes.sh

# Краткая проверка
./check_processes.sh --brief

# Обратная совместимость (симлинк на check_processes.sh)
./check_processes_safe.sh

# Справка по параметрам
./check_processes.sh --help
```

**Что показывает детальная проверка:**
- Статус процессов (Flask, Telegram Bot, Cloudflare Tunnel)
- CPU, память, uptime каждого процесса
- Состояние портов (8001, 3000)
- Доступность HTTP endpoints
- Состояние PID и lock файлов
- Лог сохраняется в `logs/scripts/check_processes_YYYYMMDD_HHMMSS.log`

### Остановка сервисов

```bash
# Остановить все сервисы
./stop_services.sh
```

**Что делает скрипт:**
- Останавливает процессы по PID-файлам
- Принудительно завершает оставшиеся процессы
- Очищает `.flask.pid`, `.bot.pid`, lock-файлы
- Логирует всё в `logs/scripts/stop_services_YYYYMMDD_HHMMSS.log`

### Мониторинг и автовосстановление

```bash
# Проверить и восстановить упавшие сервисы
./monitor_services.sh

# Добавить в crontab для автомониторинга каждые 5 минут
*/5 * * * * cd /Users/denisfedko/news_ai_bot && ./monitor_services.sh
```

**Что делает скрипт:**
- Проверяет доступность Flask, Telegram Bot, Cloudflare Tunnel
- Автоматически перезапускает упавшие сервисы
- Логирует всё в `logs/scripts/monitor_services_YYYYMMDD_HHMMSS.log`

### Запуск только Telegram Bot

```bash
# Запустить только бота с защитой от дублирования
./run_bot.sh
```

**Что делает скрипт:**
- Проверяет lock-файлы и процессы
- Предотвращает множественный запуск
- Проверяет доступность всех зависимостей
- Устанавливает обработчики сигналов для корректной остановки
- Логирует всё в `logs/scripts/run_bot_YYYYMMDD_HHMMSS.log`

### Проверка зависимостей

```bash
# Проверить зависимости и конфигурацию
./check_dependencies.sh
```

**Что проверяет:**
- Импорты основных модулей Python
- Переменные окружения (TELEGRAM_BOT_TOKEN, OPENAI_API_KEY)
- Подключение к базе данных

### Логирование

Все скрипты сохраняют детальные логи в директорию `logs/scripts/`:
- `start_services_YYYYMMDD_HHMMSS.log` — запуск сервисов
- `stop_services_YYYYMMDD_HHMMSS.log` — остановка сервисов
- `check_processes_YYYYMMDD_HHMMSS.log` — проверка статуса
- `monitor_services_YYYYMMDD_HHMMSS.log` — мониторинг
- `run_bot_YYYYMMDD_HHMMSS.log` — запуск бота

Формат логов: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`

### Обратная совместимость

Старые имена скриптов работают через симлинки:
- `start_services_safe.sh` → `start_services.sh`
- `check_processes_safe.sh` → `check_processes.sh`

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

## 🔒 Безопасность

PulseAI реализует многоуровневую систему безопасности:

### Telegram WebApp Authentication
- **HMAC SHA256** проверка всех данных от Telegram
- **Временные ограничения** - данные действительны 24 часа
- **Fallback совместимость** для плавной миграции

### Name Normalization System
- Защита от **emoji-only имён**: `🔥🔥🔥` → `User #<user_id>`
- Удаление **невидимых символов**: `John\u200bDoe` → `JohnDoe`
- Конвертация **стилизованных Unicode**: `𝕀𝕧𝕒𝕟` → `Ivan`
- Исправление **испорченной кодировки**: `ÐÐ°Ð½` → `Иван`

### Session Security
- **HTTPOnly куки** - защита от XSS
- **Secure флаг** - только HTTPS в production
- **SameSite защита** - предотвращение CSRF атак
- **24-часовые сессии** с автоматическим истечением

### CORS Configuration
- Ограничение доступа только к доменам Telegram
- Поддержка Cloudflare туннелей
- Блокировка неавторизованных запросов

### Security Monitoring
- Логирование всех попыток аутентификации
- Мониторинг неудачных попыток входа
- Алерты при подозрительной активности

**Подробнее:** [docs/SECURITY.md](docs/SECURITY.md)

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) файл для деталей.

## 🎉 Стабильная версия v2.1

**PulseAI v2.1** — полностью стабильная версия, готовая к продакшену!

### ✅ Что работает идеально:
- **Персонализированное приветствие** с именем пользователя
- **AI Дайджесты** с 4 стилями и системой отзывов
- **Безопасная аутентификация** через Telegram WebApp
- **Стабильная база данных** с миграциями и индексами
- **Полное тестирование** — 52 теста проходят

### 📊 Статистика:
- 👥 **Пользователи:** 3+ активных
- 📰 **Новости:** 597 сегодня из 84 источников
- 🤖 **Дайджесты:** 28+ созданных с рейтингом 0.625-1.0
- ⚡ **Производительность:** API <200ms

### 🚀 Готовность к продакшену:
- ✅ Мониторинг и логирование
- ✅ Безопасность и CORS
- ✅ Retry логика для БД
- ✅ Документация обновлена

**Подробный отчет:** [STABLE_VERSION_REPORT.md](STABLE_VERSION_REPORT.md)

---

## 📞 Поддержка

- 📖 **Документация:** [docs/README.md](docs/README.md)
- 🐛 **Баги:** [Issues](https://github.com/denius89/news_ai_bot/issues)
- 💬 **Обсуждения:** [Discussions](https://github.com/denius89/news_ai_bot/discussions)

---

*PulseAI - AI-powered news and events platform* 🚀
