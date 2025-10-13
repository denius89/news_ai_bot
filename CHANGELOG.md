# Changelog

Все значимые изменения в проекте PulseAI документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased] - 2025-10-13

### Улучшено
- **Shell-скрипты управления v2.0** - объединение и улучшение скриптов
- **start_services.sh** - объединены start_services.sh и start_services_safe.sh с флагом `--skip-health-check`
- **check_processes.sh** - объединены check_processes.sh и check_processes_safe.sh с флагами `--brief` и `--detailed`
- **Логирование скриптов** - все скрипты теперь сохраняют логи в `logs/scripts/` с timestamp
- **Обратная совместимость** - старые имена скриптов работают через симлинки
- **Справка по параметрам** - добавлен флаг `--help` во все основные скрипты
- **Git Hooks v2.0** - исправлены и улучшены pre-commit и pre-push hooks
- **pre-commit hook** - быстрая проверка только staged файлов (синтаксис + критичные ошибки)
- **pre-push hook** - строгая проверка всего проекта или fallback на базовые проверки
- **GitHub Actions workflows** - полная оптимизация CI/CD pipeline
- **integration.yml** - добавлено кеширование, timeout, триггер на push в main
- **daily-digest.yml** - добавлено кеширование, timeout, upload логов при ошибках

### Добавлено
- **Централизованное логирование** - функции log_info, log_success, log_warning, log_error во всех скриптах
- **Цветной вывод** - улучшенная читаемость с использованием ANSI цветов
- **Директория logs/scripts/** - новая директория для логов shell-скриптов
- **Документация скриптов** - новый раздел "Shell-скрипты управления" в README.md
- **docs/GIT_HOOKS.md** - полная документация по git hooks
- **SKIP_HOOKS переменная** - возможность пропуска hooks через `SKIP_HOOKS=1 git commit/push`
- **Интеллектуальные проверки** - hooks адаптируются к наличию инструментов (black, flake8)
- **.github/workflows/tests.yml** - основной CI workflow для автоматических тестов (исправлен broken badge)
- **.github/workflows/code-quality.yml** - проверки качества кода для PR (black, flake8, isort, mypy)
- **.github/workflows/README.md** - полная документация по всем workflows
- **Кеширование pip** - ускорение установки зависимостей в 10+ раз (~30 сек вместо 2-3 мин)
- **Artifacts upload** - автоматическое сохранение логов при ошибках в workflows
- **Timeout защита** - все workflows имеют timeout для предотвращения зависания

### Изменено
- **start_services.sh** - добавлена поддержка флагов, логирование, улучшенная обработка ошибок
- **check_processes.sh** - добавлены режимы brief/detailed, логирование
- **stop_services.sh** - добавлено логирование, улучшенная очистка
- **monitor_services.sh** - добавлено логирование, улучшенный вывод
- **run_bot.sh** - добавлено логирование, улучшенная проверка зависимостей
- **.git/hooks/pre-commit** - убрана зависимость от несуществующего tools/repo_map.py
- **.git/hooks/pre-push** - используется scripts/strict_check.sh если доступны инструменты
- **README.md** - обновлена документация по shell-скриптам и git hooks

### Исправлено
- **pre-commit hook** - больше не пытается запустить несуществующий tools/repo_map.py
- **pre-push hook** - больше не требует обязательно black и make lint
- **Git hooks** - теперь работают с базовыми инструментами Python без дополнительных зависимостей
- **Hooks fallback** - адекватная деградация при отсутствии инструментов качества
- **GitHub Actions badge** - создан отсутствующий tests.yml на который ссылается badge в README
- **Workflows без кеширования** - добавлено кеширование pip во все workflows

### Технические детали
- **Изменено файлов:** 11 (6 shell-скриптов + 2 git hooks + 2 workflows + README.md + CHANGELOG.md + docs/GIT_HOOKS.md)
- **Добавлено файлов:** 3 workflows + 1 документация (.github/workflows/tests.yml, code-quality.yml, README.md)
- **Удалено файлов:** 2 (start_services_safe.sh, check_processes_safe.sh заменены симлинками)
- **Добавлено:** симлинки, logs/scripts/, docs/GIT_HOOKS.md, workflows documentation, SKIP_HOOKS поддержка
- **Формат логов:** [YYYY-MM-DD HH:MM:SS] [LEVEL] message
- **CI/CD:** 4 workflows (tests, integration, code-quality, daily-digest) с кешированием и timeouts

## [3.0.0] - 2025-01-11

### Добавлено
- **Day 17 - Event Intelligence & Notifications** - полноценная система уведомлений и умного управления API
- **Rate Limit Manager (services/rate_limit_manager.py)** - умное управление лимитами для всех 11 провайдеров
- **Event Intelligence Layer** - кеширование и throttling с учетом лимитов каждого провайдера
- **Notification System (services/notification_service.py)** - персональные уведомления с фильтрацией по категориям
- **Telegram Sender (notifications/telegram_sender.py)** - интеграция отправки уведомлений через бота
- **SSE Real-time Stream (services/events_stream.py)** - обновления событий в реальном времени
- **Smart Scheduler (tools/events_scheduler.py)** - планировщик фетчей с учетом rate limits
- **Notification Sender Tool (tools/send_notifications.py)** - CLI для отправки уведомлений
- **WebApp Settings UI (NotificationSettings.tsx)** - React компонент для настройки уведомлений
- **User Preferences API** - endpoints `/api/user/preferences` (GET/POST) и `/api/user/notifications/test`
- **User Personalization** - таблицы user_preferences и event_logs в БД

### Изменено
- **services/notification_service.py** - полная реализация вместо placeholder
- **routes/api_routes.py** - добавлены 3 новых endpoint для user preferences
- **README.md** - обновлена информация о Day 17
- **CHANGELOG.md** - добавлена информация о новой функциональности

### Технические детали
- **Изменено файлов:** 8+ (services, routes, webapp, tools, notifications)
- **Новых API endpoints:** 3 (/user/preferences GET/POST, /user/notifications/test)
- **SQL миграция:** 2 новые таблицы (user_preferences, event_logs) + 5 индексов
- **Rate limits:** 11 провайдеров с индивидуальными лимитами и кешированием
- **CLI tools:** 2 новых исполняемых скрипта

## [2.4.0] - 2025-01-11

### Добавлено
- **Day 16 - Event Expansion & AI Calendar Part 2** - ML-фильтрация v2 и Smart Sync
- **ML-фильтрация v2 (ai_modules/importance_v2.py)** - оценка важности без AI вызовов, использует ML фичи
- **Smart Sync система (tools/events/smart_sync.py)** - инкрементальное обновление только изменившихся событий
- **CoinMarketCal провайдер** - интеграция крупнейшего крипто-календаря с vote-based важностью
- **OECD провайдер** - экономические события ОЭСР (placeholder для HTML scraping)
- **Notification Service (services/notification_service.py)** - заглушка для будущих уведомлений
- **Enhanced API** - флаг `important=true` в `/api/events/upcoming` для фильтрации важных событий
- **Новые поля БД** - importance_score, credibility_score, sync_status, last_synced_at
- **Unit тесты** - tests/unit/ai_modules/test_importance_v2.py

### Изменено
- **tools/events/fetch_events.py** - интеграция ML-фильтрации v2 вместо простого порога
- **database/events_service.py** - методы get_event_by_hash() и update_event() для Smart Sync
- **routes/events_routes.py** - поддержка флага important для фильтрации событий
- **config/data/sources_events.yaml** - добавлены OECD, IMF, WEF провайдеры

### Технические детали
- **Изменено файлов:** 10+ (ai_modules, tools, database, routes, config)
- **Добавлено провайдеров:** 2 (CoinMarketCal, OECD)
- **SQL миграция:** 4 новых поля + 3 constraints + 5 indexes
- **Тестов:** 1 новый файл (test_importance_v2.py)

## [2.3.0] - 2025-01-11

### Добавлено
- **Day 15 - Event Expansion & AI Calendar** - масштабное расширение системы событий
- **20+ новых провайдеров событий** - crypto (CoinGecko, DeFi Llama, TokenUnlocks), sports (Football-Data, TheSportsDB), markets (Finnhub), tech (GitHub Releases), world (UN Security Council)
- **AI фильтрация событий** - автоматическая фильтрация по importance ≥ 0.6
- **Расширенная база данных** - новые поля: status, result_data, unique_hash, metadata, updated_at
- **Динамическая загрузка провайдеров** - конфигурация через config/data/sources_events.yaml
- **Новые API endpoints** - /api/events/upcoming, /api/events/categories, /api/events/{id}/result
- **Инструменты обновления событий** - tools/events/update_event_results.py
- **Полное тестирование** - unit тесты для BaseEventProvider, integration тесты для полного flow

### Изменено
- **events/events_parser.py** - динамическая загрузка провайдеров из конфигурации
- **database/events_service.py** - методы для работы с events_new таблицей
- **tools/events/fetch_events.py** - AI фильтрация, поддержка новых параметров
- **routes/events_routes.py** - новые endpoints для upcoming событий и категорий
- **webapp/src/pages/EventsPage.tsx** - подключение к реальному API вместо mock данных
- **Frontend календаря** - loading states, error handling, retry functionality

### Удалено
- **events/providers/investing.py** - старый провайдер Investing удален
- **Mock данные в EventsPage** - заменены на реальные API вызовы

### Исправлено
- **Дедупликация событий** - через unique_hash поле
- **Обновление результатов** - автоматическое обновление статуса completed событий
- **Конфигурация провайдеров** - централизованное управление через YAML

### Технические детали
- **Изменено файлов:** 15+ (providers, services, routes, frontend, tests)
- **Добавлено провайдеров:** 9 (crypto: 3, sports: 2, markets: 1, tech: 1, world: 1)
- **Новых API endpoints:** 3
- **Тестов:** 2 новых файла (unit + integration)
- **SQL миграция:** расширение events_new таблицы

## [2.2.0] - 2025-10-10

### Добавлено
- **Digest UI/UX Improvements** - улучшенный интерфейс дайджестов
- **HTML-рендеринг в preview** - корректное отображение форматированного текста в карточках
- **Персистентность отзывов** - отзывы сохраняются при навигации между страницами
- **API поля feedback_score и feedback_count** - расширена информация о дайджестах

### Изменено
- **Структура карточек дайджестов** - убрано дублирование, категория и стиль в цветных бейджах
- **Модалка создания дайджестов** - оптимизирована высота и отступы (space-y-6 → space-y-4)
- **Логика заголовков** - умное извлечение из HTML тегов или первого предложения
- **Обработка отзывов** - инициализация состояния из API при загрузке дайджестов

### Исправлено
- **Дублирование текста в preview** - убрано повторение первых 100 символов
- **HTML теги отображались как текст** - добавлен dangerouslySetInnerHTML
- **Отзывы сбрасывались при навигации** - добавлена персистентность через API
- **Высота модалки создания** - сделана более компактной

### Технические детали
- **Изменено файлов:** 3 (DigestPage.tsx, DigestGenerator.tsx, api_routes.py)
- **Добавлено полей в API:** feedback_score, feedback_count
- **Оптимизирована высота модалки:** space-y-6 → space-y-4, py-3 → py-2

## [2.1.0] - 2025-10-09

### Добавлено
- **Персонализированное приветствие** - стабильная работа с Telegram WebApp API
- **AI Дайджесты v2** - 4 новых стиля (newsroom, analytical, magazine, casual)
- **Система отзывов** - кнопки 👍/👎 с предотвращением дублирования
- **Безопасная аутентификация** - HMAC SHA256 + нормализация имен
- **Стабильная база данных** - миграции, индексы, retry логика
- **Полное тестирование** - 52 теста, все сценарии покрыты

### Изменено
- **Dark Mode Optimization** - полная поддержка с корректным контрастом
- **Unicode Names** - корректная обработка всех типов имён
- **AI Digest System** - персонализация и аналитика
- **Infrastructure** - стабильность и надёжность

### Исправлено
- **Контраст в статистических карточках** - слабые цвета в темной теме
- **Десктопная навигация** - отсутствие dark mode стилей
- **Уведомления** - жёстко заданные цвета без адаптации
- **Модальные окна** - проблема "белое на белом" в темной теме
- **Unicode stylized names** - проблема с двойной UTF-8 кодировкой

## [2.0.0] - 2025-01-06

### Добавлено
- **Secure Telegram Authentication System** - безопасная аутентификация
- **HMAC SHA256 проверка** - криптографическая проверка данных Telegram WebApp
- **Name Normalization System** - защита от emoji-only имён, невидимых символов, стилизованных Unicode
- **Flask Session Security** - защищённые куки, CSRF защита, HTTPS-only в production
- **CORS Configuration** - ограничение доступа по доменам Telegram
- **Security Monitoring** - логирование всех попыток аутентификации
- **Complete Test Coverage** - 52 теста для нормализации имён и аутентификации

### Изменено
- **Authentication Flow** - переход на HMAC SHA256 вместо простой проверки headers
- **User Name Storage** - нормализация и валидация имён пользователей
- **Security Headers** - добавлены защитные заголовки и CORS политики

### Исправлено
- **Security Vulnerabilities** - уязвимости в аутентификации
- **Unicode Name Issues** - проблемы с отображением имён пользователей
- **Session Management** - улучшено управление сессиями

## [1.0.0] - 2024-12-XX

### Добавлено
- **Initial Release** - первая стабильная версия PulseAI
- **Telegram Bot** - базовый функционал бота
- **Web App** - веб-интерфейс для управления
- **AI Digest System** - генерация дайджестов
- **Database Integration** - интеграция с Supabase
- **Basic Authentication** - простая аутентификация через Telegram

---

*Формат версий: [MAJOR.MINOR.PATCH] - дата в формате YYYY-MM-DD*
