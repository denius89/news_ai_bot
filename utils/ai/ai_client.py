# utils/ai_client.py
import logging
import asyncio
import sys
import os
from openai import OpenAI
from config.core.settings import OPENAI_API_KEY, AI_MODEL_SUMMARY, AI_MAX_TOKENS

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger("ai_client")

# Настройка клиента OpenAI (новая версия API)
client = OpenAI(api_key=OPENAI_API_KEY)


def ask(prompt: str, model: str = None, max_tokens: int = None) -> str:
    """
    Универсальная функция для обращения к OpenAI ChatCompletion.
    """
    if not prompt.strip():
        raise ValueError("❌ Пустой prompt для AI запроса")

    model = model or AI_MODEL_SUMMARY
    max_tokens = max_tokens or AI_MAX_TOKENS

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        content = resp.choices[0].message.content.strip()
        logger.debug("AI response (model=%s): %s", model, content[:200])
        return content
    except Exception as e:
        logger.exception("❌ Ошибка в запросе к OpenAI")
        raise e


async def ask_async(prompt: str, model: str = None, max_tokens: int = None, style: str = "analytical") -> str:
    """
    Асинхронная функция для обращения к OpenAI ChatCompletion.
    """
    if not prompt.strip():
        raise ValueError("❌ Пустой prompt для AI запроса")

    model = model or AI_MODEL_SUMMARY
    max_tokens = max_tokens or AI_MAX_TOKENS

    # Temperature based on style
    temps = {"analytical": 0.3, "business": 0.5, "meme": 0.8}
    temperature = temps.get(style, 0.7)

    try:
        # Run in thread pool to avoid blocking with timeout
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                ),
            ),
            timeout=30.0,  # 30 seconds timeout
        )
        content = response.choices[0].message.content.strip()
        logger.debug("AI response (model=%s, style=%s): %s", model, style, content[:200])
        return content
    except asyncio.TimeoutError:
        logger.exception("❌ OpenAI API timeout (>30s)")
        raise
    except Exception as e:
        logger.exception("❌ Ошибка в асинхронном запросе к OpenAI")
        raise e
