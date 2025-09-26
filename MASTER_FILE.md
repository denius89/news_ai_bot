# 📰 News AI Bot — MASTER_FILE

Файл **MASTER_FILE.md** — свод правил, архитектуры и соглашений проекта.  
Это основной документ для разработчиков и участников проекта.

---

## Docs Index
- [VISION](docs/VISION.md)
- [ROADMAP](docs/ROADMAP.md)
- [COMMUNICATION](docs/COMMUNICATION.md)

---

## Правила (коротко)
- Git: коммит/пуш после каждого шага.
- Задачи: в TASKS.md, приоритеты 🔴/🟡/🟢.
- Решения и договорённости фиксируем здесь.

---

## Решения по парсерам и базе (Day 01)
- rss_parser.py/events_parser.py: привести к единому формату записи (см. ниже чек-лист ревью).
- db_models.py: проверить уникальные ключи, индексы; логирование на уровне INFO.

---



## Решения по источникам и очистке (Day 02)

### Что и почему
- **Источники:** убран Axios (нет стабильного RSS) и временно исключён Reuters (DNS/доступность). Добавлены новые RSS (CoinDesk, Cointelegraph, Bloomberg Markets, TechCrunch и др.).
- **Очистка текста:** вынесена в `utils/clean_text.py` (единый препроцессинг).
- **Дедупликация:** `uid = sha256(url|title)`, `upsert` по `uid` — убрали дубли при массе источников.
- **Утилиты:** добавлен `tools/show_news.py` для просмотра последних новостей из БД.
- **Константы:** `COUNTRY_MAP`, категории и теги вынесены в `config/constants.py`.
- **Документация:** обновлены `README.md`, `docs/DEPLOY.md`, `docs/ARCHITECTURE.md` (Mermaid-схема).

### Технические детали
- MIME‑проверка для RSS (`requests` → заголовок `Content-Type` должен содержать `xml`/`rss`), иначе — ошибка загрузки.
- Нормализация дат: `dateutil` → UTC (`astimezone(timezone.utc)`).
- Очистка HTML: BeautifulSoup → `.get_text()`, нормализация пробелов.
- Фильтр дублей на уровне парсера (in‑memory `seen`) + на уровне БД (`on_conflict="uid"`).
- Логи: именованные логгеры `parsers.rss`, `parsers.events`, `database`, единый формат через `utils/logging_setup.py`.

### Результат
- Дублей в таблице `news` нет.
- Парсинг стабильный: проблемные источники отключены/заменены.
- Тесты для парсеров и утилит проходят.

## 📂 Структура проекта

> ℹ️ **Примечание**
> Файл `CODEMAP.md` генерируется автоматически скриптом [`tools/repo_map.py`](tools/repo_map.py).
> Если структура в `MASTER_FILE.md` и `CODEMAP.md` различаются — приоритет у `CODEMAP.md`.
> Обновить карту проекта:
>
> ```bash
> python tools/repo_map.py
> ```

📌 Снимок структуры на момент редактирования (актуальную **всегда** смотри в `CODEMAP.md`):

```text
├── .github/
│   └── workflows/
│       ├── integration.yml
│       └── tests.yml
├── ai_modules/
│   ├── init.py
│   ├── credibility.py
│   └── importance.py
├── config/
│   ├── init.py
│   ├── constants.py
│   ├── logging.yaml
│   └── sources.yaml
├── database/
│   ├── init.py
│   ├── db_models.py
│   ├── init_tables.sql
│   └── seed_data.sql
├── digests/
│   ├── init.py
│   ├── ai_summary.py
│   └── generator.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMUNICATION.md
│   ├── DEPLOY.md
│   ├── ROADMAP.md
│   └── VISION.md
├── logs/
├── parsers/
│   ├── init.py
│   ├── events_parser.py
│   └── rss_parser.py
├── routes/
│   ├── init.py
│   └── news_routes.py
├── static/
│   └── style.css
├── telegram_bot/
│   ├── __init__.py
│   ├── bot.py
│   ├── config.py
│   ├── keyboards.py
│   ├── utils/
│   │   └── formatters.py
│   └── handlers/
│       ├── __init__.py
│       ├── start.py
│       ├── digest.py
│       ├── digest_ai.py
│       └── events.py
├── templates/
│   ├── base.html
│   ├── digest.html
│   ├── events.html
│   └── index.html
├── tests/
│   ├── init.py
│   ├── conftest.py
│   ├── test_ai_modules.py
│   ├── test_ai_summary.py
│   ├── test_clean_text.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_deepl.py
│   ├── test_digests.py
│   ├── test_main.py
│   ├── test_main_import.py
│   ├── test_openai.py
│   ├── test_parsers.py
│   ├── test_routes.py
│   ├── test_supabase.py
│   └── test_webapp.py
├── tools/
│   ├── fetch_and_store_events.py
│   ├── fetch_and_store_news.py
│   ├── fix_old_news.py
│   ├── repo_map.py
│   └── show_news.py
├── .editorconfig
├── .env.example
├── .gitignore
├── CODEMAP.md
├── config.py
├── CONTRIBUTING.md
├── LICENSE
├── main.py
├── MASTER_FILE.md
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
├── setup.cfg
├── TASKS.md
└── webapp.py
```

## 🗄️ База данных

Проект использует **Supabase (PostgreSQL)** вместо локальной SQLite.  

### Таблица `news` (основная)
| Поле         | Тип         | Описание |
|--------------|-------------|----------|
| uid          | text (PK)   | Уникальный идентификатор `sha256(url|title)` |
| title        | text        | Заголовок новости |
| link         | text        | Ссылка на источник |
| published_at | timestamptz | Дата и время публикации (UTC) |
| content      | text        | Текст новости (если доступен) |
| credibility  | numeric     | Оценка достоверности (AI) |
| importance   | numeric     | Оценка важности (AI) |
| source       | text        | Источник (название из конфигурации) |
| category     | text        | Категория (crypto, economy, world, tech, …) |

**Особенности**  
Функция `upsert_news` сохраняет новости по уникальному `uid = sha256(url|title)`.  
Вставка происходит через `upsert` с `on_conflict="uid"`.  

### Таблица `events`
| Поле        | Тип         | Описание |
|-------------|-------------|----------|
| id          | uuid (PK)   | Уникальный идентификатор |
| title       | text        | Название события |
| country     | text        | Код страны (например, `US`) |
| currency    | text        | Валюта (например, `USD`) |
| importance  | int         | Важность (1 = low, 2 = medium, 3 = high) |
| event_time  | timestamptz | Время события в UTC |
| fact        | text        | Фактическое значение |
| forecast    | text        | Прогноз |
| previous    | text        | Предыдущее значение |

**Особенности**
- `importance` теперь хранится как **int (1–3)**.
- При парсинге Investing значения `low/medium/high` конвертируются в числа через `IMPORTANCE_TO_PRIORITY`.
- Это позволяет унифицировать хранение и использовать при фильтрации событий в Telegram-боте.

---

### Дополнительные таблицы
- **users** — пользователи (например, для будущей интеграции с Telegram-ботом).  
  Поля: `telegram_id`, `created_at`.  
- **digests** — дайджесты для пользователей (в перспективе).  
  Поля: `summary`, `created_at`.  

---

### Особенности
- Функция `upsert_news` сохраняет новости по уникальному `uid = sha256(url|title)`.  
  Вставка происходит через `upsert` с `on_conflict="uid"`.  
- Даты нормализуются в **UTC**.  
- Если `content` отсутствует → поле может быть `NULL`.  
- При вставке новостей и событий сохраняются оценки AI (`credibility`, `importance`).  
- Таблицы создаются через Supabase или локальные SQL-скрипты (`database/init_tables.sql`, `seed_data.sql`).   

## 📜 Логирование

В проекте используется стандартный модуль Python `logging` с централизованной инициализацией в `utils/logging_setup.py`. Конфигурация уровней логов планируется через `config/logging.yaml`.

- Добавлено логирование выбора категорий и ошибок генерации AI-дайджеста (`digest_ai.py`).
- В консоль выводится информация:
  - категория, выбранная пользователем,
  - ошибки OpenAI при генерации текста.
- Это помогает отлаживать работу бота и отслеживать пользовательские сценарии.


### Основные особенности:
- Логи пишутся **одновременно в консоль и файл** `logs/app.log`.
- Для файла используется **ротация**: при достижении определённого размера старые логи сохраняются с суффиксом (`app.log.1`, `app.log.2`, …).
- Формат логов:
    
    YYYY-MM-DD HH:MM:SS,mmm [LEVEL] Сообщение
- В логах дополнительно отображаются:
- список используемых источников (`name`, `category`, `url`),
- количество новостей, загруженных с каждого источника,
- итоговое количество сохранённых новостей.

Пример:
    
    2025-09-18 17:36:52,841 [INFO] Загружаем новости из 24 источников (all)...
    2025-09-18 17:36:52,842 [INFO]   CoinDesk (crypto): https://www.coindesk.com/arc/outboundfeeds/rss/
    2025-09-18 17:36:52,843 [INFO]   BBC World (world): http://feeds.bbci.co.uk/news/world/rss.xml
    2025-09-18 17:36:53,012 [INFO] Получено 50 новостей. Записываем в базу...

### Где смотреть
- **Консоль** — быстрый просмотр во время разработки.
- **logs/app.log** — история для отладки (с ротацией).

> ⚠️ Папка `logs/` добавлена в `.gitignore`, чтобы логи не попадали в репозиторий.

### Инициализация (фрагмент)
Форматирование и ротация настраиваются в `main.py`:
```python
import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("news_ai_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler) 
```
## ▶️ Запуск и утилиты

### Основной скрипт `main.py`
Запускает процесс загрузки и сохранения новостей (ETL) или генерации дайджеста.

Примеры запуска:
    
    # все источники, максимум 20 новостей с каждого (итого до 480), потом общий срез 100
    python main.py --source all --per-source-limit 20 --limit 100
    
    # только крипто, по 20 новостей с каждого источника в категории
    python main.py --source crypto --per-source-limit 20
    
    # только экономика, всего до 10 новостей
    python main.py --source economy --limit 10
    
    # сгенерировать дайджест последних 5 новостей
    python main.py --digest 5
    
    # сгенерировать дайджест с помощью AI
    python main.py --digest 5 --ai

**Параметры:**
- `--source` — набор источников: `all` | `crypto` | `economy` | `world` | `technology` | `politics`  
- `--per-source-limit` — максимум новостей, загружаемых с **каждого источника** (по умолчанию 20)  
- `--limit` — общий максимум новостей за прогон (срез сверху, после объединения всех источников)  
- `--digest` — сформировать текстовый дайджест (по умолчанию 5 новостей)  
- `--ai` — использовать AI для генерации дайджеста (вместо простого списка)  

### Утилита `tools/show_news.py`
Выводит последние новости из базы для проверки.

Пример:
    
    python tools/show_news.py --limit 5

---

### Утилита `tools/fix_old_news.py`
Используется для исправления старых записей в базе:

- Добавляет поле `source`, если оно отсутствует.  
- Обновляет пустой `content`, если появилось описание.  
- Может работать выборочно через флаги (например, только для пропавших источников).  

Пример запуска:
    
    python tools/fix_old_news.py --mode fill-missing

## 🧭 Git-правила
- Основная ветка: `main`
- Новые фичи: `feature/<имя>`
- Правка багов: `fix/<имя>`
- Обновления документации: `docs/<имя>`
- После добавления кода всегда:

  ```bash
  git add .
  git commit -m "type: описание"
  git push
  ```
 
## ✅ Правила правок (GALLOP)
1.  Goal — цель правки
2.  Action — что меняем
3.  Location — где (файл/модуль)
4.  Logic — зачем
5.  Output — что должно получиться
6.  Push — не забываем git add . && git commit && git push

---

## 🧠 Используемые технологии

- **Python 3.11+** — основной язык разработки.
- **Flask** — веб-фреймворк для WebApp.
- **Supabase (PostgreSQL)** — облачная база данных вместо локальной SQLite.
- **OpenAI API (GPT-4o-mini)** — для анализа, аннотаций и AI-оценок.
- **Requests, Feedparser, BeautifulSoup** — для загрузки и парсинга RSS/HTML.
- **PyYAML** — конфигурации источников (`config/sources.yaml`).
- **Logging (RotatingFileHandler)** — единый сбор логов в консоль и файл.
- **Jinja2** (через Flask) — шаблонизатор для UI (страницы /digest, /events).
- **Custom CSS (static/style.css)** — собственные стили с адаптацией под светлую/тёмную тему и мобильные устройства.
- Возможность подключения **новых источников новостей** через `sources.yaml`.

---

## 🔑 Настройка окружения
-   Python + venv
-   Git + GitHub
-   Render для деплоя
-   Переменные окружения (.env, Render Secrets)

---

## 📌 Статус
-   План проекта
-   Структура файлов
-   Git-процесс
-   Настройка окружения
-   Первый парсер
-   AI-оценка новостей
-   Календарь событий
-   Веб-интерфейс

---

## 🧪 Тесты и отладка

Все тесты хранятся в папке `tests/`. Для запуска используется `pytest`.

### 🚀 Быстрый старт
- Только unit-тесты (CI-профиль):
  ```bash
  pytest -m "not integration"
  ```
- Unit + покрытие:
  ```bash
  pytest -m "not integration" --cov=./ --cov-report=term-missing --cov-fail-under=30
  ```
- Только интеграционные (нужен `.env`: `SUPABASE_URL`, `SUPABASE_KEY`, и т.п.):
  ```bash
  pytest -m integration
  ```
- Запуск одного тест-файла/теста:
  ```bash
  pytest tests/test_parsers.py -q
  pytest -k "fetch_rss_dedup" -q
  ```

### 🏷 Маркировка
- Интеграционные тесты помечаются `@pytest.mark.integration` и **не** запускаются в CI по умолчанию.

### 📌 Наличие тестов (на Day 2)
- `tests/test_ai_modules.py` — заглушки AI (credibility, importance).  
- `tests/test_clean_text.py` — тесты для `utils/clean_text` (удаление HTML-тегов, нормализация пробелов, извлечение текста из DOM-элементов). 
- `tests/test_digests.py` — генерация дайджестов/`ai_summary`.  
- `tests/test_main_import.py` — импорт/входная точка `main.py`.  
- `tests/test_parsers.py` — `rss_parser` и `events_parser`: нормализация дат, dedup, MIME-guard.  
- `tests/test_routes.py` — Flask Blueprints (`news_routes`).  
- `tests/test_webapp.py` — импорт приложения, Jinja-фильтры.  
- `tests/test_db_insert.py` — **integration**: `fetch_rss` → upsert → dedup в БД.  
- `tests/test_supabase.py` — **integration**: подключение к Supabase.
  

### 🔧 Pre-push (локально)
Перед пушем рекомендуется запускать:
```bash
flake8 .
black --check .
pytest -m "not integration" --cov=./ --cov-report=term-missing --cov-fail-under=30
```
(если настроен git hook — он будет делать это автоматически)
---

### SQL-скрипты (для локальной отладки)
- `database/init_tables.sql` — создаёт структуру таблиц.  
- `database/seed_data.sql` — наполняет тестовыми данными.  

> ⚠️ В реальном окружении используется Supabase (PostgreSQL). SQL-скрипты могут применяться только для локальных тестов.  

## 📌 Задачи на будущее

1. Расширить парсер новостей:
   - сохранять не только `title` и `link`, но и `summary`/`content`.
2. Добавить веб-интерфейс (админ-панель / webapp) для просмотра новостей и календаря.
3. Реализовать календарь событий с оценкой важности.
4. Подключить GitHub Actions (CI):
   - создать `.github/workflows/ci.yml`,
   - хранить `SUPABASE_URL` и `SUPABASE_KEY` в GitHub Secrets,
   - добавить бэйджик «CI passing» в `README.md`.


## Контекст задач
Кратко фиксируем «зачем» делаем задачу, чтобы не терялась логика.  
Пример: «Фильтр по темам нужен, чтобы формировать персональные дайджесты».

## 📌 История решений

- ✅ **Day 01 (24.09.2025)**
  • Добавлены `CONTRIBUTING.md`, `.editorconfig`, `pyproject.toml`.  
  • Настроен CI: flake8, black, pytest, coverage, isort, mypy.  
  • Исправлены тесты (`ai_modules`, `supabase`, `openai`, `digests`, `parsers`).  
  • Добавлены вспомогательные тесты (`test_main_import`, `test_routes`, `test_webapp`).  
  • Добавлены `tools/fetch_and_store_events.py` и `tools/show_latest_news.py`.  
  • `repo_map.py` исправлен, теперь корректно генерирует `CODEMAP.md`.  
  • Автоформатирование black/isort по всему проекту.  
  • CI проходит: оба бейджа (`main` и `day-01-docs-parsers`) — passing.  
  • Итог: Day 01 завершён.  

- ✅ **Day 02 (25.09.2025)**
  • Убран Axios (нет стабильного RSS) и временно исключён Reuters.  
  • Добавлены новые RSS (CoinDesk, Cointelegraph, Bloomberg Markets, TechCrunch и др.).  
  • Вынесена очистка текста в `utils/clean_text.py`.  
  • Реализован dedup (`uid = sha256(url|title)`, upsert по `uid`).  
  • Добавлен `tools/show_news.py` для просмотра новостей.  
  • `COUNTRY_MAP`, категории и теги вынесены в `config/constants.py`.  
  • Обновлены `README.md`, `docs/DEPLOY.md`, `docs/ARCHITECTURE.md` (Mermaid-схема).  
  • Итог: Day 02 завершён.  

- ✅ **Day 03 (26.09.2025)**
  • Добавлен Telegram-бот (aiogram 3.x): хэндлеры `/start`, `/digest`, `/digest_ai`, `/events`.
  • Главное меню и навигация через inline-кнопки (назад, категории).
  • Форматирование новостей и событий (emoji, Credibility, Importance, summary).
  • Реализован AI-дайджест по категориям за день.
  • В `db_models.py` добавлен fallback для `title`, улучшен `get_latest_events`.
  • Доработан `ai_summary.py`: исправлен prompt, убраны ошибки стиля.
  • В пайплайн добавлен парсер Investing (`tools/fetch_and_store_events.py`).
  • Обновлены `DEPLOY.md` (деплой бота) и `README.md` (раздел про Telegram).
  • Итог: Day 03 завершён.
  • В Telegram-бот добавлены **inline-клавиатуры**:
    • `start_inline_keyboard` — первая кнопка «🚀 Старт».
    • `main_inline_keyboard` — главное меню (📰 Новости, 🤖 AI-дайджест, 📅 События).
    • `back_inline_keyboard` — возврат в меню.
  • Архитектурное решение: бот полностью работает через inline-навигацию, без ReplyKeyboard.
  • Теперь бот встроен в пайплайн проекта (ручное тестирование команд, CI пока не прогоняет).

### Шаблон записи решения
**Дата:** YYYY-MM-DD  
**Что решили:**  
Краткое описание сути решения.  

**Альтернативы:**  
Какие другие варианты рассматривались.  

**Почему так:**  
Аргументы выбора.  

**Влияние:**  
Что изменилось в проекте.

## Правила общения
- Ты — архитектор проекта (ставишь задачи, утверждаешь решения).  
- Я — помощник (уточняю задачи, оформляю чек-листы, напоминаю про git).  
- Приоритеты задач: 🔴 срочно, 🟡 скоро, 🟢 можно отложить.  
- Цикл работы:  
  1. Задача → 2. Уточнение → 3. Чек-лист → 4. Git commit → 5. Итог в TASKS.md.

## Формат чек-листов
- Каждая задача оформляется как карточка:  
  - Заголовок  
  - Приоритет  
  - Контекст (зачем)  
  - Подзадачи (чек-лист)  
  - Критерии приёмки  
