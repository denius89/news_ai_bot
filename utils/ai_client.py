# utils/ai_client.py
import logging
import openai
from config.settings import OPENAI_API_KEY, AI_MODEL_SUMMARY, AI_MAX_TOKENS

logger = logging.getLogger("ai_client")

# Настройка ключа
openai.api_key = OPENAI_API_KEY


def ask(prompt: str, model: str = None, max_tokens: int = None) -> str:
    """
    Универсальная функция для обращения к OpenAI ChatCompletion.
    """
    if not prompt.strip():
        raise ValueError("❌ Пустой prompt для AI запроса")

    model = model or AI_MODEL_SUMMARY
    max_tokens = max_tokens or AI_MAX_TOKENS

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        content = resp["choices"][0]["message"]["content"].strip()
        logger.debug("AI response (model=%s): %s", model, content[:200])
        return content
    except Exception as e:
        logger.exception("❌ Ошибка в запросе к OpenAI")
        raise e
