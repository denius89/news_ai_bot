"""
Multi-stage Digest Generator with Chain-of-Thought reasoning.

This module implements a 5-stage generation process:
0. Reasoning (Chain-of-Thought)
1. Fact extraction
2. Outline creation
3. Text generation
4. Editing and refinement
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.news import NewsItem
from utils.ai.ai_client import ask_async

try:
    from digests.rag_system import get_rag_context

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logger = logging.getLogger(__name__)


class MultiStageGenerator:
    """5-stage digest generation with Chain-of-Thought reasoning."""

    def __init__(self):
        self.stage_logs = []

    async def generate(
        self,
        news_items: List[NewsItem],
        category: str,
        subcategory: Optional[str] = None,
        style: str = "analytical",
        events: Optional[List[Dict[str, Any]]] = None,
        use_reasoning: bool = True,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """Генерация через 5 этапов с Chain-of-Thought."""

        start_time = datetime.utcnow()
        logger.info(f"Starting multi-stage generation for {category}/{subcategory}")

        # Stage 0: Chain-of-Thought reasoning
        reasoning = None
        if use_reasoning:
            reasoning = await self._reason_about_news(news_items, category, subcategory, events, use_rag)
            logger.info("Stage 0: Reasoning completed")

        # Stage 1: Extract facts
        facts = await self._extract_facts(news_items, events, reasoning)
        logger.info(f"Stage 1: Extracted {len(facts)} facts")

        # Stage 2: Create outline
        outline = await self._create_outline(facts, category, subcategory, reasoning)
        logger.info("Stage 2: Outline created")

        # Stage 3: Generate text
        text = await self._generate_text(facts, outline, category, subcategory, style, reasoning)
        logger.info("Stage 3: Text generated")

        # Stage 4: Edit and refine
        final_text = await self._edit_text(text, facts, outline, category, subcategory)
        logger.info("Stage 4: Text refined")

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        return {
            "text": final_text,
            "reasoning": reasoning,
            "facts": facts,
            "outline": outline,
            "stats": {
                "stages": 5,
                "facts_count": len(facts),
                "word_count": len(final_text.split()),
                "generation_time_sec": duration,
            },
            "stage_logs": self.stage_logs,
        }

    async def _reason_about_news(
        self,
        news_items: List[NewsItem],
        category: str,
        subcategory: Optional[str],
        events: Optional[List[Dict[str, Any]]] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """Stage 0: Chain-of-Thought reasoning."""

        news_text = "\n\n".join(
            [f"{i+1}. {item.title}: {(item.content or '')[:200]}..." for i, item in enumerate(news_items)]
        )

        events_text = ""
        if events:
            events_text = "\n\nПРЕДСТОЯЩИЕ СОБЫТИЯ:\n" + "\n".join(
                [f"• {e['title']} ({e['date']})" for e in events[:3]]  # Limit events for reasoning
            )

        subcategory_context = f"/{subcategory}" if subcategory else ""

        # Добавляем RAG контекст если доступен
        rag_context = ""
        if use_rag and RAG_AVAILABLE:
            try:
                rag_context = get_rag_context(
                    category=category,
                    subcategory=subcategory,
                    style="analytical",
                    news_items=news_items,
                    max_samples=2,  # Меньше для reasoning этапа
                )
                if rag_context:
                    rag_context = (
                        "\n\n🎯 ПРИМЕРЫ ВЫСОКОКАЧЕСТВЕННЫХ ДАЙДЖЕСТОВ:\n"
                        + rag_context.split("ПРИМЕРЫ ВЫСОКОКАЧЕСТВЕННЫХ ДАЙДЖЕСТОВ:")[-1]
                        if "ПРИМЕРЫ ВЫСОКОКАЧЕСТВЕННЫХ ДАЙДЖЕСТОВ:" in rag_context
                        else rag_context
                    )
                    logger.info(f"Added RAG context to reasoning: {len(rag_context)} chars")
            except Exception as e:
                logger.warning(f"Failed to add RAG context to reasoning: {e}")

        prompt = f"""Проанализируй эти новости и подумай вслух.

КАТЕГОРИЯ: {category}{subcategory_context}
{rag_context}

НОВОСТИ:
{news_text}
{events_text}

РАЗМЫШЛЯЙ ПОШАГОВО:

1. ГЛАВНАЯ ТЕМА: Какая одна тема объединяет эти события в контексте {subcategory if subcategory else category}?

2. ПРИЧИННО-СЛЕДСТВЕННЫЕ СВЯЗИ: Какие связи ты видишь между событиями?

3. КОНТЕКСТ: Как это связано с предстоящими событиями и трендами?

4. УГОЛ ЗРЕНИЯ: Какой подход будет наиболее интересен читателю?

5. МЕТАФОРЫ: Какие метафоры или аналогии можно использовать для объяснения?

6. ПРОГНОЗ: Что это значит для будущего в этой области?

Верни строго JSON без дополнительного текста:
{{
  "main_theme": "...",
  "connections": ["связь 1", "связь 2"],
  "context_links": ["контекст 1", "контекст 2"],
  "angle": "...",
  "metaphors": ["метафора 1", "метафора 2"],
  "forecast": "..."
}}"""

        try:
            response = await ask_async(prompt=prompt, style="analytical", max_tokens=800)

            if response and response.strip().startswith("{"):
                reasoning = json.loads(response.strip())
                self.stage_logs.append(
                    {"stage": 0, "name": "reasoning", "success": True, "output_length": len(response)}
                )
                return reasoning
            else:
                logger.warning("Failed to parse reasoning JSON")
        except Exception as e:
            logger.error(f"Reasoning stage failed: {e}")

        # Fallback reasoning
        return {
            "main_theme": "Обзор важных событий",
            "connections": ["временная связь событий"],
            "context_links": ["общий контекст"],
            "angle": "аналитический",
            "metaphors": [],
            "forecast": "продолжение трендов",
        }

    async def _extract_facts(
        self, news_items: List[NewsItem], events: Optional[List[Dict[str, Any]]], reasoning: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stage 1: Extract key facts from news items."""

        facts = []

        for item in news_items:
            fact = {
                "title": item.title,
                "content": item.content or "",
                "source": item.source or "Unknown",
                "importance": item.importance or 0.0,
                "credibility": item.credibility or 0.0,
                "published_at": item.published_at_fmt if item.published_at else "Unknown",
                "category": item.category,
                "subcategory": item.subcategory,
            }
            facts.append(fact)

        # Add event facts
        if events:
            for event in events[:5]:  # Limit events
                fact = {
                    "title": event["title"],
                    "content": f"Событие: {event.get('description', '')}",
                    "source": "Events",
                    "importance": event.get("importance", 0.7),
                    "credibility": 0.9,  # Events are high credibility
                    "published_at": event.get("date", "Unknown"),
                    "category": "event",
                    "subcategory": event.get("subcategory", ""),
                }
                facts.append(fact)

        # Add reasoning insights as facts
        if reasoning and reasoning.get("context_links"):
            for link in reasoning["context_links"][:2]:
                fact = {
                    "title": "Контекстный анализ",
                    "content": link,
                    "source": "AI Reasoning",
                    "importance": 0.6,
                    "credibility": 0.8,
                    "published_at": "Analysis",
                    "category": "context",
                    "subcategory": "",
                }
                facts.append(fact)

        self.stage_logs.append({"stage": 1, "name": "extract_facts", "success": True, "facts_count": len(facts)})

        return facts

    async def _create_outline(
        self,
        facts: List[Dict[str, Any]],
        category: str,
        subcategory: Optional[str],
        reasoning: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Stage 2: Create structured outline."""

        main_theme = reasoning.get("main_theme", "Обзор событий") if reasoning else "Обзор событий"
        angle = reasoning.get("angle", "аналитический") if reasoning else "аналитический"

        prompt = f"""Создай структуру дайджеста на основе фактов и анализа.

ТЕМА: {main_theme}
УГОЛ: {angle}
КАТЕГОРИЯ: {category}/{subcategory if subcategory else 'general'}

ФАКТЫ ({len(facts)}):
{chr(10).join([f"- {fact['title']}: {fact['content'][:100]}..." for fact in facts[:5]])}

СОЗДАЙ СТРУКТУРУ JSON:
{{
  "title": "заголовок (5-8 слов)",
  "dek": "подзаголовок (10-15 слов)",
  "sections": [
    {{
      "heading": "заголовок раздела",
      "purpose": "что рассказывает",
      "facts": [индексы фактов 0-4],
      "order": 1
    }}
  ],
  "conclusion": "что ожидать дальше"
}}"""

        try:
            response = await ask_async(prompt=prompt, style="analytical", max_tokens=600)

            if response and response.strip().startswith("{"):
                outline = json.loads(response.strip())
                self.stage_logs.append(
                    {
                        "stage": 2,
                        "name": "create_outline",
                        "success": True,
                        "sections_count": len(outline.get("sections", [])),
                    }
                )
                return outline
        except Exception as e:
            logger.error(f"Outline creation failed: {e}")

        # Fallback outline
        outline = {
            "title": f"Дайджест {category}",
            "dek": "Обзор важных событий",
            "sections": [
                {
                    "heading": "Основные события",
                    "purpose": "рассказывает о ключевых новостях",
                    "facts": list(range(min(3, len(facts)))),
                    "order": 1,
                }
            ],
            "conclusion": "События развиваются по текущему сценарию",
        }

        return outline

    async def _generate_text(
        self,
        facts: List[Dict[str, Any]],
        outline: Dict[str, Any],
        category: str,
        subcategory: Optional[str],
        style: str,
        reasoning: Optional[Dict[str, Any]],
    ) -> str:
        """Stage 3: Generate full text based on outline and facts."""

        # Prepare facts text
        facts_text = "\n\n".join(
            [f"ФАКТ {i}: {fact['title']}\n{fact['content'][:300]}..." for i, fact in enumerate(facts)]
        )

        # Prepare reasoning context
        reasoning_context = ""
        if reasoning:
            reasoning_context = f"""
АНАЛИЗ И РАССУЖДЕНИЯ:
- Главная тема: {reasoning.get('main_theme', '')}
- Связи: {', '.join(reasoning.get('connections', []))}
- Метафоры: {', '.join(reasoning.get('metaphors', []))}
- Прогноз: {reasoning.get('forecast', '')}
"""

        prompt = f"""Создай дайджест на основе структуры и фактов.

СТРУКТУРА:
Заголовок: {outline.get('title', '')}
Подзаголовок: {outline.get('dek', '')}

Разделы:
{chr(10).join([f"- {section['heading']}: {section['purpose']}" for section in outline.get('sections', [])])}

{reasoning_context}

ФАКТЫ:
{facts_text}

СТИЛЬ: {style}
КАТЕГОРИЯ: {category}/{subcategory if subcategory else 'general'}

ТРЕБОВАНИЯ:
- Используй связное повествование
- Покажи связи между событиями
- Добавь контекст и анализ
- Пиши увлекательно и информативно
- Длина: 400-800 слов

Создай готовый дайджест в HTML формате (без <html>, <body> тегов)."""

        try:
            response = await ask_async(prompt=prompt, style=style, max_tokens=1500)

            if response:
                self.stage_logs.append(
                    {"stage": 3, "name": "generate_text", "success": True, "output_length": len(response)}
                )
                return response

        except Exception as e:
            logger.error(f"Text generation failed: {e}")

        # Fallback text
        return f"<b>{outline.get('title', 'Дайджест')}</b>\n\nАнализ событий в процессе обработки."

    async def _edit_text(
        self, text: str, facts: List[Dict[str, Any]], outline: Dict[str, Any], category: str, subcategory: Optional[str]
    ) -> str:
        """Stage 4: Edit and refine the generated text."""

        prompt = f"""Отредактируй и улучши этот дайджест.

ИСХОДНЫЙ ТЕКСТ:
{text}

ЗАДАЧИ РЕДАКТУРЫ:
1. Проверь факты на соответствие источникам
2. Улучши стиль и читабельность
3. Добавь недостающие связи между событиями
4. Убери повторы и улучши структуру
5. Сделай текст более увлекательным

СТИЛЬ РЕДАКТУРЫ:
- Сохрани основную информацию
- Улучши формулировки
- Добавь плавные переходы
- Проверь логику изложения

Верни улучшенный текст в том же формате."""

        try:
            response = await ask_async(prompt=prompt, style="analytical", max_tokens=1200)

            if response and len(response.strip()) > 100:  # Reasonable minimum
                self.stage_logs.append(
                    {"stage": 4, "name": "edit_text", "success": True, "improvements": len(response) - len(text)}
                )
                return response

        except Exception as e:
            logger.error(f"Text editing failed: {e}")

        # Return original text if editing fails
        return text


# Convenience function
async def generate_multistage_digest(
    news_items: List[NewsItem],
    category: str,
    subcategory: Optional[str] = None,
    style: str = "analytical",
    events: Optional[List[Dict[str, Any]]] = None,
    use_reasoning: bool = True,
    use_rag: bool = True,
) -> Dict[str, Any]:
    """Generate digest using multi-stage approach."""

    generator = MultiStageGenerator()
    return await generator.generate(
        news_items=news_items,
        category=category,
        subcategory=subcategory,
        style=style,
        events=events,
        use_reasoning=use_reasoning,
        use_rag=use_rag,
    )
