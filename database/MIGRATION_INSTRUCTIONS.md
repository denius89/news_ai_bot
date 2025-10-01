# Database Migration Instructions

## Проблема
Таблица `users` существует, но не хватает колонок:
- `username` (TEXT)
- `locale` (TEXT, DEFAULT 'ru') 
- `updated_at` (TIMESTAMPTZ, DEFAULT now())

## Решение

### Вариант 1: Через Supabase Dashboard (Рекомендуется)

1. Откройте [Supabase Dashboard](https://app.supabase.com)
2. Перейдите в ваш проект
3. Откройте **SQL Editor**
4. Выполните следующий SQL:

```sql
-- Add username column
ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;

-- Add locale column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS locale TEXT DEFAULT 'ru';

-- Add updated_at column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Update existing rows to set updated_at
UPDATE users SET updated_at = now() WHERE updated_at IS NULL;
```

### Вариант 2: Через psql (если у вас есть доступ к базе)

```bash
psql "postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"

# Затем выполните SQL из файла:
\i database/migrations/2025_10_02_add_missing_columns.sql
```

### Проверка

После применения миграции проверьте, что колонки добавлены:

```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
```

Ожидаемый результат:
```
column_name | data_type    | column_default
------------|--------------|---------------
id          | uuid         | gen_random_uuid()
telegram_id | bigint       | 
username    | text         | 
locale      | text         | 'ru'::text
created_at  | timestamptz  | now()
updated_at  | timestamptz  | now()
```

## После миграции

Запустите тесты, чтобы убедиться, что все работает:

```bash
make test
make run-tests-bot
```
