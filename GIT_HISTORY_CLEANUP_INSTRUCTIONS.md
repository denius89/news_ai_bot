# 🧹 ИНСТРУКЦИИ ПО ОЧИСТКЕ GIT ИСТОРИИ

**ВНИМАНИЕ:** Эта операция изменит публичную историю репозитория!

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

Файл `.env.backup` с секретами находится в коммите `93bfb623a13059c210fb59476be0f33bc81c75bd` и должен быть удален из всей истории Git.

---

## 🚀 ВАРИАНТ 1: BFG Repo-Cleaner (РЕКОМЕНДУЕТСЯ - БЫСТРЫЙ)

### Шаг 1: Установка BFG

```bash
# macOS (через Homebrew)
brew install bfg

# Или скачайте вручную:
# https://rtyley.github.io/bfg-repo-cleaner/
```

### Шаг 2: Создание резервной копии

```bash
cd /home/user
git clone --mirror news_ai_bot news_ai_bot-backup.git
```

### Шаг 3: Удаление файлов из истории

```bash
cd /home/user/news_ai_bot

# Удалить .env.backup из всей истории
bfg --delete-files .env.backup
bfg --delete-files .env.backup2
```

### Шаг 4: Очистка и сборка мусора

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Шаг 5: Проверка

```bash
# Убедитесь, что файлы удалены
git log --all --full-history --source -- .env.backup

# Не должно быть результатов!
```

### Шаг 6: Force Push

```bash
git push origin --force --all
git push origin --force --tags
```

---

## 🛠️ ВАРИАНТ 2: git filter-branch (МЕДЛЕННЫЙ, НО РАБОТАЕТ ВЕЗДЕ)

### Шаг 1: Создание резервной копии

```bash
cd /home/user/news_ai_bot
git branch backup-before-cleanup
```

### Шаг 2: Удаление файлов из истории

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.backup .env.backup2" \
  --prune-empty --tag-name-filter cat -- --all
```

Эта команда:
- Пройдет по всей истории
- Удалит `.env.backup` и `.env.backup2` из каждого коммита
- Удалит пустые коммиты
- Обновит теги

### Шаг 3: Очистка ссылок

```bash
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Шаг 4: Проверка

```bash
# Убедитесь, что файлы удалены
git log --all --full-history --source -- .env.backup

# Не должно быть результатов!
```

### Шаг 5: Force Push

```bash
git push origin --force --all
git push origin --force --tags
```

---

## ⚠️ ВАЖНЫЕ ПРЕДУПРЕЖДЕНИЯ

### Перед выполнением:

1. **Создайте резервную копию репозитория**
   ```bash
   cd /home/user
   cp -r news_ai_bot news_ai_bot-backup-$(date +%Y%m%d)
   ```

2. **Убедитесь, что все изменения закоммичены**
   ```bash
   cd /home/user/news_ai_bot
   git status
   # Должно быть чисто
   ```

3. **Если есть другие разработчики:**
   - Предупредите их ЗАРАНЕЕ
   - После force push они должны будут удалить свои локальные копии и сделать `git clone` заново

### После force push:

1. **GitHub может кэшировать старую историю** до 24 часов
2. **Любые форки репозитория** все еще будут содержать старую историю
3. **Если репозиторий публичный** - секреты могли быть проиндексированы поисковиками

---

## 🔍 ПРОВЕРКА ПОСЛЕ ОЧИСТКИ

```bash
cd /home/user/news_ai_bot

# 1. Проверка локальной истории
git log --all --full-history --source -- .env.backup
# Вывод: пусто ✅

# 2. Проверка упоминаний в коммитах
git log --all -S "sk-proj-" --oneline
# Вывод: пусто ✅

# 3. Проверка размера репозитория (должен уменьшиться)
git count-objects -vH

# 4. После push - проверка на GitHub
# Перейдите: https://github.com/repository-owner/news_ai_bot/commits/main
# Коммит 93bfb62 должен измениться или исчезнуть
```

---

## 🆘 ЧТО ДЕЛАТЬ, ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

### Восстановление из резервной копии:

```bash
cd /home/user
rm -rf news_ai_bot
cp -r news_ai_bot-backup-YYYYMMDD news_ai_bot
cd news_ai_bot
git remote set-url origin contact@example.invalid:repository-owner/news_ai_bot.git
```

### Если force push не работает:

```bash
# Проверьте защиту ветки на GitHub
# Settings → Branches → Branch protection rules

# Временно отключите защиту main ветки
# Выполните force push
# Верните защиту обратно
```

---

## 📝 ГОТОВЫЙ СКРИПТ (ВАРИАНТ 2 - БЕЗОПАСНЫЙ)

Сохраните в файл `cleanup_git_history.sh`:

```bash
#!/bin/bash
set -e

echo "🧹 Очистка Git истории от .env.backup"
echo ""

# Переход в директорию
cd /home/user/news_ai_bot

# Резервная копия
echo "📦 Создание резервной копии..."
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S)

# Удаление из истории
echo "🗑️  Удаление файлов из истории..."
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.backup .env.backup2" \
  --prune-empty --tag-name-filter cat -- --all

# Очистка
echo "🧽 Очистка ссылок..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Проверка
echo "🔍 Проверка..."
if git log --all --full-history --source -- .env.backup | grep -q "."; then
    echo "❌ ОШИБКА: Файлы все еще в истории!"
    exit 1
else
    echo "✅ Файлы успешно удалены из истории"
fi

echo ""
echo "📊 Статистика репозитория:"
git count-objects -vH

echo ""
echo "⚠️  СЛЕДУЮЩИЙ ШАГ:"
echo "git push origin --force --all"
echo "git push origin --force --tags"
echo ""
echo "ВНИМАНИЕ: Это изменит публичную историю!"
```

Использование:

```bash
chmod +x cleanup_git_history.sh
./cleanup_git_history.sh
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

- [ ] Все новые API ключи получены и обновлены в `.env`
- [ ] Создана резервная копия репозитория
- [ ] Выполнена очистка истории (BFG или filter-branch)
- [ ] Проверено, что `.env.backup` удален из истории
- [ ] Выполнен `git gc --prune=now --aggressive`
- [ ] Выполнен `git push --force`
- [ ] Проверено на GitHub, что старые коммиты изменились
- [ ] Проверено, что в истории нет упоминаний `sk-proj-`
- [ ] Все сервисы перезапущены с новыми ключами
- [ ] Проверена работоспособность бота

---

## 📞 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

- **BFG Repo-Cleaner:** https://rtyley.github.io/bfg-repo-cleaner/
- **Git filter-branch:** https://git-scm.com/docs/git-filter-branch
- **GitHub: Removing sensitive data:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

---

**Создано:** 16 октября 2025  
**Для репозитория:** repository-owner/news_ai_bot

