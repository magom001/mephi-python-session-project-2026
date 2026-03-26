"""Обработчики Telegram-сообщений.

Реализует команды /start, /token и обработку текстовых сообщений.
"""

import logging

from aiogram import Router, types
from aiogram.filters import Command

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Обработчик команды /start. Приветствует пользователя и описывает порядок работы."""
    await message.answer(
        "Это бот с доступом к большой языковой модели по JWT-токену.\n"
        "Сначала отправьте токен командой: /token <JWT>\n"
        "Потом просто напишите вопрос и я с удовольствием отвечу!"
    )


@router.message(Command("token"))
async def cmd_token(message: types.Message) -> None:
    """Обработчик команды /token <JWT>.

    Валидирует токен и сохраняет его в Redis под ключом token:<tg_user_id>.
    """
    if message.text is None:
        await message.answer("Пожалуйста, укажите токен: /token <JWT>")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пожалуйста, укажите токен: /token <JWT>")
        return

    token = parts[1].strip()

    # Validate token before saving
    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Токен невалиден. Пожалуйста, получите новый токен в Auth Service."
        )
        return

    user_id = message.from_user.id  # type: ignore[union-attr]
    redis = get_redis()
    try:
        await redis.set(f"token:{user_id}", token)
    finally:
        await redis.aclose()

    await message.answer("Токен сохранён. Теперь можно отправлять запросы модели.")


@router.message()
async def handle_text(message: types.Message) -> None:
    """Обработчик текстовых сообщений.

    Проверяет наличие и валидность JWT в Redis, отправляет задачу
    в Celery через RabbitMQ для обработки LLM-запроса.
    """
    user_id = message.from_user.id  # type: ignore[union-attr]
    chat_id = message.chat.id

    redis = get_redis()
    try:
        token = await redis.get(f"token:{user_id}")
    finally:
        await redis.aclose()

    if not token:
        await message.answer(
            "У вас нет сохранённого токена. "
            "Пожалуйста, авторизуйтесь в Auth Service и отправьте токен командой /token <JWT>"
        )
        return

    # Validate stored token
    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Ваш токен истёк или невалиден. "
            "Пожалуйста, получите новый токен в Auth Service и отправьте его командой /token <JWT>"
        )
        return

    prompt = message.text or ""
    if not prompt.strip():
        await message.answer("Пожалуйста, введите текстовый запрос.")
        return

    # Send task to Celery via RabbitMQ
    llm_request.delay(chat_id, prompt)

    await message.answer("Запрос принят. Ответ придёт следующим сообщением.")
