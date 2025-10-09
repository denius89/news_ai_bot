"""
digests/configs.py
Централизованное хранилище категорий, периодов и стилей для AI-дайджестов.
"""

# Категории новостей
CATEGORIES = {
    "crypto": "Crypto",
    "economy": "Economy", 
    "world": "World",
    "technology": "Technology",
    "politics": "Politics",
}

# Периоды выборки
PERIODS = {
    "today": "Сегодня",
    "7d": "Последние 7 дней",
    "30d": "Последние 30 дней",
}

# Стили генерации текста
STYLES = {
    "analytical": "Аналитический",
    "business": "Бизнес",
    "meme": "Мемный",
}
