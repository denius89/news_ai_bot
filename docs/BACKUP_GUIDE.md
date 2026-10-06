# 🗄️ Database Backup Guide

**Создано:** 27 октября 2025
**Статус:** Production Ready
**Автор:** PulseAI Team

---

## 📋 Содержание

- [Обзор](#обзор)
- [Быстрый старт](#быстрый-старт)
- [Создание backup](#создание-backup)
- [Восстановление из backup](#восстановление-из-backup)
- [Автоматизация](#автоматизация)
- [Troubleshooting](#troubleshooting)

---

## 🔍 Обзор

**Назначение:** Автоматическое резервное копирование базы данных PulseAI.

**Возможности:**
- ✅ Сжатие backup (gzip)
- ✅ Автоматическая очистка старых backup (30 дней)
- ✅ Логирование всех операций
- ✅ Восстановление за одну команду
- ✅ Поддержка Supabase PostgreSQL

**Файлы:**
- `scripts/backup_db.sh` — создание backup
- `scripts/restore_db.sh` — восстановление из backup
- `backups/` — директория для хранения backup

---

## 🚀 Быстрый Старт

### 1. Создать backup:

```bash
./scripts/backup_db.sh
```

**Результат:**
```
✅ Backup created: backups/pulseai_20251027_143022.sql.gz
Size: 2.5M
```

### 2. Восстановить из backup:

```bash
./scripts/restore_db.sh backups/pulseai_20251027_143022.sql.gz
```

---

## 💾 Создание Backup

### Ручной Backup

```bash
# Basic usage
./scripts/backup_db.sh

# Custom backup directory
./scripts/backup_db.sh /path/to/custom/backups
```

### Автоматический Backup (Cron)

Добавить в crontab для ежедневного backup в 3:00:

```bash
# Open crontab
crontab -e

# Add this line (adjust path):
0 3 * * * cd /home/user/news_ai_bot && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

**С сохранением логов:**
```bash
# Backup с логом
0 3 * * * cd /home/user/news_ai_bot && ./scripts/backup_db.sh >> logs/backup_$(date +\%Y\%m\%d).log 2>&1
```

### Backup Метрики

**Размер backup:** ~2-10 MB (сжатый)
**Время создания:** ~10-30 секунд
**Хранение:** Последние 30 дней
**Автоудаление:** Да (старые backup удаляются)

---

## 🔄 Восстановление из Backup

### Базовое Восстановление

```bash
./scripts/restore_db.sh backups/pulseai_20251027_143022.sql.gz
```

**⚠️ WARNING:** Это заменит ВСЕ данные в БД!
**Рекомендация:** Сделайте backup текущего состояния перед восстановлением.

### Процесс Восстановления

1. **Проверка файла:**
   - Проверяет существование backup файла
   - Проверяет формат (.sql.gz)

2. **Подтверждение:**
   - Запрашивает подтверждение (yes/no)
   - Показывает информацию о backup

3. **Восстановление:**
   - Извлекает SQL из .gz
   - Выполняет SQL команды в БД
   - Показывает прогресс

4. **Завершение:**
   - Проверяет успешность
   - Показывает результат

---

## ⚙️ Автоматизация

### Cron Job Setup

#### Вариант 1: Ежедневный backup в 3:00 AM

```bash
# Добавить в crontab
0 3 * * * cd /home/user/news_ai_bot && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

#### Вариант 2: Backup каждые 6 часов

```bash
0 */6 * * * cd /home/user/news_ai_bot && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

#### Вариант 3: Backup раз в час (для критичных данных)

```bash
0 * * * * cd /home/user/news_ai_bot && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

### Monitoring Backup

**Проверить последние backup:**
```bash
ls -lh backups/pulseai_*.sql.gz | tail -5
```

**Проверить cron job:**
```bash
crontab -l | grep backup_db
```

**Проверить логи:**
```bash
tail -f logs/backup.log
```

---

## 🔧 Troubleshooting

### Проблема: "Command not found: pg_dump"

**Решение:**
```bash
# Установить PostgreSQL client
# macOS:
brew install postgresql

# Ubuntu/Debian:
sudo apt-get install postgresql-client

# Проверить:
pg_dump --version
```

### Проблема: "SUPABASE_URL and SUPABASE_KEY must be set"

**Решение:**
```bash
# Проверить .env
cat .env | grep SUPABASE

# Если пусто, добавить в .env:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Проблема: "Connection refused"

**Решение:**
```bash
# Проверить доступность Supabase
ping db.supabase.co

# Проверить credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Проблема: "permission denied"

**Решение:**
```bash
# Дать права на выполнение
chmod +x scripts/backup_db.sh
chmod +x scripts/restore_db.sh
```

### Проблема: "Backup corrupted"

**Решение:**
```bash
# Проверить целостность backup
gunzip -t backups/pulseai_20251027_143022.sql.gz

# Если OK, backup не поврежден
# Если ERROR, backup поврежден - используйте другой backup
```

---

## 📊 Мониторинг Backup

### Список всех Backup

```bash
ls -lh backups/pulseai_*.sql.gz
```

**Пример вывода:**
```
-rw-r--r--  1 user  staff   2.5M Oct 27 14:30 pulseai_20251027_143022.sql.gz
-rw-r--r--  1 user  staff   2.5M Oct 26 14:30 pulseai_20251026_143022.sql.gz
-rw-r--r--  1 user  staff   2.5M Oct 25 14:30 pulseai_20251025_143022.sql.gz
```

### Проверка размера Backup

```bash
du -sh backups/
```

### Проверка даты последнего Backup

```bash
ls -lt backups/ | head -5
```

---

## 🛡️ Безопасность

### Хранение Backup

✅ **Рекомендуется:**
- Локальный сервер
- Шифрованный диск
- Отдельный сервер для backup
- S3 или другой облачный storage

❌ **Не рекомендуется:**
- Хранение на production сервере
- Незашифрованные backup
- Back업 без паролей

### Ротация Backup

**Текущая политика:**
- Хранить: Последние 30 дней
- Удалять: Старше 30 дней
- Размер: ~75 MB (30 дней × 2.5 MB)

**Для production:**
```bash
# Хранить 90 дней вместо 30
# Изменить в backup_db.sh:
KEEP_DAYS=90
```

---

## 📝 Best Practices

### 1. Регулярные Backup

- **Ежедневно** для production
- **Каждые 6 часов** для критичных данных
- **Перед миграциями** обязательно

### 2. Тестирование Restore

**Не реже раза в месяц:**
```bash
# Создать тестовую БД
createdb pulseai_test

# Восстановить backup в test БД
gunzip < backups/pulseai_20251027_143022.sql.gz | psql -d pulseai_test
```

### 3. Множественные Backup

**Хранить в разных местах:**
- Локальный сервер
- Облачное хранилище
- CD/DVD (для критичных данных)

### 4. Мониторинг

**Отслеживать:**
- Успешность backup
- Размер backup
- Дата последнего backup
- Ошибки в логах

---

## 🎯 Production Checklist

- [ ] Backup настроен (cron job)
- [ ] Тестирование restore выполнено
- [ ] Логи проверены
- [ ] Мониторинг настроен
- [ ] План восстановления документирован
- [ ] Team обучен процедурам

---

## 📞 Support

**Проблемы с backup?**
1. Проверить логи: `tail -f logs/backup.log`
2. Проверить credentials: `cat .env | grep SUPABASE`
3. Проверить права: `ls -l scripts/backup_db.sh`

**Восстановление не работает?**
1. Проверить формат backup: `file backups/pulseai_*.sql.gz`
2. Проверить подключение: `psql -h db.supabase.co -U postgres -d pulseai`
3. Попробовать старый backup

---

**Дата:** 27 октября 2025
**Версия:** 1.0
**Статус:** Production Ready
