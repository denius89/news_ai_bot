# 📝 Changelog - PulseAI

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

---

## [Unreleased]

### Исправлено
- **UI/UX улучшения** (24 октября 2025)
  - Исправлен порядок кнопок периода в генераторе дайджестов
  - Теперь порядок логичный: "Сегодня" → "За неделю" → "За месяц"
  - Улучшен пользовательский опыт при выборе временного периода

### Добавлено
- **Полная унификация админ-панели** (22 октября 2025)
  - Унифицированы все компоненты с NeoGlass дизайн-системой
  - Переведен весь интерфейс админки на русский язык
  - Созданы переиспользуемые UI компоненты: Toggle, Chip, Accordion, StatusIndicator
  - Добавлена система design tokens для семантических цветов
  - Реализована единая система стилей для всех админ-компонентов
- **Архитектурные улучшения админки** (22 октября 2025)
  - System Monitor перенесен из Config в Metrics как отдельный таб
  - News Control и Events Control объединены в единый раздел Content
  - Улучшена навигация с табами для лучшей организации функций
  - Оптимизирована структура компонентов для переиспользования
- **Техническая очистка проекта** (22 октября 2025)
  - Удалены неиспользуемые файлы: AdminTest.tsx, TestMetrics.tsx, AdminApp.tsx, AdminMetricsEnhanced.tsx
  - Исправлены все CSS классы: text-muted-foreground → text-muted
  - Очищен корень проекта от временных MD файлов и PID файлов
  - Улучшена структура проекта и удален технический долг

### Изменено
- **Дизайн-система админки** (22 октября 2025)
  - Заменены все hardcoded цвета на семантические design tokens
  - Унифицированы стили кнопок, карточек, форм и навигации
  - Улучшена консистентность визуального стиля во всех разделах
  - Оптимизированы анимации и переходы для лучшего UX

### Исправлено
- **Качество кода админки** (22 октября 2025)
  - Исправлены все TypeScript ошибки и предупреждения
  - Улучшена типизация компонентов и хуков
  - Оптимизированы импорты и структура файлов
  - Устранены дублирующиеся компоненты и логика

### Добавлено
- **Настройка IDE для разработки** (17 октября 2025)
  - Настроено автоматическое форматирование кода в VS Code
  - Добавлены правила для Python (Black + Flake8) с автоисправлением при сохранении
  - Настроены задачи для форматирования и проверки качества кода
  - Улучшена конфигурация TypeScript и JSON форматирования
- **Улучшения UI/UX веб-приложения** (17 октября 2025)
  - Реализована новая система навигации AI Dock v4.1 с Perfect Balance дизайном
  - Добавлены Telegram-style стеклянные эффекты для нижней навигации
  - Улучшена видимость навигации в светлой теме
  - Обновлены карточки компонентов до AI Mist визуальной системы
  - Исправлены проблемы с центрированием нижней навигации

### Изменено
- **Оптимизация API запросов** (17 октября 2025)
  - Улучшена производительность при подписке на все категории
  - Оптимизированы запросы к backend для лучшего UX

### Исправлено
- **AI дайджесты теперь отображаются корректно** (17 октября 2025)
  - Исправлен OpenAI API ключ (найден рабочий ключ из корневого .env)
  - Исправлено сохранение в поле `content` вместо только `summary`
  - Обновлены функции в database/db_models.py и routes/api_routes.py
  - Восстановлено содержимое для всех старых дайджестов (5 штук)
- **События не отображались на мобильных** (17 октября 2025)
  - Добавлен fallback: если нет подписок → показывать все события
  - Защита от Invalid Date в компонентах GroupedEventCard и EventCard
  - Оптимизация рендеринга для мобильных устройств

### Добавлено
- **Infinite scroll для событий** (17 октября 2025)
  - Реализован постепенная подгрузка событий (+50 при скролле)
  - Начальная загрузка: 100 событий
  - Индикаторы прогресса: "Показано X из Y"
  - Оптимизация для мобильных устройств (не крашится при 775 событиях)
- **Кнопка "Подняться вверх"** (17 октября 2025)
  - Добавлена во все разделы: Новости, События, Дайджесты
  - Зелёная круглая кнопка с иконкой стрелки
  - Появляется при скролле > 300px
  - Плавная анимация и прокрутка
- **Улучшенная фильтрация по подпискам** (17 октября 2025)
  - Целенаправленная загрузка новостей по категориям подписки
  - Увеличенный буфер (x3-x5) для фильтрации подкатегорий
  - Пользователь с подписками видит 40-60+ новостей вместо 5
  - Аналогичная оптимизация для событий
- **Обновлённая статистика на главной** (17 октября 2025)
  - Реальные данные из БД вместо захардкоженных
  - Новые метрики: "Активные пользователи" и "События на неделю"
  - Убраны бесполезные метрики: "Категории" (всегда 5)
  - Исправлено использование UTC для стабильности подсчёта
- **Автоматическое восстановление .env** (17 октября 2025)
  - Добавлена система автовосстановления .env из Git Stash
  - Интегрировано во все скрипты запуска (start_services.sh, start_bot.sh, START_ADMIN.sh)
  - Создана документация AUTO_ENV_RESTORE.md
  - Защита от случайного удаления конфигурации
  - Не требует ручного вмешательства при запуске
- **Обновление Cursor AI Rules** (17 октября 2025)
  - Исправлен frontmatter для правильной работы alwaysApply: true
  - Обновлены 6 правил: database, dependencies, logging, errors, background jobs, performance
- **Масштабное расширение RSS-источников** (16 октября 2025)
  - **+72 топовых источника** из FeedSpot (топ-100 по каждой категории)
  - Итого: **255 источников в 70 субкатегориях** (было ~183)
  - Русскоязычные источники: GoHa (игры, киберспорт, железо)
  - Crypto: +13 источников (Bitcoinist, CryptoPotato, AMBCrypto, DeFi Pulse, etc.)
  - Sports: +28 источников (Sky Sports, FOX Sports, CBS, BBC, SI, etc.)
  - World: +15 источников (NBC, CBS, CNN, NYT, Guardian, France 24, etc.)
  - Tech: +1 источник (GoHa Hardware)
  - Полная валидация всех источников - все работают корректно
- **ML-оптимизация и самообучение** (16 октября 2025)
  - Обучены локальные ML-модели на 4,499 примерах (F1=0.729-0.744)
  - Локальный предиктор включен и работает
  - **Экономия 60-70% AI токенов** в production
  - Автоматическое самообучение каждые 2 дня
  - Пагинация для сбора до 25,000 примеров
  - Сохранение StandardScaler вместе с моделями
- **Инструменты для работы с новостями**
  - `tools/news/fetch_and_train.py` - умный парсинг с автообучением
  - `tools/news/README.md` - полная документация
  - Документация: QUICK_START_NEWS.md, FINAL_RSS_UPDATE_REPORT.md
- **Масштабное расширение категорий и подкатегорий**
  - 16 новых подкатегорий для новостей (sports: 13, markets: 3)
  - 15 новых подкатегорий в Event Providers
  - 109 новых иконок (backend + frontend маппинг)
  - Полное покрытие: crypto, tech, world уже были, sports и markets расширены
- Admin Panel с полным функционалом (Dashboard, Metrics, Logs, Config)
- Enhanced Metrics с 6 вкладками (News, Events, Users, AI, Digests, System)
- Event Configuration как подвкладка в Sources
- Lucide Icons во всех компонентах Admin Panel
- Base64 кодирование для HTTP headers с кириллицей
- Connection pooling для Supabase клиентов
- Flask-Caching для улучшения производительности
- Система кеширования API endpoints

### Исправлено
- **Качество кода и форматирование** (17 октября 2025)
  - Исправлены все ошибки flake8 в проекте
  - Настроено автоматическое форматирование Black с line-length=120
  - Добавлены задачи VS Code для проверки качества кода
  - Настроена автоматическая органзация импортов и исправление ошибок при сохранении
  - Pre-push hooks теперь проходят успешно
- **Обновлены TODO комментарии** (17 октября 2025)
  - Все TODO привязаны к конкретным этапам MVP Launch плана
  - Добавлены ссылки на Week 2 (Subscriptions) и Week 3 (Performance)
  - 7 TODO обновлены с четким планом реализации
- **Критический баг в self_tuning_trainer.py** - StandardScaler не сохранялся
  - ML-модели обучались, но scaler отсутствовал при загрузке
  - Локальный предиктор выдавал ошибку "StandardScaler not fitted"
  - Исправлено: scaler теперь сохраняется в models/scaler.pkl
- **Лимит Supabase 1,000 записей** в сборе данных для обучения
  - Добавлена пагинация с .range() для сбора до 25,000 примеров
  - Полный датасет теперь используется для обучения моделей
- Критическая ошибка с кириллическими символами в HTTP headers
- Несинхронизированные Cloudflare URL во всех сервисах
- Проблемы с аутентификацией пользователей с кириллическими именами
- Проблемы с параллельными запросами в Flask
- Неправильные default значения для AI метрик (30 дней → 7 дней)
- Проблемы с отображением данных в Admin Panel

### Изменено
- **Event Providers расширены новыми подкатегориями:**
  - CoinGecko: +NFT события, gamefi, regulation, security
  - Finnhub: +dividends, умная категоризация economic events (forex, rates, bonds, commodities)
  - GitHub: +категоризация репозиториев (ai, hardware, cybersecurity, startups)
  - UN SC: +умное определение типа встречи (conflicts, sanctions, migration)
- **sources.yaml оптимизирован:**
  - Удалены 13 неработающих RSS источников
  - Добавлены 13 рабочих альтернатив
  - Общее количество: 70 подкатегорий, 197 источников
- Обновлены все Cloudflare URL на актуальный: `https://example.invalid`
- Улучшена производительность API через кеширование
- Обновлен UI Admin Panel с современными компонентами
- Оптимизированы запросы к базе данных

### Удалено
- Устаревшие TODO задачи из первоначального плана
- Неиспользуемые функции нормализации Unicode
- Дублирующиеся конфигурационные файлы

---

## [0.1.0] - 2025-10-15

### Добавлено
- **Admin Panel** - Полнофункциональная панель администратора
  - Dashboard с общей статистикой системы
  - Enhanced Metrics с 6 категориями аналитики
  - Real-time Logs с Server-Sent Events
  - Configuration management с динамическими настройками
  - Event Configuration для управления провайдерами событий

- **Authentication System** - Система аутентификации
  - Telegram WebApp аутентификация
  - Admin privileges проверка
  - DEV mode bypass для разработки
  - Base64 кодирование для HTTP headers

- **API Endpoints** - Расширенные API
  - `/admin/api/*` - Admin Panel API
  - `/admin/api/metrics/*` - Метрики системы
  - `/admin/api/config/*` - Управление конфигурацией
  - `/admin/api/events/*` - Управление событиями
  - `/admin/api/sources/*` - Управление источниками

- **Enhanced Metrics** - Расширенная аналитика
  - News Analytics (timeline, categories, sources)
  - Events Analytics (upcoming, priorities, categories)
  - User Engagement (growth, active users, subscriptions)
  - AI Performance (tokens, costs, quality metrics)
  - Digest Analytics (count, length, feedback)
  - System Health (processes, resources, uptime)

- **Configuration Management** - Управление настройками
  - Dynamic system configuration через `system_config` table
  - AI Settings (models, tokens, thresholds)
  - System Settings (intervals, limits, notifications)
  - Prompts Viewer (read-only AI prompts)
  - Sources Manager (news sources + events providers)
  - System Monitor (real-time status)

- **UI/UX Improvements** - Улучшения интерфейса
  - Lucide Icons во всех компонентах
  - Modern tabbed interface
  - Responsive design
  - Dark mode support
  - Loading states и error handling

### Технические улучшения
- **Performance** - Производительность
  - Flask threading для параллельных запросов
  - Connection pooling для Supabase
  - API endpoint caching (60s TTL)
  - In-memory cache decorator

- **Security** - Безопасность
  - Base64 encoding для non-ASCII characters в HTTP headers
  - Admin privilege validation
  - Request sanitization
  - Secure session management

- **Monitoring** - Мониторинг
  - Real-time system health monitoring
  - Process status tracking
  - Resource usage monitoring
  - Database latency tracking

### Database Changes
- **New Tables**
  - `admins` - Admin users management
  - `system_config` - Dynamic system configuration

- **Migrations**
  - `2025_10_14_add_admins_table.sql`
  - `2025_10_15_system_config.sql`

### Dependencies
- **Added**
  - `Flask-Caching>=2.3.0` - Advanced caching
  - `psutil` - System monitoring
  - `@tanstack/react-query` - Data fetching
  - `recharts` - Charts and graphs
  - `framer-motion` - Animations
  - `lucide-react` - Icons

### Configuration Files
- **Updated**
  - `config/core/cloudflare.py` - Cloudflare tunnel configuration
  - `.env` - Main environment variables
  - `config_files/environment/.env` - Configuration environment
  - `requirements.txt` - Python dependencies

### Documentation
- **Created**
  - `ADMIN_PANEL_IMPLEMENTATION.md` - Detailed implementation guide
  - `ADMIN_FINAL_REPORT.md` - Final implementation report
  - `ADMIN_CONFIG_COMPLETE.md` - Configuration page report
  - `ADMIN_METRICS_PHASE1_COMPLETE.md` - Phase 1 metrics report
  - `ADMIN_METRICS_PHASE2_COMPLETE.md` - Phase 2 metrics report
  - `WEBAPP_FIX_CYRILLIC_HEADERS.md` - Cyrillic headers fix documentation
  - `CLOUDFLARE_URL_AUDIT_REPORT.md` - Cloudflare URL audit
  - `CURRENT_SERVICES_STATUS.md` - Services status
  - `FINAL_SESSION_SUMMARY.md` - Session summary
  - `DEPLOYMENT_STATUS.md` - Deployment status
  - `CHANGELOG.md` - This file

---

## [0.0.1] - 2025-10-14

### Добавлено
- Базовая структура PulseAI проекта
- Telegram Bot интеграция
- Flask WebApp
- PostgreSQL/Supabase интеграция
- Базовая система новостей и событий
- RSS парсинг
- AI обработка контента
- Система дайджестов

### Технические детали
- Python 3.11+
- Flask 3.0+
- React 18 + TypeScript
- PostgreSQL (Supabase)
- Telegram Bot API
- OpenAI API integration

---

## Соглашения

### Типы изменений
- **Добавлено** - для новых функций
- **Изменено** - для изменений в существующей функциональности
- **Устарело** - для функций, которые скоро будут удалены
- **Удалено** - для удаленных функций
- **Исправлено** - для любых исправлений ошибок
- **Безопасность** - для исправлений уязвимостей

### Версионирование
- **MAJOR** - несовместимые изменения API
- **MINOR** - новая функциональность, обратно совместимая
- **PATCH** - исправления ошибок, обратно совместимые

---

**Последнее обновление:** 2025-10-15
**Версия:** 0.1.0
**Статус:** ✅ Стабильная
