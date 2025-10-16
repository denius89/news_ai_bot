# 🚀 .env Backup - Шпаргалка

**Quick Reference для PulseAI**

---

## ⚡ Основные команды (используйте каждый день)

```bash
# Сохранить .env перед изменениями
env-save "описание что меняете"

# Восстановить последний backup
env-restore

# Посмотреть все backup'ы
env-list

# Помощь
env-help
```

---

## 📋 Сценарии использования

### 1. Перед обновлением API ключа

```bash
env-save "before updating OpenAI key"
nano .env
# Меняете ключ...

# Если что-то не работает:
env-restore
```

### 2. Тестирование новой конфигурации

```bash
env-save "stable config before experiments"
nano .env
# AI_MODEL_SUMMARY=gpt-4o-mini → gpt-4o
./start_services.sh

# Если плохо работает:
env-restore
```

### 3. Быстрое редактирование с авто-backup

```bash
env-edit
# Автоматически создаст backup и откроет редактор
```

---

## 🔧 Продвинутые команды

```bash
# Сравнить текущий .env с backup'ом
env-diff

# Посмотреть содержимое backup'а
env-show stash@{0}

# Оставить только последние 5 backup'ов
env-cleanup 5

# Применить конкретный backup (не последний)
git stash apply stash@{2}
```

---

## ✅ Текущий статус

```bash
# У вас уже есть один backup:
env-list

# Вывод:
# stash@{0}: On main: 2025-10-16 22:47 - initial backup before active development
```

---

## 💡 Best Practices

1. **Всегда** создавайте backup перед изменением .env
2. **Используйте** описательные названия: `env-save "before switching to production keys"`
3. **Регулярно** чистите старые backup'ы: `env-cleanup 5`
4. **Проверяйте** что изменилось: `env-diff`

---

## 🆘 Если что-то пошло не так

```bash
# Восстановить последний backup
env-restore

# Если нужна более старая версия
env-list
git stash apply stash@{N}  # Где N - номер нужного backup'а
```

---

## 📖 Дополнительная информация

- **Полное руководство:** `.env-stash-guide.md`
- **Backup Guide:** `BACKUP_GUIDE.md`
- **Функции:** `.env-stash-functions.sh`

---

**Статус:** ✅ Готово к использованию  
**Создано:** 16 октября 2025


