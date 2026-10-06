# 🚨 ОТЧЕТ О ИНЦИДЕНТЕ БЕЗОПАСНОСТИ

**Дата инцидента:** 16 октября 2025  
**Дата обнаружения:** 16 октября 2025  
**Статус:** КРИТИЧЕСКИЙ - Требуются немедленные действия

---

## 📋 Краткое описание

Обнаружена утечка API ключей в публичный репозиторий GitHub через файл `.env.backup`, который был закоммичен в коммите `93bfb623a13059c210fb59476be0f33bc81c75bd` от 16 октября 2025.

**OpenAI уже отключил скомпрометированный ключ** и отправил уведомление.

---

## 🔑 Скомпрометированные ключи

### ✅ Уже отключены:
1. **OPENAI_API_KEY** - `sk-proj-dgV9...JAA` ✅ Отключен OpenAI

### ❌ Требуют немедленной ротации:

2. **TELEGRAM_BOT_TOKEN** - `0:AAHp8o_***masked***`
3. **GITHUB_TOKEN** - `ghp_***masked***`
4. **SUPABASE_KEY** - полный ключ виден в истории
5. **SUPABASE_URL** - `https://***masked***.supabase.co`
6. **COINMARKETCAL_API_KEY** - `***masked***`
7. **COINDAR_API_KEY** - `***masked***`
8. **EODHD_TOKEN** - `***masked***`
9. **FMP_TOKEN** - `***masked***`
10. **FINNHUB_TOKEN** - `***masked***`
11. **FOOTBALL_DATA_TOKEN** - `***masked***`

---

## 🎯 НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ (КРИТИЧНО!)

### 1. OpenAI API Key ✅ ВЫПОЛНЕНО
- [x] OpenAI автоматически отключил ключ
- [ ] **Создать новый ключ:** https://platform.openai.com/api-keys
- [ ] Обновить в `.env` файле

### 2. Telegram Bot Token ❌ КРИТИЧНО
**Почему критично:** Доступ к вашему боту, возможность читать/отправлять сообщения от его имени

**Действия:**
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/revoke` или `/token`
3. Выберите вашего бота
4. Получите новый токен
5. Обновите в `.env`: `TELEGRAM_BOT_TOKEN=новый_токен`
6. Перезапустите бота

### 3. GitHub Token ❌ КРИТИЧНО
**Почему критично:** Доступ к вашим приватным репозиториям, возможность делать коммиты от вашего имени

**Действия:**
1. Перейдите: https://github.com/settings/tokens
2. Найдите токен `ghp_5g8t0...3GrTPP`
3. Нажмите **Delete** / **Revoke**
4. Создайте новый токен с минимальными правами (только `public_repo` или `repo` если нужны приватные)
5. Обновите в `.env`: `GITHUB_TOKEN=новый_токен`

### 4. Supabase ❌ КРИТИЧНО
**Почему критично:** Полный доступ к вашей базе данных

**Действия:**
1. Перейдите в Supabase Dashboard: https://supabase.com/dashboard/project/nzgzolramikbxpdsnzdv/settings/api
2. Раздел **Project API keys**
3. Нажмите **Reset** на `anon` public key
4. Скопируйте новый ключ
5. Обновите в `.env`: `SUPABASE_KEY=новый_ключ`
6. **Опционально:** Создайте новый проект и мигрируйте данные для полной безопасности

### 5. Остальные API ключи

#### CoinMarketCal
- Dashboard: https://coinmarketcal.com/en/account/api
- Отозвать старый ключ и создать новый

#### Coindar
- Dashboard: https://coindar.org/en/account/api
- Создать новый API ключ

#### EODHD
- Dashboard: https://eodhd.com/cp/settings
- Сбросить API токен

#### Financial Modeling Prep
- Dashboard: https://site.financialmodelingprep.com/developer
- Получить новый API ключ

#### Finnhub
- Dashboard: https://finnhub.io/dashboard
- Сбросить API ключ

#### Football Data
- Dashboard: https://www.football-data.org/client/profile
- Создать новый токен

---

## 🛠️ ТЕХНИЧЕСКАЯ ОЧИСТКА

### 1. Локальная очистка ✅ ВЫПОЛНЕНО
- [x] Удалены файлы `.env.backup` и `.env.backup2`
- [x] Обновлен `.gitignore` для защиты от будущих утечек
- [x] Создан `.env.example` как шаблон

### 2. Очистка Git истории ⚠️ ТРЕБУЕТСЯ ВЫПОЛНИТЬ

**Вариант A: BFG Repo-Cleaner (РЕКОМЕНДУЕТСЯ)**

```bash
# 1. Установите BFG (macOS)
brew install bfg

# 2. Создайте резервную копию
cd /home/user/news_ai_bot
git clone --mirror . ../news_ai_bot-backup.git

# 3. Удалите файл из истории
bfg --delete-files .env.backup

# 4. Очистите рефлоги и сборку мусора
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (ВНИМАНИЕ: это изменит историю!)
git push origin --force --all
git push origin --force --tags
```

**Вариант B: git filter-branch (если нет BFG)**

```bash
cd /home/user/news_ai_bot

# Удалите .env.backup из всей истории
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.backup .env.backup2" \
  --prune-empty --tag-name-filter cat -- --all

# Очистка
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
git push origin --force --tags
```

**⚠️ ВНИМАНИЕ:** 
- Force push изменит публичную историю репозитория
- Если есть другие разработчики, они должны сделать `git clone` заново
- Сделайте резервную копию перед выполнением!

---

## 🔒 ПРЕВЕНТИВНЫЕ МЕРЫ НА БУДУЩЕЕ

### 1. Pre-commit хук для предотвращения утечек

Создайте файл `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Проверка на случайный коммит секретов

if git diff --cached --name-only | grep -E "\.env$|\.env\..*"; then
    echo "❌ ОШИБКА: Попытка закоммитить .env файл!"
    echo "Используйте .env.example для шаблонов"
    exit 1
fi

# Проверка на потенциальные секреты в коде
if git diff --cached | grep -E "(sk-proj-|sk-pro-|ghp_|eyJhbGciOi)"; then
    echo "❌ ОШИБКА: Обнаружены потенциальные API ключи в коммите!"
    exit 1
fi

exit 0
```

Сделайте исполняемым:
```bash
chmod +x .git/hooks/pre-commit
```

### 2. Используйте git-secrets

```bash
# Установка (macOS)
brew install git-secrets

# Настройка в репозитории
cd /home/user/news_ai_bot
git secrets --install
git secrets --register-aws
git secrets --add 'sk-proj-[a-zA-Z0-9_-]+'
git secrets --add 'ghp_[a-zA-Z0-9]+'
git secrets --add '[0-9]{10}:AA[a-zA-Z0-9_-]+'  # Telegram bot tokens
```

### 3. Используйте .env только локально

**Правила работы с .env:**
- ✅ `.env` всегда в `.gitignore`
- ✅ Используйте `.env.example` для документации
- ✅ Для продакшена используйте системные переменные окружения или секреты-менеджеры
- ❌ НИКОГДА не создавайте `.env.backup`, `.env.local`, `.env.production` если не уверены что они в `.gitignore`

### 4. Мониторинг GitHub

Включите GitHub Secret Scanning:
- Перейдите в Settings → Security → Secret scanning
- Включите все опции

---

## 📊 ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЯ

### Чеклист безопасности:

- [ ] Все 11 API ключей обновлены
- [ ] `.env` файл содержит только новые ключи
- [ ] `.env.backup` удален из git истории
- [ ] Force push выполнен успешно
- [ ] Pre-commit хук установлен
- [ ] `.env.example` обновлен и закоммичен
- [ ] `.gitignore` содержит все паттерны `.env*`
- [ ] Все сервисы перезапущены с новыми ключами
- [ ] Telegram бот работает с новым токеном
- [ ] OpenAI API работает с новым ключом
- [ ] Supabase подключение работает

---

## 🔍 ПРОВЕРКА АКТИВНОСТИ НА СКОМПРОМЕТИРОВАННЫХ КЛЮЧАХ

### OpenAI
1. Перейдите: https://platform.openai.com/usage
2. Проверьте активность за последние дни
3. Ищите подозрительные запросы

### Supabase
1. Dashboard → Logs → API
2. Проверьте подозрительную активность
3. Проверьте изменения в базе данных

### GitHub
1. Settings → Security → Audit log
2. Ищите неавторизованную активность

### Telegram
1. Проверьте логи бота
2. Проверьте, не было ли отправлено сообщений без вашего ведома

---

## 📝 TIMELINE ИНЦИДЕНТА

- **03.10.2025 09:37** - Коммит `.env` в git (первое появление)
- **16.10.2025 21:18** - Коммит `.env.backup` в публичный репозиторий
- **16.10.2025** - OpenAI обнаружил утечку и отключил ключ
- **16.10.2025** - Получено уведомление от OpenAI
- **16.10.2025** - Начата очистка (текущий момент)

---

## 🎓 УРОКИ НА БУДУЩЕЕ

1. **Автоматизация:** Используйте pre-commit хуки
2. **Культура безопасности:** Никогда не создавайте `.env.backup` файлы
3. **Мониторинг:** Включите GitHub Secret Scanning
4. **Ротация ключей:** Регулярно обновляйте API ключи
5. **Принцип минимальных привилегий:** Создавайте токены с минимальными правами

---

## 📞 КОНТАКТЫ ПОДДЕРЖКИ

- **OpenAI Support:** https://help.openai.com/
- **GitHub Security:** https://github.com/security
- **Supabase Support:** https://supabase.com/support

---

**Статус:** 🔴 ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ДЕЙСТВИЕ  
**Приоритет:** КРИТИЧЕСКИЙ  
**Ответственный:** Denys maintainer (contact@example.invalid)

---

## ✅ ПРОГРЕСС ВЫПОЛНЕНИЯ

- [x] Обнаружение проблемы
- [x] Локальная очистка файлов
- [x] Обновление .gitignore
- [x] Создание .env.example
- [ ] **Ротация всех API ключей** ⬅️ СЛЕДУЮЩИЙ ШАГ
- [ ] Очистка Git истории
- [ ] Force push
- [ ] Установка pre-commit хуков
- [ ] Финальная проверка

---

**Создано:** 16 октября 2025  
**Обновлено:** 16 октября 2025  
**Версия:** 1.0

