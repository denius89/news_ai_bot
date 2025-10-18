# digests/prompts_v2.py
"""
PULSEAI — SUPER PROMPT: РЕАЛИСТИЧНЫЕ ИНТЕЛЛЕКТУАЛЬНЫЕ AI-ДАЙДЖЕСТЫ (JOURNALISTIC v2)

Новый модуль промтов для профессиональной журналистской генерации дайджестов.
Поддерживает 4 стиля, 4 тона, 3 длины и 2 аудитории.
"""

import json
import logging
from typing import Dict, List, Tuple, Any, Optional  # noqa: F401

logger = logging.getLogger("prompts_v2")

# Import personas for automatic selection
try:
    from ai_modules.personas import PersonaSelector, select_persona_for_context
    PERSONAS_AVAILABLE = True
except ImportError:
    PERSONAS_AVAILABLE = False
    logger.warning("Personas module not available, using default persona selection")

# ============================================================================
# STYLE PROFILES (4 стиля)
# ============================================================================

STYLE_CARDS = {
    "newsroom": {
        "name": "Newsroom",
        "description": "Reuters/Bloomberg стиль — факты, цифры, краткость",
        "characteristics": [
            "Краткие предложения (15-20 слов)",
            "Факты без интерпретации",
            "Цифры и статистика в приоритете",
            "1-2 абзаца максимум",
            "Нейтральный тон без эмоций",
        ],
        "expert_persona": "Опытный журналист Reuters с 15-летним стажем",
        "writing_style": "пишет как для профессионального издания, использует точные формулировки",
    },
    "analytical": {
        "name": "Аналитический",
        "description": "Глубокий анализ с причинно-следственными связями",
        "characteristics": [
            "Длинные предложения с анализом",
            "Причинно-следственные связи",
            "Контекст и предыстория",
            "2-3 абзаца с развитием мысли",
            "Интеллектуальный тон",
        ],
        "expert_persona": "Ведущий аналитик The Economist",
        "writing_style": "анализирует события как эксперт, выявляет скрытые связи и тренды",
    },
    "magazine": {
        "name": "Magazine",
        "description": "Storytelling стиль — engaging, метафоры, читабельность",
        "characteristics": [
            "Живые метафоры и аналогии",
            "Эмоциональная окраска",
            "Читабельный стиль",
            "2-4 абзаца с развитием",
            "Engaging тон",
        ],
        "expert_persona": "Талантливый автор The Atlantic",
        "writing_style": "превращает факты в увлекательную историю, использует метафоры и аналогии",
    },
    "casual": {
        "name": "Простой",
        "description": "Разговорный стиль для Telegram — просто, понятно, дружелюбно",
        "characteristics": [
            "Простые предложения",
            "Разговорные обороты",
            "Дружелюбный тон",
            "1-2 абзаца",
            "Понятно для всех",
        ],
        "expert_persona": "Опытный блогер с миллионной аудиторией",
        "writing_style": "объясняет сложное простыми словами, как другу за чашкой кофе",
    },
    "business": {
        "name": "Бизнес",
        "description": "Корпоративный стиль — структурированно, профессионально, с фокусом на влияние",
        "characteristics": [
            "Структурированные абзацы",
            "Фокус на рыночном влиянии",
            "Конкретные цифры и данные",
            "Профессиональная терминология",
            "Executive summary подход",
        ],
        "expert_persona": "Управляющий директор McKinsey",
        "writing_style": "анализирует ситуацию как бизнес-консультант, фокусируется на стратегических последствиях",
    },
    "explanatory": {
        "name": "Объясняющий",
        "description": "Образовательный стиль — четко, пошагово, с контекстом",
        "characteristics": [
            "Пошаговые объяснения",
            "Расшифровка терминов",
            "Исторический контекст",
            "Причинно-следственные связи",
            "Доступный язык",
        ],
        "expert_persona": "Профессор Стэнфорда",
        "writing_style": "преподает сложные концепции простыми словами, всегда объясняет контекст",
    },
    "technical": {
        "name": "Технический",
        "description": "Экспертный стиль — глубокое погружение, техническая точность",
        "characteristics": [
            "Техническая терминология",
            "Детальный анализ",
            "Экспертные инсайты",
            "Ссылки на источники",
            "Профессиональная глубина",
        ],
        "expert_persona": "Ведущий инженер Google",
        "writing_style": "пишет как технический эксперт, использует профессиональную терминологию и глубокий анализ",
    },
    "meme": {
        "name": "Мемный",
        "description": "Юмор и ирония — engaging, relatable, с элементами сатиры",
        "characteristics": [
            "Юмористические сравнения",
            "Ироничные комментарии",
            "Мемные отсылки",
            "Легкий тон",
            "Relatable контент",
        ],
        "expert_persona": "Популярный финансовый мемер с Twitter",
        "writing_style": "пишет с юмором и иронией, использует мемы и современные отсылки для объяснения финансовых событий",
    },
}

# ============================================================================
# CATEGORY CARDS (5 категорий)
# ============================================================================

CATEGORY_CARDS = {
    "crypto": {
        "name": "Криптовалюты",
        "expert": "Виталик Бутерин",
        "subcategories": {
            "bitcoin": {
                "focus": "BTC, майнинг, халвинг, институциональное принятие",
                "keywords": ["bitcoin", "btc", "халвинг", "майнинг", "etf"]
            },
            "ethereum": {
                "focus": "ETH, смарт-контракты, обновления сети, DeFi",
                "keywords": ["ethereum", "eth", "eip", "merge", "staking"]
            },
            "defi": {
                "focus": "Децентрализованные финансы, протоколы, TVL",
                "keywords": ["defi", "tvl", "yield", "lending", "dex"]
            },
            "nft": {
                "focus": "NFT, метавселенные, коллекции",
                "keywords": ["nft", "opensea", "метавселенная", "коллекция"]
            },
            "regulation": {
                "focus": "Регуляция, законодательство, SEC, MiCA",
                "keywords": ["sec", "регуляция", "mica", "закон", "запрет"]
            }
        },
        "focus": "блокчейн, DeFi, NFT, регуляция",
        "keywords": ["блокчейн", "DeFi", "NFT", "регуляция"]
    },
    "markets": {
        "name": "Финансовые рынки",
        "expert": "Уоррен Баффет",
        "subcategories": {
            "stocks": {
                "focus": "Акции, индексы, корпоративные новости",
                "keywords": ["акции", "s&p500", "nasdaq", "дивиденды"]
            },
            "forex": {
                "focus": "Валютные пары, ЦБ, процентные ставки",
                "keywords": ["forex", "доллар", "евро", "фрс", "ставка"]
            },
            "commodities": {
                "focus": "Нефть, золото, сырьевые товары",
                "keywords": ["нефть", "золото", "газ", "металлы"]
            },
            "bonds": {
                "focus": "Облигации, доходность, долговой рынок",
                "keywords": ["облигации", "доходность", "трежерис"]
            }
        },
        "focus": "фондовые рынки, валюты, сырьевые товары",
        "keywords": ["акции", "валюта", "нефть", "золото"]
    },
    "tech": {
        "name": "Технологии",
        "expert": "Илон Маск",
        "subcategories": {
            "ai": {
                "focus": "ИИ, LLM, машинное обучение",
                "keywords": ["ai", "gpt", "llm", "машинное обучение"]
            },
            "startups": {
                "focus": "Стартапы, венчур, IPO, M&A",
                "keywords": ["стартап", "венчур", "ipo", "сделка"]
            },
            "cybersecurity": {
                "focus": "Кибербезопасность, уязвимости, атаки",
                "keywords": ["взлом", "уязвимость", "кибератака", "cve"]
            },
            "gadgets": {
                "focus": "Гаджеты, релизы, обзоры",
                "keywords": ["iphone", "samsung", "релиз", "анонс"]
            }
        },
        "focus": "ИИ, стартапы, кибербезопасность, гаджеты",
        "keywords": ["ИИ", "стартапы", "кибербезопасность"]
    },
    "sports": {
        "name": "Спорт",
        "expert": "Василий Уткин",
        "subcategories": {
            "football": {
                "focus": "Футбол, матчи, трансферы, турниры",
                "keywords": ["футбол", "матч", "трансфер", "лига"]
            },
            "basketball": {
                "focus": "Баскетбол, NBA, Евролига",
                "keywords": ["баскетбол", "nba", "евролига"]
            },
            "esports": {
                "focus": "Киберспорт, турниры, команды",
                "keywords": ["esports", "dota", "csgo", "турнир"]
            },
            "other": {
                "focus": "Другие виды спорта",
                "keywords": ["хоккей", "теннис", "формула"]
            }
        },
        "focus": "результаты, трансферы, турниры",
        "keywords": ["матчи", "трансферы", "турниры"]
    },
    "world": {
        "name": "Мир",
        "expert": "Дмитрий Киселев",
        "subcategories": {
            "geopolitics": {
                "focus": "Геополитика, международные отношения",
                "keywords": ["геополитика", "санкции", "саммит"]
            },
            "conflicts": {
                "focus": "Конфликты, военные действия",
                "keywords": ["конфликт", "война", "перемирие"]
            },
            "diplomacy": {
                "focus": "Дипломатия, переговоры, соглашения",
                "keywords": ["дипломатия", "переговоры", "соглашение"]
            },
            "elections": {
                "focus": "Выборы, политика, референдумы",
                "keywords": ["выборы", "референдум", "голосование"]
            }
        },
        "focus": "геополитика, конфликты, дипломатия",
        "keywords": ["геополитика", "конфликты", "дипломатия"]
    }
}

# ============================================================================
# TONE OPTIONS (4 тона)
# ============================================================================

TONE_CARDS = {
    "neutral": {
        "name": "Нейтральный",
        "description": "Сбалансированная подача фактов без эмоций",
        "characteristics": ["Объективность", "Факты", "Сбалансированность", "Профессионализм"],
    },
    "insightful": {
        "name": "Инсайты",
        "description": "Акцент на инсайты, контекст и глубокое понимание",
        "characteristics": ["Анализ", "Контекст", "Инсайты", "Предвидение"],
    },
    "critical": {
        "name": "Критический",
        "description": "Критический анализ с выявлением проблем",
        "characteristics": ["Скептицизм", "Анализ рисков", "Выявление проблем", "Критическое мышление"],
    },
    "optimistic": {
        "name": "Позитивный",
        "description": "Позитивный фокус на возможностях и решениях",
        "characteristics": ["Позитивность", "Возможности", "Решения", "Прогресс"],
    },
}

# ============================================================================
# LENGTH SPECIFICATIONS (3 длины)
# ============================================================================

LENGTH_SPECS = {
    "short": {
        "name": "Короткий",
        "max_words": 300,
        "paragraphs": "2-3",
        "description": "Краткая сводка для быстрого чтения",
    },
    "medium": {
        "name": "Средний",
        "max_words": 600,
        "paragraphs": "3-4",
        "description": "Сбалансированный дайджест с контекстом",
    },
    "long": {
        "name": "Длинный",
        "max_words": 1000,
        "paragraphs": "4-6",
        "description": "Подробный анализ с глубоким контекстом",
    },
}

# ============================================================================
# AUDIENCE TARGETING (2 аудитории)
# ============================================================================

AUDIENCE_SPECS = {
    "general": {
        "name": "Общая аудитория",
        "description": "Широкая аудитория без специальных знаний",
        "characteristics": ["Простые объяснения", "Минимум терминов", "Общие понятия", "Доступность"],
    },
    "pro": {
        "name": "Профессионалы",
        "description": "Аудитория с профессиональными знаниями в области",
        "characteristics": ["Специализированные термины", "Технические детали", "Экспертный уровень", "Глубина"],
    },
}

# ============================================================================
# FEW-SHOT EXAMPLES
# ============================================================================

FEW_SHOT_EXAMPLES = [
    {
        "category": "crypto",
        "style": "newsroom",
        "tone": "neutral",
        "length": "short",
        "input": "Bitcoin достиг $50,000, Ethereum обновил рекорд",
        "output": {
            "title": "Криптовалюты обновили максимумы",
            "dek": "Bitcoin торгуется выше $50,000, Ethereum установил новый рекорд",
            "summary": "Bitcoin впервые с апреля превысил отметку $50,000, торгуясь на уровне $50,200. Ethereum обновил исторический максимум, достигнув $3,200. Рост связан с институциональным интересом и позитивными регуляторными новостями.",
            "why_important": [
                "Психологический барьер $50,000 для Bitcoin может привлечь новых инвесторов",
                "Рост Ethereum подтверждает активность в DeFi и NFT секторах",
                "Институциональный интерес к криптовалютам продолжает расти",
            ],
            "context": "Рост происходит на фоне заявлений регуляторов о разработке четких правил для криптовалютного рынка.",
            "what_next": "Аналитики ожидают продолжения роста при сохранении позитивного регуляторного фона.",
            "sources_cited": ["CoinDesk", "Reuters", "Bloomberg"],
            "meta": {
                "style_profile": "newsroom",
                "tone": "neutral",
                "length": "short",
                "audience": "general",
                "confidence": 0.95,
            },
        },
    },
    {
        "category": "tech",
        "style": "analytical",
        "tone": "insightful",
        "length": "medium",
        "input": "OpenAI представила GPT-5, Google анонсировала Gemini Pro",
        "output": {
            "title": "Новая эра ИИ: GPT-5 против Gemini Pro",
            "dek": "OpenAI и Google представили следующее поколение языковых моделей",
            "summary": "OpenAI анонсировала GPT-5 с улучшенными возможностями рассуждения и планирования. Одновременно Google представила Gemini Pro с фокусом на мультимодальность и интеграцию с экосистемой. Конкуренция между лидерами ИИ вступает в новую фазу.",
            "why_important": [
                "GPT-5 демонстрирует значительный прогресс в логическом мышлении",
                "Gemini Pro интегрируется с Google Workspace, меняя рабочие процессы",
                "Конкуренция ускоряет инновации в области ИИ",
            ],
            "context": "Рынок ИИ растет экспоненциально, с прогнозируемым объемом $1.8 трлн к 2030 году.",
            "what_next": "Ожидается интеграция новых моделей в корпоративные решения и потребительские приложения.",
            "sources_cited": ["TechCrunch", "The Verge", "Wired"],
            "meta": {
                "style_profile": "analytical",
                "tone": "insightful",
                "length": "medium",
                "audience": "pro",
                "confidence": 0.92,
            },
        },
    },
]

# ============================================================================
# SYSTEM PROMPT TEMPLATE
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """Ты — {expert_persona}. {writing_style}

ТВОЯ СПЕЦИАЛИЗАЦИЯ: {category_name}

ЗАДАЧА: Создать увлекательный дайджест как для ведущего издания.

СТИЛЬ НАПИСАНИЯ:
✓ Связное повествование — каждый абзац плавно переходит в следующий
✓ Показывай СВЯЗИ между событиями ("На фоне этого...", "Параллельно...", "В то же время...")
✓ Используй метафоры и аналогии для объяснения сложного
✓ Добавляй контекст и предысторию к каждому событию
✓ Анализируй причинно-следственные связи
✓ Создавай нарратив — история развития событий

СТРУКТУРА:
1. Захватывающее вступление (2-3 предложения о главном тренде)
2. Основная часть: развитие тем с деталями и анализом
3. Контекст: как это связано с предыдущими событиями и предстоящими
4. Выводы: что это значит и что ждать дальше

ТЕХНИКИ STORYTELLING:
- Начинай с самого интересного факта
- Используй конкретные цифры и детали
- Цитируй источники естественно
- Создавай интригу ("Это не первый раз когда...")
- Завершай прогнозом или вопросом
- Используй временные маркеры ("Вчера", "На этой неделе", "Одновременно")

КАЧЕСТВО ТЕКСТА:
- Избегай повторений и тавтологий
- Каждое предложение добавляет новую информацию
- Используй активный залог где возможно
- Проверяй логическую последовательность
- Убедись, что каждый абзац имеет четкую цель

Параметры:
СТИЛЬ: {style_description}
ХАРАКТЕРИСТИКИ: {characteristics}
ТОН: {tone_description}
ДЛИНА: {length_description} ({max_words} слов максимум)
АУДИТОРИЯ: {audience_description}

Пиши так, чтобы читатель не мог оторваться до конца.

ФОРМАТ ОТВЕТА: Строго JSON без дополнительного текста."""

# ============================================================================
# USER PROMPT TEMPLATE
# ============================================================================

USER_PROMPT_TEMPLATE = """СОЗДАЙ ДАЙДЖЕСТ ПО ТЕМЕ: {category_name}

ЭКСПЕРТИЗА: {expert}
ФОКУС: {focus}
ВЛИЯНИЕ: {impact}
КЛЮЧЕВЫЕ СЛОВА: {keywords}

НОВОСТИ ДЛЯ АНАЛИЗА:
{news_text}

ТРЕБОВАНИЯ К КАЧЕСТВУ:
- importance >= {min_importance} И credibility >= {min_credibility}
- Только проверенные источники
- Факты без интерпретации
- Соответствие стилю {style_name}

ВЕРНИ JSON В ТОЧНОМ ФОРМАТЕ:
{output_schema}"""

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

OUTPUT_SCHEMA = {
    "title": "string (краткий заголовок, 5-8 слов)",
    "dek": "string (подзаголовок, 10-15 слов)",
    "summary": "string (основной текст дайджеста)",
    "why_important": "array of strings (3 пункта максимум)",
    "context": "string (дополнительный контекст, опционально)",
    "what_next": "string (что ожидать дальше, опционально)",
    "sources_cited": "array of strings (источники из новостей)",
    "meta": {
        "style_profile": "string (newsroom|analytical|magazine|casual)",
        "tone": "string (neutral|insightful|critical|optimistic)",
        "length": "string (short|medium|long)",
        "audience": "string (general|pro)",
        "confidence": "number (0.0-1.0, оценка качества)",
    },
}

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================


def build_prompt(input_payload: Dict[str, Any]) -> Tuple[str, str]:
    """
    Build system and user prompts from input payload.

    Args:
        input_payload: Dictionary with keys:
            - category: str (crypto, markets, tech, sports, world)
            - style_profile: str (newsroom, analytical, magazine, casual)
            - tone: str (neutral, insightful, critical, optimistic)
            - length: str (short, medium, long)
            - audience: str (general, pro)
            - news_text: str (formatted news data)
            - min_importance: float (default 0.6)
            - min_credibility: float (default 0.7)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Validate input
    required_keys = ["category", "style_profile", "tone", "length", "audience", "news_text"]
    for key in required_keys:
        if key not in input_payload:
            raise ValueError(f"Missing required key: {key}")

    # Get configurations
    category = input_payload["category"]
    style_profile = input_payload["style_profile"]
    tone = input_payload["tone"]
    length = input_payload["length"]
    audience = input_payload["audience"]

    # Validate values
    if style_profile not in STYLE_CARDS:
        raise ValueError(f"Invalid style_profile: {style_profile}")
    if tone not in TONE_CARDS:
        raise ValueError(f"Invalid tone: {tone}")
    if length not in LENGTH_SPECS:
        raise ValueError(f"Invalid length: {length}")
    if audience not in AUDIENCE_SPECS:
        raise ValueError(f"Invalid audience: {audience}")
    if category not in CATEGORY_CARDS:
        raise ValueError(f"Invalid category: {category}")

    # Get style configuration
    style_config = STYLE_CARDS[style_profile]
    tone_config = TONE_CARDS[tone]
    length_config = LENGTH_SPECS[length]
    audience_config = AUDIENCE_SPECS[audience]
    category_config = CATEGORY_CARDS[category]

    # Build system prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        expert_persona=style_config["expert_persona"],
        writing_style=style_config["writing_style"],
        category_name=category_config["name"],
        style_name=style_config["name"],
        style_description=style_config["description"],
        characteristics=", ".join(style_config["characteristics"]),
        tone_description=tone_config["description"],
        length_description=length_config["description"],
        max_words=length_config["max_words"],
        audience_description=audience_config["description"],
        tone_name=tone_config["name"],
    )

    # Build user prompt
    user_prompt = USER_PROMPT_TEMPLATE.format(
        category_name=category_config["name"],
        expert=category_config["expert"],
        focus=category_config["focus"],
        impact=category_config.get("impact", category_config["focus"]),  # Используем focus если impact нет
        keywords=", ".join(category_config["keywords"]),
        news_text=input_payload["news_text"],
        min_importance=input_payload.get("min_importance", 0.6),
        min_credibility=input_payload.get("min_credibility", 0.7),
        style_name=style_config["name"],
        output_schema=json.dumps(OUTPUT_SCHEMA, indent=2, ensure_ascii=False),
    )

    return system_prompt, user_prompt


def validate_sources(
    sources: List[Dict[str, Any]], min_importance: float = 0.6, min_credibility: float = 0.7
) -> Dict[str, Any]:
    """
    Validate sources meet quality threshold.

    Args:
        sources: List of source dictionaries with 'importance' and 'credibility' keys
        min_importance: Minimum importance threshold
        min_credibility: Minimum credibility threshold

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "valid_sources": list,
            "skipped_count": int,
            "reason": str (if invalid)
        }
    """
    valid_sources = []
    skipped_count = 0

    for source in sources:
        importance = source.get("importance", 0.0)
        credibility = source.get("credibility", 0.0)

        if importance >= min_importance and credibility >= min_credibility:
            valid_sources.append(source)
        else:
            skipped_count += 1

    if not valid_sources:
        return {
            "valid": False,
            "valid_sources": [],
            "skipped_count": skipped_count,
            "reason": f"low importance/credibility (min: {min_importance}/{min_credibility})",
        }

    return {"valid": True, "valid_sources": valid_sources, "skipped_count": skipped_count, "reason": None}


def get_style_config(style_profile: str) -> Dict[str, Any]:
    """Get configuration for a specific style profile."""
    if style_profile not in STYLE_CARDS:
        raise ValueError(f"Unknown style profile: {style_profile}")
    return STYLE_CARDS[style_profile]


def get_category_config(category: str) -> Dict[str, Any]:
    """Get configuration for a specific category."""
    if category not in CATEGORY_CARDS:
        raise ValueError(f"Unknown category: {category}")
    return CATEGORY_CARDS[category]


def get_tone_config(tone: str) -> Dict[str, Any]:
    """Get configuration for a specific tone."""
    if tone not in TONE_CARDS:
        raise ValueError(f"Unknown tone: {tone}")
    return TONE_CARDS[tone]


def get_length_config(length: str) -> Dict[str, Any]:
    """Get configuration for a specific length."""
    if length not in LENGTH_SPECS:
        raise ValueError(f"Unknown length: {length}")
    return LENGTH_SPECS[length]


def get_audience_config(audience: str) -> Dict[str, Any]:
    """Get configuration for a specific audience."""
    if audience not in AUDIENCE_SPECS:
        raise ValueError(f"Unknown audience: {audience}")
    return AUDIENCE_SPECS[audience]


# ============================================================================
# QUALITY CHECKS
# ============================================================================


def validate_output_schema(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate output matches expected schema.

    Args:
        output: Generated digest output

    Returns:
        Validation result with errors if any
    """
    errors = []

    # Required fields
    required_fields = ["title", "dek", "summary", "why_important", "meta"]
    for field in required_fields:
        if field not in output:
            errors.append(f"Missing required field: {field}")

    # Validate meta structure
    if "meta" in output:
        meta = output["meta"]
        meta_required = ["style_profile", "tone", "length", "audience", "confidence"]
        for field in meta_required:
            if field not in meta:
                errors.append(f"Missing meta field: {field}")

    # Validate confidence range
    if "meta" in output and "confidence" in output["meta"]:
        confidence = output["meta"]["confidence"]
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            errors.append("Confidence must be a number between 0.0 and 1.0")

    return {"valid": len(errors) == 0, "errors": errors}


def calculate_confidence_score(output: Dict[str, Any], sources_count: int) -> float:
    """
    Calculate confidence score based on output quality and source count.

    Args:
        output: Generated digest output
        sources_count: Number of sources used

    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 0.0

    # Base score for required fields
    required_fields = ["title", "dek", "summary", "why_important"]
    for field in required_fields:
        if field in output and output[field]:
            score += 0.15

    # Meta fields
    if "meta" in output:
        meta = output["meta"]
        meta_fields = ["style_profile", "tone", "length", "audience"]
        for field in meta_fields:
            if field in meta and meta[field]:
                score += 0.05

    # Source count bonus
    if sources_count >= 3:
        score += 0.1
    elif sources_count >= 2:
        score += 0.05

    # Content quality indicators
    if "summary" in output and len(output["summary"]) > 100:
        score += 0.05

    if "why_important" in output and len(output["why_important"]) >= 2:
        score += 0.05

    return min(score, 1.0)


def get_subcategory_config(category: str, subcategory: str) -> Dict[str, Any]:
    """Get configuration for a specific subcategory."""
    if category not in CATEGORY_CARDS:
        raise ValueError(f"Unknown category: {category}")

    category_config = CATEGORY_CARDS[category]
    if "subcategories" not in category_config:
        raise ValueError(f"Category {category} has no subcategories")

    if subcategory not in category_config["subcategories"]:
        raise ValueError(f"Unknown subcategory {subcategory} for category {category}")

    return category_config["subcategories"][subcategory]


def get_available_subcategories(category: str) -> List[str]:
    """Get list of available subcategories for a category."""
    if category not in CATEGORY_CARDS:
        raise ValueError(f"Unknown category: {category}")

    category_config = CATEGORY_CARDS[category]
    if "subcategories" not in category_config:
        return []

    return list(category_config["subcategories"].keys())


def build_prompt_with_subcategory(
    input_payload: Dict[str, Any],
    subcategory: str = None
) -> Tuple[str, str]:
    """
    Build system and user prompts with subcategory support.

    Args:
        input_payload: Dictionary with keys (same as build_prompt)
        subcategory: Optional subcategory string (e.g., "bitcoin", "stocks")

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # First get base prompts
    system_prompt, user_prompt = build_prompt(input_payload)

    category = input_payload["category"]

    # If subcategory is specified and exists, enhance prompts
    if subcategory:
        try:
            subcategory_config = get_subcategory_config(category, subcategory)

            # Enhance system prompt with subcategory info
            subcategory_info = f"\n\nСПЕЦИАЛИЗАЦИЯ: {category} → {subcategory_config['focus']}\nКЛЮЧЕВЫЕ СЛОВА ПОДКАТЕГОРИИ: {', '.join(subcategory_config['keywords'])}"
            system_prompt += subcategory_info

            # Enhance user prompt with subcategory context
            subcategory_context = f"\n\nПОДКАТЕГОРИЯ: {subcategory}\nФОКУС ПОДКАТЕГОРИИ: {subcategory_config['focus']}\nКЛЮЧЕВЫЕ СЛОВА: {', '.join(subcategory_config['keywords'])}"
            user_prompt += subcategory_context

        except ValueError:
            logger.warning(f"Invalid subcategory {subcategory} for category {category}, using base configuration")

    return system_prompt, user_prompt


def build_prompt_with_persona(
    input_payload: Dict[str, Any],
    persona_id: Optional[str] = None,
    subcategory: Optional[str] = None,
    urgency: float = 0.5,
    complexity: float = 0.5,
    news_count: int = 5,
    avg_importance: float = 0.5
) -> Tuple[str, str]:
    """
    Build system and user prompts with automatic persona selection.
    
    Args:
        input_payload: Dictionary with keys (same as build_prompt)
        persona_id: Optional persona ID to use (if None, auto-selects)
        subcategory: Optional subcategory string
        urgency: Urgency level (0.0-1.0)
        complexity: Complexity level (0.0-1.0)
        news_count: Number of news items
        avg_importance: Average importance of news items
        
    Returns:
        Tuple of (system_prompt, user_prompt, selected_persona_id)
    """
    category = input_payload["category"]
    
    # Auto-select persona if not provided and personas are available
    if not persona_id and PERSONAS_AVAILABLE:
        try:
            persona_id, persona_config = select_persona_for_context(
                category=category,
                subcategory=subcategory,
                urgency=urgency,
                complexity=complexity,
                news_count=news_count,
                avg_importance=avg_importance
            )
            
            # Override style_profile in input_payload with persona style
            if persona_config.get("style") in STYLE_CARDS:
                input_payload["style_profile"] = persona_config["style"]
                logger.info(f"Auto-selected persona: {persona_id} with style {persona_config['style']}")
            
        except Exception as e:
            logger.warning(f"Failed to auto-select persona: {e}, using default style")
    
    # Get base prompts (with or without subcategory)
    if subcategory:
        system_prompt, user_prompt = build_prompt_with_subcategory(input_payload, subcategory)
    else:
        system_prompt, user_prompt = build_prompt(input_payload)
    
    # Enhance with persona context if available
    if persona_id and PERSONAS_AVAILABLE:
        try:
            selector = PersonaSelector()
            persona_context = selector.get_persona_prompt_context(persona_id)
            
            # Add persona context to system prompt
            system_prompt += f"\n\n{persona_context}"
            
            # Update input_payload meta to include persona info
            if "meta" not in input_payload:
                input_payload["meta"] = {}
            input_payload["meta"]["selected_persona"] = persona_id
            
            logger.info(f"Enhanced prompts with persona: {persona_id}")
            
        except Exception as e:
            logger.warning(f"Failed to enhance prompts with persona {persona_id}: {e}")
    
    return system_prompt, user_prompt
