# 🚀 Roadmap PulseAI (30 дней)

PulseAI — **AI-Driven News & Events Platform**, которая превращает хаотичный поток новостей и событий в персональные дайджесты, умный календарь и автоматический контент-менеджмент для Telegram и WebApp.

---

## Week 1 — Core & Quality (ядро)
**✅ Day 1 — Docs + Review Parsers**
- Созданы: `VISION.md`, `ROADMAP.md`, `COMMUNICATION.md`
- Review парсеров (`rss_parser.py`, `events_parser.py`)
- CI setup (`.github/workflows/tests.yml`)
- Проверка `db_models.py` и логирования
- Тестовый прогон: источники → БД

**Day 2 — Источники и очистка**
- Добавить 2–3 новых источника в `config/sources.yaml`
- Починить парсинг проблемных RSS (Axios, Reuters)
- Вынести HTML-очистку в `utils/clean_text.py`
- Тесты для новых источников (`tests/test_parsers.py`)
- Fix дублей в БД (`make_uid`)

**Day 3 — Credibility & Importance**
- Прогон AI-модулей на реальных данных
- Логирование ошибок AI (fallback)
- Unit-тесты для `ai_modules/`
- Метка AI-версии в новостях
- Обновить `README.md` (раздел AI-модули)

**Day 4 — AI Summary**
- Расширить `digests/ai_summary.py` (стили: аналитический, деловой, мемный)
- Добавить «почему важно» в дайджесты
- Тесты для `generate_digest()` (разные стили)
- WebApp: обновить `digest.html`
- Логирование времени генерации дайджеста

**Day 5 — Фильтры и UI**
- Добавить таблицу `topics` в БД
- Привязка тем к `config/sources.yaml`
- Фильтры по темам в `webapp.py`
- WebApp UI: выбор темы (dropdown)
- Unit-тесты фильтрации

---

## Week 2 — Subscriptions & Telegram
**Day 6 — Subscriptions**
- Таблица `subscriptions` в БД
- Методы `subscribe/unsubscribe`
- WebApp UI: управление подписками
- Тесты для подписок
- Обновить `MASTER_FILE.md`

**Day 7 — Telegram Bot MVP**
- MVP на `aiogram`
- Команды `/start`, `/digest`, `/help`
- Привязка к Supabase
- Тестовый деплой бота
- Интеграционный тест (`pytest.mark.integration`)

**Day 8 — Inline-фильтры**
- Inline-фильтры в боте
- Команда `/subscribe`
- Webhook или polling setup
- Логирование сообщений бота
- Тесты с mock Telegram API

**Day 9 — Автодайджесты**
- Автодайджесты по крону (утро/вечер)
- Логирование отправленных дайджестов
- Экспорт календаря событий в `.ics`
- UI: «Неделя впереди»
- Тесты авто-дайджестов

**Day 10 — ETL-пайплайн**
- Очистка HTML, fallback для пустых полей
- Дедупликация (по `uid`)
- Логирование ошибок с trace_id
- E2E тест: новости → БД → дайджест → Telegram
- Обновить `docs/ARCHITECTURE.md`

---

## Week 3 — Growth & Value
**Day 11 — Новые источники**
- Добавить категории: технологии, регуляторка
- Парсинг Twitter/X, LinkedIn (MVP)
- Поддержка новых категорий в БД
- UI: выбор категорий
- Тесты соцсетей

**Day 12 — Приоритеты событий**
- Поддержка приоритетов (low/med/high)
- Парсинг с Investing (priority mapping)
- Отображение бейджа приоритета в UI
- Фильтр по приоритету
- Тесты нормализации

**Day 13 — Календарь**
- Улучшенный календарь (сортировка, поиск)
- Подписки на события по ключевым словам
- Экспорт календаря в Google Calendar API
- Unit-тесты для экспорта
- Документация в `docs/ARCHITECTURE.md`

**Day 14 — Аналитика**
- Аналитика в WebApp (графики, активность)
- Логирование использования (events log)
- Хранение статистики в БД
- Тесты аналитики
- Обновить `ROADMAP.md`

**Day 15 — Real-time**
- Real-time уведомления (важные события)
- Push через Telegram
- Валидация подписок
- Тесты real-time
- Итоговый отчёт недели

---

## Week 4 — AI, White-Label & Launch
**Day 16–17 — AI-аннотации**
- Сравнение моделей (GPT-4, LLaMA, Mistral)
- Тесты моделей (BLEU/ROUGE)
- Выбор best-of
- Документация: сравнение моделей
- Обновить `README.md`

**Day 18–19 — White-label**
- API `/api/digest`
- Шаблоны white-label фронтенда
- Кастомизация бренда (цвета, лого)
- Unit-тесты API
- Документация white-label

**Day 20–22 — Монетизация B2B**
- SaaS-планы (Basic/Pro/Enterprise)
- Авторизация пользователей (Supabase Auth)
- Billing MVP (Stripe/crypto)
- Тесты авторизации и биллинга
- Обновить `VISION.md`

**Day 23–24 — Freemium B2C**
- Ограниченный дайджест (free)
- Premium-функции (фильтры, календари)
- Тесты тарифов
- Обновить `README.md`

**Day 25–27 — Growth-хуки**
- Реферальная система
- Партнёрки (брокеры, аналитика)
- Логирование партнёрских кликов
- Тесты рефералок
- Обновить `docs/COMMUNICATION.md`

**Day 28–30 — Финализация**
- Финализация MVP
- E2E тесты: новости → Telegram → отчёт
- Полная документация (`README.md`, `DEPLOY.md`)
- Презентация продукта
- Подготовка к релизу

---

## 📊 Бэклог
- Повышение покрытия тестами ≥ 70%
- CI: линтеры (flake8, black, isort, mypy)
- Growth & мультиплатформенность
- Монетизация (расширенные тарифы)
- Экспорт в сторонние сервисы (Slack, Discord)