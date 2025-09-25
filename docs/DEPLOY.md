# 🚀 Деплой и запуск

## Локальный запуск
1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/denius89/news_ai_bot.git
   cd news_ai_bot
   ```

2. Создать виртуальное окружение и установить зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # для Linux/macOS
   venv\Scripts\activate      # для Windows

   pip install -r requirements.txt
   ```

3. Скопировать и заполнить переменные окружения:
   ```bash
   cp .env.example .env
   ```
   В `.env` нужно указать:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `DEEPL_API_KEY`

4. Запустить webapp:
   ```bash
   python webapp.py
   ```
   или CLI:
   ```bash
   python main.py --source all --limit 10
   ```

---

## Деплой на Render (пример)
1. Создать новый **Web Service** на [Render](https://render.com).
2. Указать репозиторий GitHub (`news_ai_bot`).
3. В `Environment` добавить переменные:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `DEEPL_API_KEY`
4. Build command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start command:
   ```bash
   gunicorn webapp:app
   ```

---

## Запуск фоновых задач (ETL)
Для периодического парсинга новостей и событий можно использовать **CRON** или **Render Jobs**.

Пример (Linux CRON, каждые 30 минут):
```bash
*/30 * * * * cd /path/to/news_ai_bot && venv/bin/python tools/fetch_and_store_news.py
```

---

## Supabase setup
1. Создать проект в [Supabase](https://supabase.com).
2. В разделе **SQL editor** выполнить:
   ```sql
   -- Создание таблицы новостей
   create table if not exists news (
       uid text primary key,
       title text,
       content text,
       link text,
       published_at timestamptz,
       source text,
       category text,
       credibility numeric,
       importance numeric
   );

   -- Создание таблицы событий
   create table if not exists events (
       event_id text primary key,
       event_time timestamptz,
       country text,
       currency text,
       title text,
       importance int,
       fact text,
       forecast text,
       previous text,
       source text,
       country_code text,
       created_at timestamptz
   );
   ```
3. Скопировать `SUPABASE_URL` и `SUPABASE_KEY` в `.env`.

---

✅ Теперь у тебя есть рабочая инструкция для локального запуска и деплоя.
