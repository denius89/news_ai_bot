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

## Миграция soft delete для дайджестов

Если вам нужно добавить поддержку архивирования и мягкого удаления дайджестов:

### Через Supabase Dashboard

```sql
-- Add soft delete and archive columns to digests table
ALTER TABLE digests 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_digests_deleted ON digests(deleted_at);
CREATE INDEX IF NOT EXISTS idx_digests_archived ON digests(archived);
CREATE INDEX IF NOT EXISTS idx_digests_active ON digests(user_id, created_at DESC) 
WHERE deleted_at IS NULL AND archived = FALSE;

-- Add comments for documentation
COMMENT ON COLUMN digests.deleted_at IS 'Timestamp when digest was soft deleted (NULL = active)';
COMMENT ON COLUMN digests.archived IS 'Whether digest is archived (TRUE = archived, FALSE = active)';
```

### Проверка миграции

```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'digests' AND column_name IN ('deleted_at', 'archived')
ORDER BY ordinal_position;
```

Ожидаемый результат:
```
column_name | data_type            | column_default
------------|----------------------|----------------
deleted_at  | timestamp with tz    | NULL
archived    | boolean              | false
```

## После миграции

Запустите тесты, чтобы убедиться, что все работает:

```bash
make test
make run-tests-bot
```
