# News AI Bot

## 🎯 Цель проекта
Создать умного бота для сбора и анализа новостей (крипта, экономика), с возможностью:
	- агрегировать источники
	- оценивать достоверность
	- переводить при необходимости
	- формировать дайджесты и календарь событий
	- предоставлять AI-аналитику (утро/вечер)

---

## 📂 Структура проекта

> ℹ️ Актуальная структура проекта автоматически поддерживается в `CODEMAP.md`.  
> Здесь зафиксирован снимок на 2025-09-18.
```
├── CODEMAP.md
├── MASTER_FILE.md
├── README.md
├── requirements.txt
├── TASKS.md
├── main.py
├── database/
│   └── db_models.py
├── parsers/
│   └── rss_parser.py
├── tools/
│   └── repo_map.py
├── tests/
│   ├── test_ai_modules.py
│   └── test_supabase.py
└── logs/
```

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
	-	Python 3.11+
	-	Flask (WebApp)
	-	SQLite (БД)
	-	OpenAI API (GPT-4o-mini)
	-	Requests, BeautifulSoup (парсинг)
	-	Возможность подключения новых источников новостей

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

Все тесты хранятся в папке tests/.
Каждый тест — отдельный файл, запускается командой:

```bash
python tests/<имя_файла>.py
```

### Текущие тесты
	- test_openai.py — проверка подключения к OpenAI API  
	- test_deepl.py — проверка перевода через DeepL API  
	- test_supabase.py — проверка подключения к базе данных Supabase
	- test_db_insert.py — проверка:
    	• загрузки новостей из RSS
    	• генерации AI-оценок (credibility, importance)
    	• сохранения всех полей в Supabase (включая published_at как ISO-строку)

Мы используем Supabase (PostgreSQL).

### Таблицы
	- **news** — новости (title, content, source, published_at)
	- **users** — пользователи (telegram_id, created_at)
	- **digests** — дайджесты для пользователей (summary, created_at)

### SQL-скрипты
	- `database/init_tables.sql` — создаёт структуру таблиц
	- `database/seed_data.sql` — наполняет тестовыми данными
---

## 📌 Задачи на будущее

1. Расширить парсер новостей:
   - сохранять не только `title` и `link`, но и `summary`/`content`.
2. Добавить веб-интерфейс (админ-панель / webapp) для просмотра новостей и календаря.
3. Реализовать календарь событий с оценкой важности.
4. Подключить GitHub Actions (CI):
   - создать `.github/workflows/ci.yml`,
   - хранить `SUPABASE_URL` и `SUPABASE_KEY` в GitHub Secrets,
   - добавить бэйджик «CI passing» в `README.md`.