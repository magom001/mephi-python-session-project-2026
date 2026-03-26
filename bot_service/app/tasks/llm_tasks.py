"""Задачи Celery для обработки LLM-запросов."""

import asyncio
import logging

import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="llm_request", bind=True, max_retries=2)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:  # type: ignore[no-untyped-def]
    """Задача Celery: вызывает OpenRouter LLM и отправляет ответ пользователю в Telegram.

    Args:
        tg_chat_id: Идентификатор чата Telegram.
        prompt: Текстовый запрос пользователя.

    Returns:
        Текст ответа LLM.
    """
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_process_llm_request(tg_chat_id, prompt))
        return result
    except Exception as exc:
        logger.exception("LLM request failed for chat_id=%s", tg_chat_id)
        raise self.retry(exc=exc, countdown=5)
    finally:
        loop.close()


async def _process_llm_request(tg_chat_id: int, prompt: str) -> str:
    """Выполняет запрос к OpenRouter API и отправляет ответ через Telegram Bot API.

    Args:
        tg_chat_id: Идентификатор чата Telegram.
        prompt: Текстовый запрос пользователя.

    Returns:
        Текст ответа LLM.
    """
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter API error: {response.status_code} — {response.text}"
        )

    data = response.json()
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected response format: {data}") from exc

    # Send the answer back to the user via Telegram Bot API
    tg_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15.0) as client:
        await client.post(tg_url, json={"chat_id": tg_chat_id, "text": answer})

    return answer
