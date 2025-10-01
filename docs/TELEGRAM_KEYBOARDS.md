# Telegram Keyboards Documentation

Документация по клавиатурам Telegram бота PulseAI.

## Обзор

Бот использует Inline клавиатуры для навигации и управления подписками/уведомлениями.

## Структура клавиатур

### 1. Главное меню (`main_inline_keyboard`)

```python
def main_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📰 Новости", callback_data="digest:all")],
            [types.InlineKeyboardButton(text="🤖 AI-дайджест", callback_data="digest_ai")],
            [types.InlineKeyboardButton(text="📅 События", callback_data="events")],
            [types.InlineKeyboardButton(text="📋 Подписки", callback_data="subscriptions")],  # НОВОЕ
            [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],  # НОВОЕ
        ]
    )
```

### 2. Подписки (`subscriptions_inline_keyboard`)

```python
def subscriptions_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subs")],
            [types.InlineKeyboardButton(text="➕ Подписаться", callback_data="subscribe_menu")],
            [types.InlineKeyboardButton(text="➖ Отписаться", callback_data="unsubscribe_menu")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )
```

### 3. Уведомления (`notifications_inline_keyboard`)

```python
def notifications_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🔔 Мои уведомления", callback_data="my_notifications")],
            [types.InlineKeyboardButton(text="✅ Включить дайджест", callback_data="notify_on_digest")],
            [types.InlineKeyboardButton(text="❌ Выключить дайджест", callback_data="notify_off_digest")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )
```

### 4. Выбор категорий (`categories_inline_keyboard`)

```python
def categories_inline_keyboard(action: str = "subscribe") -> types.InlineKeyboardMarkup:
    keyboard = []
    for key, label in CATEGORIES.items():
        keyboard.append([
            types.InlineKeyboardButton(
                text=label, 
                callback_data=f"{action}:{key}"
            )
        ])
    
    keyboard.append([
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
```

## Callback Handlers

### Подписки

| Callback Data | Handler | Описание |
|---------------|---------|----------|
| `subscriptions` | `cb_subscriptions_menu` | Показать меню подписок |
| `my_subs` | `cb_my_subs` | Показать список подписок пользователя |
| `subscribe_menu` | `cb_subscribe_menu` | Показать выбор категории для подписки |
| `unsubscribe_menu` | `cb_unsubscribe_menu` | Показать выбор категории для отписки |
| `subscribe:{category}` | `cb_subscribe_category` | Подписаться на выбранную категорию |
| `unsubscribe:{category}` | `cb_unsubscribe_category` | Отписаться от выбранной категории |

### Уведомления

| Callback Data | Handler | Описание |
|---------------|---------|----------|
| `notifications` | `cb_notifications_menu` | Показать меню уведомлений |
| `my_notifications` | `cb_my_notifications` | Показать настройки уведомлений пользователя |
| `notify_on_digest` | `cb_notify_on_digest` | Включить уведомления дайджеста |
| `notify_off_digest` | `cb_notify_off_digest` | Отключить уведомления дайджеста |

## Пользовательский интерфейс

### Поток навигации

```
Главное меню
├── 📰 Новости
├── 🤖 AI-дайджест  
├── 📅 События
├── 📋 Подписки
│   ├── 📋 Мои подписки
│   ├── ➕ Подписаться
│   │   └── Выбор категории → Подписка
│   └── ➖ Отписаться
│       └── Выбор категории → Отписка
└── 🔔 Уведомления
    ├── 🔔 Мои уведомления
    ├── ✅ Включить дайджест
    └── ❌ Выключить дайджест
```

### Примеры использования

#### Подписка на категорию
1. Пользователь нажимает "📋 Подписки"
2. Выбирает "➕ Подписаться"
3. Выбирает категорию (например, "Криптовалюты")
4. Получает подтверждение "✅ Подписка на crypto добавлена"
5. Возвращается в меню подписок

#### Просмотр подписок
1. Пользователь нажимает "📋 Подписки"
2. Выбирает "📋 Мои подписки"
3. Видит список своих подписок:
   ```
   📋 Ваши подписки:
   
   1. crypto
   2. economy
   3. technology
   ```

#### Управление уведомлениями
1. Пользователь нажимает "🔔 Уведомления"
2. Выбирает "🔔 Мои уведомления"
3. Видит текущие настройки:
   ```
   🔔 Ваши уведомления:
   
   1. digest - ✅ включено
      Частота: daily, время: 9:00
   ```

## Технические детали

### Импорты
```python
from telegram_bot.keyboards import (
    subscriptions_inline_keyboard,
    notifications_inline_keyboard,
    categories_inline_keyboard,
    back_inline_keyboard,
)
```

### Использование в хендлерах
```python
@router.callback_query(F.data == "subscriptions")
async def cb_subscriptions_menu(query: types.CallbackQuery):
    await query.message.edit_text(
        "📋 Управление подписками",
        parse_mode="HTML",
        reply_markup=subscriptions_inline_keyboard()
    )
```

### Обработка ошибок
Все callback-хендлеры включают:
- Try/catch блоки для обработки исключений
- Логирование ошибок
- Graceful fallback с сообщениями об ошибках
- Возврат в соответствующие меню

## Доступные категории

Категории берутся из `digests.configs.CATEGORIES`:

- `crypto` - Криптовалюты
- `economy` - Экономика  
- `technology` - Технологии
- `world` - Мир
- `politics` - Политика
- `business` - Бизнес

## Доступные типы уведомлений

- `digest` - Ежедневные дайджесты
- `events` - Уведомления о событиях
- `breaking` - Экстренные новости
