"""Модуль получения Redis-клиента."""

import redis.asyncio as aioredis

from app.core.config import settings


def get_redis() -> aioredis.Redis:
    """Создаёт и возвращает Redis-клиент на основе настроек."""
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)
