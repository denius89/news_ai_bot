-- Новости
create table if not exists news (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text,
  source text,
  published_at timestamp with time zone default now()
);

-- Пользователи
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  telegram_id text unique,
  created_at timestamp with time zone default now()
);

-- Дайджесты
create table if not exists digests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  created_at timestamp with time zone default now(),
  summary text
);
