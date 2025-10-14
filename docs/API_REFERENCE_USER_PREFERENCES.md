# API Reference: User Preferences System

## 📋 Обзор

API для управления предпочтениями категорий пользователя. Позволяет получать, обновлять и фильтровать контент на основе пользовательских настроек.

## 🔐 Аутентификация

Все endpoints требуют аутентификации через Telegram WebApp.

**Заголовки:**
```
X-Telegram-Init-Data: <telegram_init_data>
X-Telegram-User-Data: <serialized_telegram_user>
```

## 📡 Endpoints

### GET /api/user/category-preferences

Получение предпочтений пользователя и структуры категорий.

**Параметры:** Нет

**Ответ:**
```json
{
  "status": "success",
  "data": {
    "preferences": {
      "sports": ["football", "tennis", "hockey"],
      "crypto": null,
      "markets": [],
      "tech": ["ai", "cybersecurity"],
      "world": null
    },
    "categories_structure": {
      "sports": {
        "name": "Sports",
        "emoji": "⚽",
        "subcategories": {
          "football": {
            "name": "Football",
            "icon": "⚽"
          },
          "tennis": {
            "name": "Tennis", 
            "icon": "🎾"
          }
        }
      }
    }
  }
}
```

**Коды ответов:**
- `200` - Успешно
- `401` - Не авторизован
- `500` - Ошибка сервера

---

### POST /api/user/category-preferences

Обновление предпочтений пользователя.

**Тело запроса:**
```json
{
  "preferences": {
    "sports": ["football", "tennis", "hockey"],
    "crypto": [],
    "markets": null,
    "tech": ["ai"],
    "world": []
  }
}
```

**Логика значений:**
- `null` - включена вся категория
- `["sub1", "sub2"]` - включены конкретные подкатегории  
- `[]` - категория отключена

**Ответ:**
```json
{
  "status": "success",
  "message": "Category preferences updated successfully",
  "data": {
    "preferences": {
      "sports": ["football", "tennis", "hockey"],
      "crypto": [],
      "markets": null,
      "tech": ["ai"],
      "world": []
    }
  }
}
```

**Коды ответов:**
- `200` - Успешно обновлено
- `400` - Неверные данные
- `401` - Не авторизован
- `500` - Ошибка сервера

**Валидация:**
- Проверка существования категорий
- Проверка существования подкатегорий
- Валидация структуры JSON

---

### GET /api/categories

Получение полной структуры категорий для UI.

**Параметры:** Нет

**Ответ:**
```json
{
  "status": "success",
  "data": {
    "sports": {
      "name": "Sports",
      "emoji": "⚽",
      "subcategories": {
        "football": {
          "name": "Football",
          "icon": "⚽"
        }
      }
    }
  },
  "total_categories": 5,
  "total_subcategories": 47
}
```

---

### GET /api/news/latest

Получение новостей с опциональной фильтрацией.

**Параметры:**
- `page` (int, default: 1) - Номер страницы
- `limit` (int, default: 20) - Количество новостей
- `filter_by_subscriptions` (bool, default: false) - Фильтрация по предпочтениям

**Пример с фильтрацией:**
```
GET /api/news/latest?page=1&limit=20&filter_by_subscriptions=true
```

**Ответ:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "News title",
      "content": "News content",
      "category": "sports",
      "subcategory": "football",
      "source": "ESPN",
      "published_at": "2025-10-14T10:00:00Z",
      "credibility": 0.9,
      "importance": 0.8
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  },
  "filtered_by_subscriptions": true
}
```

---

### GET /api/events/upcoming

Получение событий с опциональной фильтрацией.

**Параметры:**
- `days` (int, default: 30) - Количество дней вперед
- `category` (string, optional) - Фильтр по категории
- `min_importance` (float, default: 0.0) - Минимальная важность
- `filter_by_subscriptions` (bool, default: false) - Фильтрация по предпочтениям

**Пример с фильтрацией:**
```
GET /api/events/upcoming?days=30&filter_by_subscriptions=true
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "uuid",
        "title": "Event title",
        "description": "Event description",
        "category": "sports",
        "subcategory": "football",
        "start_date": "2025-10-15T15:00:00Z",
        "importance": 0.9,
        "source": "ESPN"
      }
    ],
    "total_events": 50,
    "filtered_by_subscriptions": true
  }
}
```

## 🏗️ Внутренние функции

### get_user_category_preferences(user_id)

Получение предпочтений категорий пользователя.

**Параметры:**
- `user_id` (str) - UUID пользователя

**Возвращает:**
```python
{
    "sports": ["football", "tennis"],
    "crypto": null,
    "markets": []
}
```

### get_active_categories(user_id)

Получение активных категорий для фильтрации.

**Параметры:**
- `user_id` (str) - UUID пользователя

**Возвращает:**
```python
{
    'full_categories': ['crypto', 'tech'],
    'subcategories': {
        'sports': ['football', 'tennis'],
        'markets': ['earnings']
    }
}
```

### upsert_user_category_preferences(user_id, preferences)

Сохранение/обновление предпочтений пользователя.

**Параметры:**
- `user_id` (str) - UUID пользователя
- `preferences` (dict) - Словарь предпочтений

**Возвращает:**
- `bool` - True если успешно сохранено

## 📊 Структуры данных

### Category Preferences
```python
{
    "category_id": string | null | [string]
}
```

**Примеры:**
```python
# Вся категория включена
"crypto": null

# Конкретные подкатегории
"sports": ["football", "tennis", "hockey"]

# Категория отключена
"markets": []
```

### Categories Structure
```python
{
    "category_id": {
        "name": str,
        "emoji": str,
        "subcategories": {
            "subcategory_id": {
                "name": str,
                "icon": str
            }
        }
    }
}
```

## 🔍 Обработка ошибок

### Стандартные ошибки

**401 Unauthorized**
```json
{
  "error": "Authentication required"
}
```

**400 Bad Request**
```json
{
  "status": "error",
  "message": "Invalid category: invalid_category. Must be one of: crypto, sports, markets, tech, world"
}
```

**500 Internal Server Error**
```json
{
  "status": "error", 
  "message": "Error updating preferences: Database connection error"
}
```

### Валидация

**Несуществующая категория:**
```json
{
  "status": "error",
  "message": "Invalid category: invalid_category. Must be one of: crypto, sports, markets, tech, world"
}
```

**Несуществующая подкатегория:**
```json
{
  "status": "error",
  "message": "Invalid subcategory 'invalid_sub' for category 'sports'"
}
```

## 🧪 Примеры использования

### Frontend Integration

```typescript
// Получение предпочтений
const response = await fetch('/api/user/category-preferences', {
  headers: authHeaders
});
const { data } = await response.json();

// Обновление предпочтений
await fetch('/api/user/category-preferences', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    ...authHeaders
  },
  body: JSON.stringify({
    preferences: {
      sports: ['football', 'tennis'],
      crypto: null,
      markets: []
    }
  })
});

// Получение отфильтрованных новостей
const newsResponse = await fetch('/api/news/latest?filter_by_subscriptions=true', {
  headers: authHeaders
});
```

### Backend Integration

```python
from database.db_models import get_user_category_preferences, get_active_categories

# Получение предпочтений
preferences = get_user_category_preferences(user_id)

# Получение активных категорий для фильтрации
active_cats = get_active_categories(user_id)
full_categories = active_cats.get('full_categories', [])
subcategories = active_cats.get('subcategories', {})

# Фильтрация контента
filtered_content = []
for item in content:
    category = item.get('category')
    subcategory = item.get('subcategory')
    
    if category in full_categories:
        filtered_content.append(item)
    elif category in subcategories and subcategory in subcategories[category]:
        filtered_content.append(item)
```

## 📈 Мониторинг и логирование

### Логи фильтрации
```
🔍 Фильтрация новостей для пользователя {user_id}
📊 Активные категории: full=['crypto'], subcategories={'sports': ['football']}
✅ Применяем фильтрацию: 100 новостей до фильтрации
🎯 Фильтрация завершена: 15 новостей после фильтрации
```

### Метрики производительности
- Время ответа API
- Количество отфильтрованных элементов
- Использование предпочтений пользователя

---

*API Reference создан: 14 октября 2025*  
*Версия API: 1.0*
