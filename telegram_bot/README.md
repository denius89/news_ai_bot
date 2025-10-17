# PulseAI Telegram Bot

Telegram бот для персональных AI-дайджестов новостей и событий.

## 📋 Структура бота

```
telegram_bot/
├── bot.py                    # Главный файл бота (aiogram v3)
├── keyboards.py              # Все inline клавиатуры
├── handlers/                 # Обработчики команд и callback'ов
│   ├── start.py              # Приветствие, главное меню, справка
│   ├── digest_ai.py          # AI-дайджесты с выбором стиля
│   ├── events.py             # Календарь событий
│   ├── dashboard.py          # WebApp Dashboard
│   ├── notifications.py      # Система уведомлений
│   └── subscriptions.py      # Управление подписками
├── services/                 # Сервисы бота
└── utils/                    # Утилиты форматирования
```

## 🎯 Основные возможности

### 1. **Приветствие и навигация** (`handlers/start.py`)

**Команды:**
- `/start` — приветствие и главное меню

**Callback кнопки:**
- `start` — показать главное меню
- `back` — возврат в главное меню
- `settings` — открыть настройки
- `help` — показать справку

**Приветствие включает:**
- Описание 255 источников новостей
- 4 стиля AI-дайджестов
- Умный календарь с 20+ провайдерами
- WebApp Dashboard с полным функционалом

---

### 2. **AI-дайджесты** (`handlers/digest_ai.py`)

**Команды:**
- `/digest_ai` — создать персональный дайджест

**Процесс создания:**
1. **Выбор категории** — 70 категорий или "Все"
2. **Выбор периода** — сегодня, неделя, месяц
3. **Выбор стиля** — 4 профессиональных стиля:
   - 📰 **Newsroom** — Reuters/Bloomberg стиль
   - 🔍 **Analytical** — глубокий анализ
   - 📖 **Magazine** — storytelling подача
   - 💬 **Casual** — разговорный стиль

**Особенности:**
- ML-фильтрация по важности ≥ 0.6
- Проверка достоверности ≥ 0.7
- Персонализация под подписки
- Анимированная генерация
- Система обратной связи 👍/👎

---

### 3. **События** (`handlers/events.py`)

**Команды:**
- `/events` — календарь ближайших событий

**Callback:**
- `events` — показать события

**Источники событий:**
- 🪙 **Crypto** — листинги, хардфорки, релизы
- 🏈 **Sports** — матчи, турниры, финалы
- 📈 **Markets** — отчеты, IPO, дивиденды
- 💻 **Tech** — конференции, релизы, апдейты
- 🌍 **World** — саммиты, выборы, праздники

**Фильтры:**
- По важности (≥ 0.5 по умолчанию)
- Период: 30 дней вперед
- AI-оценка релевантности

---

### 4. **WebApp Dashboard** (`handlers/dashboard.py`)

**Команды:**
- `/dashboard` — открыть веб-интерфейс

**Callback:**
- `dashboard` — показать описание и кнопку запуска

**Возможности Dashboard:**
- 📑 Управление 70 категориями подписок
- 🔔 Настройка уведомлений (время, частота)
- 📅 Интерактивный календарь событий
- 📊 Статистика и метрики качества
- 💾 История дайджестов

---

### 5. **Уведомления** (`handlers/notifications.py`)

**Команды:**
- `/notifications` — управление уведомлениями

**Типы уведомлений:**

1. **📰 Дайджесты**
   - Ежедневные AI-дайджесты
   - Персонализация по категориям
   - Выбор времени доставки

2. **📅 События**
   - Уведомления о важных событиях
   - Напоминания перед началом
   - Фильтры по категориям

3. **⚡ Срочные новости**
   - Breaking news алерты
   - Мгновенные уведомления
   - Только критичные события

**Callback кнопки:**
- `notifications` — показать меню уведомлений
- `my_notifications` — список активных уведомлений
- `notify_on_digest` — включить уведомления о дайджестах
- `notify_off_digest` — выключить уведомления о дайджестах
- `mark_read:<id>` — отметить уведомление прочитанным

---

### 6. **Подписки** (`handlers/subscriptions.py`)

**Команды:**
- `/subscribe <категория>` — подписаться на категорию
- `/unsubscribe <категория>` — отписаться
- `/my_subs` — показать активные подписки
- `/categories` — список всех категорий
- `/help_subs` — справка по подпискам

#### 2-уровневая система категорий

PulseAI использует иерархическую структуру:

**📁 Категории → Подкатегории**

**Примеры:**
```
🪙 Crypto
   ├── DeFi (Decentralized Finance)
   ├── NFT (Non-Fungible Tokens)
   ├── Bitcoin
   ├── Ethereum
   └── Altcoins

💻 Tech
   ├── AI/ML (Artificial Intelligence)
   ├── Startups
   ├── Gadgets
   ├── Software
   └── Hardware

📈 Finance
   ├── Stocks
   ├── Forex
   ├── Banking
   └── Investments

🌍 World
   ├── Politics
   ├── Economics
   ├── Science
   └── Environment
```

**Преимущества:**
- 🎯 Точная настройка интересов
- 📊 Гибкая фильтрация новостей
- 🔔 Персонализированные уведомления
- 📰 Релевантные AI-дайджесты

**Как использовать:**
1. Выберите "📋 Подписки" → "➕ Подписаться"
2. Выберите категорию (например, Crypto)
3. Выберите подкатегорию (например, DeFi)
4. Получайте новости только по этой теме!

**Callback кнопки:**
- `subscriptions` — меню подписок с описанием структуры
- `my_subs` — показать активные подписки
- `subscribe_menu` — выбор категории для подписки (с примерами)
- `unsubscribe_menu` — выбор категории для отписки
- `subscribe:<category>` — подписаться на категорию
- `subscribe:<category>:<subcategory>` — подписаться на подкатегорию
- `unsubscribe:<category>` — отписаться от категории
- `unsubscribe:<category>:<subcategory>` — отписаться от подкатегории

---

## 🎨 Клавиатуры (`keyboards.py`)

### Главное меню (`main_inline_keyboard`)
```
📰 Новости
🤖 AI-дайджест
📅 События
🌐 WebApp
⚙️ Настройки
```

### Меню настроек (`settings_inline_keyboard`)
```
📋 Подписки
🔔 Уведомления
⬅️ Назад
```

### Меню подписок (`subscriptions_inline_keyboard`)
```
📋 Мои подписки
➕ Подписаться
➖ Отписаться
⬅️ Назад
```

### Меню уведомлений (`notifications_inline_keyboard`)
```
🔔 Мои уведомления
✅ Включить дайджест
❌ Выключить дайджест
⬅️ Назад
```

### Динамические клавиатуры

#### Категории (`categories_inline_keyboard`)

Умная клавиатура с 2-уровневой иерархией:

```python
def categories_inline_keyboard(action: str = "subscribe") -> types.InlineKeyboardMarkup:
    """Динамическая клавиатура категорий для подписок"""
```

**Особенности:**
- 📁 Динамически генерируется из `services/categories.py`
- 🎨 Уникальные иконки для каждой категории
- 🔗 Поддержка подкатегорий через `subcategories_inline_keyboard`
- ⚡ Кэширование для быстрой загрузки

**Источник данных:** `config/data/sources.yaml`

**Структура:**
```yaml
crypto:
  subcategories:
    - defi
    - nft
    - bitcoin
  sources:
    - url: ...
      subcategory: defi
```

#### Подкатегории (`subcategories_inline_keyboard`)

```python
def subcategories_inline_keyboard(category: str, action: str = "subscribe") -> types.InlineKeyboardMarkup:
    """Динамическая клавиатура подкатегорий для выбранной категории"""
```

**Workflow:**
1. Пользователь выбирает категорию (например, "Crypto")
2. Показывается клавиатура подкатегорий (DeFi, NFT, Bitcoin...)
3. После выбора выполняется действие (подписка/отписка)

#### Дайджесты (`digest_categories_inline_keyboard`)
- Кнопка "📚 Все категории"
- Список всех 70 категорий с иконками
- Используется для выбора темы AI-дайджеста

---

## 🔧 Технические детали

### Библиотеки
- **aiogram v3** — фреймворк для Telegram Bot API
- **asyncio** — асинхронное выполнение
- **Supabase** — база данных

### Архитектура
```
User → Telegram API → aiogram → Handlers → Services → Database
                                      ↓
                                AI Modules
```

### Логирование
- Все действия логируются
- Уровни: INFO, WARNING, ERROR
- Формат: JSON structured logging

### Обработка ошибок
```python
try:
    # Основная логика
    result = await some_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    await query.answer("❌ Ошибка", show_alert=True)
```

---

## 📊 Метрики и аналитика

### Отслеживаемые события:
- Генерация AI-дайджестов (latency, tokens, confidence)
- Подписки/отписки от категорий
- Открытие WebApp Dashboard
- Просмотр событий
- Включение/выключение уведомлений

### Пример логирования:
```python
logger.info(json.dumps({
    "event": "digest_generated",
    "user_id": user_id,
    "category": category,
    "style": style,
    "latency_ms": latency,
    "success": True
}))
```

---

## 🚀 Запуск бота

### Локально:
```bash
# Через скрипт (рекомендуется)
./run_bot.sh

# Напрямую
python3 telegram_bot/bot.py
```

### Через start_services.sh:
```bash
./start_services.sh
# Запустит Flask + Telegram Bot
```

### Проверка статуса:
```bash
./check_processes.sh
# Покажет статус всех сервисов
```

---

## 🔒 Безопасность

### Аутентификация
- Telegram User ID как основной идентификатор
- HMAC SHA256 проверка для WebApp
- Session management через Flask

### Валидация данных
- Все input данные валидируются
- Защита от SQL injection через Supabase
- Санитизация HTML в выводе

### Rate Limiting
- Защита от спама
- Throttling для AI запросов
- Cooldown для создания дайджестов

---

## 📝 Обновления v2.2 (17 октября 2025)

### Главные изменения:
✅ Добавлена кнопка "⚙️ Настройки" в главное меню
✅ Обновлено приветствие с описанием 255 источников
✅ Подробное описание 4 стилей AI-дайджестов
✅ Расширенная справка с командами и возможностями
✅ Улучшенное описание Dashboard
✅ Детальная информация о календаре событий
✅ Подробное описание системы уведомлений

### Новые описания стилей:
- **Newsroom**: Факты, цифры, без эмоций. Для быстрого чтения.
- **Analytical**: Причинно-следственные связи, контекст, инсайты.
- **Magazine**: Захватывающая подача, метафоры, вовлечение.
- **Casual**: Простым языком, как разговор с другом.

---

## 🛠️ Разработка

### Добавление нового обработчика:
1. Создать файл в `telegram_bot/handlers/`
2. Определить `router = Router()`
3. Добавить обработчики с декораторами
4. Зарегистрировать router в `telegram_bot/handlers/__init__.py`

### Пример нового обработчика:
```python
from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

@router.message(Command("mycommand"))
async def cmd_my_command(message: types.Message):
    await message.answer("Hello!")

@router.callback_query(F.data == "my_callback")
async def cb_my_callback(query: types.CallbackQuery):
    await query.message.edit_text("Updated!")
    await query.answer()
```

---

## 📚 Полезные ссылки

- 📖 [Документация aiogram v3](https://docs.aiogram.dev/)
- 🤖 [Telegram Bot API](https://core.telegram.org/bots/api)
- 📊 [Supabase Docs](https://supabase.com/docs)
- 🎨 [Telegram WebApp API](https://core.telegram.org/bots/webapps)

---

**PulseAI Telegram Bot** — персональный AI-ассистент новостей 🤖

