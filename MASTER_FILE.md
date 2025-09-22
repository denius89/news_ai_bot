# 📰 News AI Bot — MASTER_FILE

Файл **MASTER_FILE.md** — свод правил, архитектуры и соглашений проекта.  
Это основной документ для разработчиков и участников проекта.

---

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
├── .gitignore
├── CODEMAP.md
├── config.py
├── main.py
├── MASTER_FILE.md
├── README.md
├── requirements.txt
├── TASKS.md
├── webapp.py
├── ai_modules/
│   ├── __init__.py
│   ├── credibility.py
│   └── importance.py
├── config/
│   └── sources.yaml
├── database/
│   ├── __init__.py
│   ├── db_models.py
│   ├── init_tables.sql
│   └── seed_data.sql
├── digests/
│   ├── __init__.py
│   ├── ai_summary.py
│   └── generator.py
├── logs/
├── parsers/
│   ├── __init__.py
│   └── rss_parser.py
├── routes/
│   ├── __init__.py
│   └── news_routes.py
├── static/
│   └── style.css
├── templates/
│   ├── digest.html
│   └── index.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ai_modules.py
│   ├── test_ai_summary.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_deepl.py
│   ├── test_digests.py
│   ├── test_main.py
│   ├── test_openai.py
│   └── test_supabase.py
└── tools/
    ├── fix_old_news.py
    ├── repo_map.py
    └── show_news.py
```

## 🗄️ База данных

Проект использует **Supabase (PostgreSQL)** вместо локальной SQLite.  

### Таблица `news` (основная)
| Поле          | Тип         | Описание |
|---------------|-------------|----------|
| id            | uuid (PK)   | Уникальный идентификатор (генерируется автоматически) |
| title         | text        | Заголовок новости |
| link          | text        | Ссылка на источник |
| published_at  | timestamptz | Дата и время публикации (в UTC) |
| content       | text        | Текст новости (если доступен) |
| credibility   | float       | Оценка достоверности (AI) |
| importance    | float       | Оценка важности (AI) |
| source        | text        | Название источника (например, `CoinDesk`, `BBC`) |
| category      | text        | Категория (например, `crypto`, `economy`, `world`, `technology`, `politics`) |

**Дополнительно:**
- **users** — пользователи (например, для будущей интеграции с Telegram-ботом).  
  Поля: `telegram_id`, `created_at`.  
- **digests** — дайджесты для пользователей (в перспективе).  
  Поля: `summary`, `created_at`.  

**Функция `upsert_news`:**
- Сохраняет новости по уникальному `link`.  
- Если новость с таким `link` уже есть, обновляет её содержимое.  
- Все даты нормализуются в **UTC**.  
- Если `content` отсутствует → поле может быть `NULL`.  
- При вставке дополнительно сохраняются оценки AI (`credibility`, `importance`), а также `source` и `category`.  

> ⚠️ Таблицы создаются через Supabase (PostgreSQL) или с помощью локальных SQL-скриптов (`database/init_tables.sql`, `seed_data.sql`).   

## 📜 Логирование

В проекте используется стандартный модуль Python `logging`.

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

### Где смотреть:
- **Консоль** — быстрый просмотр во время разработки.
- **logs/app.log** — полная история для отладки.

> ⚠️ Папка `logs/` добавлена в `.gitignore`, чтобы логи не попадали в репозиторий.  

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
1.	Goal — цель правки
2.	Action — что меняем
3.	Location — где (файл/модуль)
4.	Logic — зачем
5.	Output — что должно получиться
6.	Push — не забываем git add . && git commit && git push

---

## 🧠 Используемые технологии
- Python 3.11+
- Flask (WebApp, маршруты и шаблоны)
- Supabase (PostgreSQL) — основная база данных
- OpenAI API (GPT-4o-mini) — генерация саммари и оценка важности/достоверности
- Requests, Feedparser, BeautifulSoup — загрузка и парсинг RSS
- YAML — конфигурация источников (`config/sources.yaml`)
- Material Design стилизация для webapp (карточки, чипы, фильтры категорий)
- Логирование через `logging` (с ротацией файлов)
- Возможность подключения новых источников новостей через `sources.yaml`

---

## 🔑 Настройка окружения
-	Python + venv
-	Git + GitHub
-	Render для деплоя
-	Переменные окружения (.env, Render Secrets)

---

## 📌 Статус
-	План проекта
-	Структура файлов
-	Git-процесс
-	Настройка окружения
-	Первый парсер
-	AI-оценка новостей
-	Календарь событий
-	Веб-интерфейс

---

## 🧪 Тесты и отладка

Все тесты хранятся в папке `tests/`.  
Для запуска используется `pytest`.

### 📌 Текущие тесты
- `test_ai_modules.py` — проверка AI-заглушек (credibility, importance)  
- `test_db_content.py` — тестирование наличия/корректности контента новостей в базе  
- `test_db_insert.py` — проверка:
  - загрузки новостей из RSS  
  - генерации AI-оценок (credibility, importance)  
  - сохранения всех полей в Supabase (включая `published_at` как ISO-строку)  
- `test_deepl.py` — проверка перевода через DeepL API  
- `test_main.py` — базовые проверки работы `main.py`  
- `test_openai.py` — проверка подключения к OpenAI API  
- `test_supabase.py` — проверка подключения к базе Supabase  

### ▶️ Запуск тестов
Из корня проекта:

```bash
pytest
```
С подробным выводом:
```bash
pytest -v
```
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