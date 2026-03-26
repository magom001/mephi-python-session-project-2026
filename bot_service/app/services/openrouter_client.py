"""Клиент для взаимодействия с OpenRouter API."""

import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    """Отправляет запрос к LLM через OpenRouter и возвращает текст ответа.

    Args:
        prompt: Текстовый запрос пользователя.

    Returns:
        Текст ответа LLM.

    Raises:
        RuntimeError: При ошибке API или неожиданном формате ответа.
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
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from exc
