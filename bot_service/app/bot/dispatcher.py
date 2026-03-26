"""Сборка Telegram-бота.

Создаёт Bot и Dispatcher, подключает обработчики.
"""

from aiogram import Bot, Dispatcher

from app.bot.handlers import router as handlers_router
from app.core.config import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
dp.include_router(handlers_router)
