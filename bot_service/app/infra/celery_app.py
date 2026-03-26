"""Настройка Celery-приложения.

RabbitMQ используется как брокер, Redis — как backend результатов.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.llm_tasks as _llm_tasks  # noqa: E402, F401  # явный импорт для регистрации задач
