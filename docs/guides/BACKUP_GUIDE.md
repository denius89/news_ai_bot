# 🔐 Руководство по безопасному backup .env файлов

**Проект:** PulseAI  
**Дата:** 16 октября 2025

---

## 🎯 Рекомендованный подход для PulseAI

### **Используйте комбинацию методов:**

| Сценарий | Метод | Когда использовать |
|----------|-------|-------------------|
| 🔧 Быстрый backup при разработке | **Git Stash** | Перед экспериментами с .env |
| 🏢 Продакшен секреты | **1Password/Bitwarden** | Для долгосрочного хранения |
| 👥 Локальные backup'ы | **tools/backup_env.sh** | Регулярные snapshot'ы |

---

## 1️⃣ Git Stash (для разработки) ⭐ РЕКОМЕНДУЕТСЯ

### Использование:

```bash
# Перед изменением .env
git stash push .env -m "backup before updating OpenAI key"

# Редактируйте .env
nano .env

# Если нужно вернуть старую версию
git stash pop

# Посмотреть все stash'и
git stash list

# Восстановить конкретный stash (без удаления из списка)
git stash apply stash@{0}

# Удалить stash после восстановления
git stash drop stash@{0}
```

### Плюсы:
✅ Встроено в Git - не нужны дополнительные инструменты  
✅ Быстро и просто  
✅ Не попадает в .git/objects (не увеличивает размер репозитория)  
✅ Идеально для временных изменений

### Когда использовать:
- Перед экспериментами с новыми API ключами
- Перед обновлением конфигурации
- Когда хотите попробовать разные настройки

---

## 2️⃣ Менеджеры паролей (для продакшена) ⭐⭐⭐ ЛУЧШИЙ ВАРИАНТ

### Вариант A: 1Password (платный, $3-5/мес)

```bash
# Установка
brew install --cask 1password
brew install --cask 1password-cli

# Логин
eval $(op signin)

# Создание записи для PulseAI
op item create \
  --category=login \
  --title="PulseAI Production" \
  --vault="Development" \
  "OPENAI_API_KEY[password]=sk-proj-..." \
  "TELEGRAM_BOT_TOKEN[password]=8062922612:..." \
  "SUPABASE_KEY[password]=eyJhbGci..." \
  "SUPABASE_URL[text]=https://example.supabase.co"

# Получение ключа
op item get "PulseAI Production" --field OPENAI_API_KEY

# Автоматическое заполнение .env
op inject -i .env.template -o .env
```

**Template (.env.template):**
```bash
OPENAI_API_KEY=op://Development/PulseAI Production/OPENAI_API_KEY
TELEGRAM_BOT_TOKEN=op://Development/PulseAI Production/TELEGRAM_BOT_TOKEN
SUPABASE_KEY=op://Development/PulseAI Production/SUPABASE_KEY
```

### Вариант B: Bitwarden (бесплатный open-source)

```bash
# Установка
brew install bitwarden-cli

# Логин
bw login contact@example.invalid

# Разблокировка (нужно при каждом запуске)
export BW_SESSION=$(bw unlock --raw)

# Создание записи
bw create item '{
  "organizationId": null,
  "folderId": null,
  "type": 2,
  "name": "PulseAI Production",
  "notes": "Production environment variables for PulseAI bot",
  "secureNote": {
    "type": 0
  },
  "fields": [
    {"name": "OPENAI_API_KEY", "value": "sk-proj-...", "type": 1},
    {"name": "TELEGRAM_BOT_TOKEN", "value": "8062922612:...", "type": 1},
    {"name": "SUPABASE_KEY", "value": "eyJhbGci...", "type": 1},
    {"name": "SUPABASE_URL", "value": "https://...", "type": 0}
  ]
}'

# Получение ключа
bw get item "PulseAI Production" | jq -r '.fields[] | select(.name=="OPENAI_API_KEY") | .value'

# Генерация .env из Bitwarden
bw get item "PulseAI Production" | jq -r '.fields[] | "\(.name)=\(.value)"' > .env
```

### Плюсы менеджеров паролей:
✅ Максимальная безопасность (AES-256 шифрование)  
✅ Синхронизация между устройствами  
✅ История изменений ключей  
✅ Безопасный шаринг с командой  
✅ 2FA защита  
✅ Audit trail (кто и когда получал доступ)  
✅ Автоматическая ротация паролей

### Когда использовать:
- ✅ Production секреты
- ✅ Долгосрочное хранение
- ✅ Работа в команде
- ✅ Когда нужна синхронизация между машинами

---

## 3️⃣ Локальный backup скрипт (для snapshot'ов) ⭐⭐

### Использование:

```bash
# Создание backup
./tools/backup_env.sh

# Вывод:
# ✅ Backup создан: /home/user/.pulseai-secrets/news_ai_bot/.env.20251016_224530
# 
# 📋 Последние backup'ы:
# -rw------- 1 project-user staff 2065 Oct 16 22:45 .env.20251016_224530
# -rw------- 1 project-user staff 2062 Oct 16 22:30 .env.20251016_223000

# Восстановление
cp ~/.pulseai-secrets/news_ai_bot/.env.20251016_224530 .env

# Просмотр всех backup'ов
ls -lht ~/.pulseai-secrets/news_ai_bot/

# Сравнение с текущим .env
diff .env ~/.pulseai-secrets/news_ai_bot/.env.20251016_224530
```

### Автоматический backup перед важными операциями:

Добавьте алиас в `~/.bashrc` или `~/.zshrc`:

```bash
# Alias для автоматического backup перед редактированием
alias edit-env='cd /home/user/news_ai_bot && ./tools/backup_env.sh && nano .env'

# Использование
edit-env  # Создаст backup и откроет редактор
```

### Плюсы:
✅ Полностью локально (нет зависимости от сервисов)  
✅ Бесплатно  
✅ Автоматическая ротация (хранит 10 последних)  
✅ Защищенные права доступа (chmod 600)

### Когда использовать:
- Перед важными изменениями .env
- Регулярные snapshot'ы (еженедельно/ежемесячно)
- Когда нужен быстрый откат

---

## 📊 Сравнительная таблица

| Критерий | Git Stash | 1Password | Bitwarden | Локальный скрипт |
|----------|-----------|-----------|-----------|------------------|
| **Безопасность** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Простота** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Стоимость** | Бесплатно | $3-5/мес | Бесплатно | Бесплатно |
| **Синхронизация** | ❌ | ✅ | ✅ | ❌ |
| **Шаринг** | ❌ | ✅ | ✅ | ⚠️ |
| **История** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Для команды** | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 Рекомендации для PulseAI

### Для сольного разработчика:

**Комбинация:**
1. **Git Stash** - для ежедневной работы
2. **Локальный скрипт** - для snapshot'ов раз в неделю
3. **Bitwarden (бесплатный)** - для продакшен ключей

**Стоимость:** $0/мес  
**Время настройки:** 10 минут

---

### Для команды (2+ человека):

**Комбинация:**
1. **Git Stash** - для ежедневной работы
2. **1Password Teams** - для всех продакшен секретов
3. **Локальный скрипт** - для личных backup'ов

**Стоимость:** $20/мес на команду  
**Время настройки:** 30 минут

---

## ⚡ Quick Start: Минимальная настройка (5 минут)

```bash
# 1. Добавьте алиас для быстрого backup
echo 'alias backup-env="cd /home/user/news_ai_bot && ./tools/backup_env.sh"' >> ~/.zshrc
source ~/.zshrc

# 2. Создайте первый backup
cd /home/user/news_ai_bot
./tools/backup_env.sh

# 3. Используйте Git Stash для ежедневной работы
git stash push .env -m "backup before changes"

# Готово! ✅
```

---

## 🚫 Что НЕ делать (НИКОГДА!)

❌ **НЕ создавайте backup в корне проекта:**
```bash
cp .env .env.backup      # ОПАСНО!
cp .env .env.old         # ОПАСНО!
cp .env .env.20251016    # ОПАСНО!
```

❌ **НЕ коммитьте backup файлы:**
```bash
git add .env.backup      # ОПАСНО!
```

❌ **НЕ храните backup на Google Drive / Dropbox без шифрования:**
```bash
cp .env ~/Google\ Drive/.env.backup  # ОПАСНО!
```

❌ **НЕ отправляйте .env по email / Slack:**
```bash
# ОПАСНО! Telegram, Email, Slack логируют всё
```

---

## ✅ Итоговая рекомендация для PulseAI

### **Лучший вариант для вас:**

```bash
# 1. Установите Bitwarden (бесплатно)
brew install bitwarden-cli

# 2. Сохраните продакшен ключи в Bitwarden
bw login
# ... сохраните все ключи ...

# 3. Используйте Git Stash для ежедневной работы
git stash push .env -m "backup before experiment"

# 4. Используйте локальный скрипт для регулярных snapshot'ов
./tools/backup_env.sh  # раз в неделю
```

**Почему:**
- ✅ Бесплатно
- ✅ Безопасно (шифрование AES-256)
- ✅ Простота использования
- ✅ Синхронизация между устройствами
- ✅ Можно расшарить с командой при необходимости

---

**Статус:** ✅ Готово к использованию  
**Создано:** 16 октября 2025  
**Автор:** Security Team


