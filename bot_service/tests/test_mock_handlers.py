from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
from jose import jwt

from app.core.config import settings


def _make_valid_token(sub: str = "1") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": "user",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def _make_message(text: str, user_id: int = 12345, chat_id: int = 12345) -> MagicMock:
    """Create a mock aiogram Message."""
    message = MagicMock()
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.chat = MagicMock()
    message.chat.id = chat_id
    message.answer = AsyncMock()
    return message


class TestTokenHandler:
    @pytest.fixture(autouse=True)
    def _patch_redis(self):
        self.fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        with patch("app.bot.handlers.get_redis", return_value=self.fake_redis):
            yield

    async def test_save_valid_token(self) -> None:
        from app.bot.handlers import cmd_token

        token = _make_valid_token(sub="42")
        message = _make_message(f"/token {token}")

        await cmd_token(message)

        stored = await self.fake_redis.get("token:12345")
        assert stored == token
        message.answer.assert_called_once()
        assert "сохранён" in message.answer.call_args[0][0].lower()

    async def test_save_invalid_token(self) -> None:
        from app.bot.handlers import cmd_token

        message = _make_message("/token totally_invalid_token")

        await cmd_token(message)

        stored = await self.fake_redis.get("token:12345")
        assert stored is None
        message.answer.assert_called_once()
        assert "невалиден" in message.answer.call_args[0][0].lower()

    async def test_token_missing_argument(self) -> None:
        from app.bot.handlers import cmd_token

        message = _make_message("/token")

        await cmd_token(message)

        message.answer.assert_called_once()
        assert "укажите" in message.answer.call_args[0][0].lower()


class TestTextHandler:
    @pytest.fixture(autouse=True)
    def _patch_redis(self):
        self.fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        with patch("app.bot.handlers.get_redis", return_value=self.fake_redis):
            yield

    async def test_no_token_rejects(self) -> None:
        from app.bot.handlers import handle_text

        message = _make_message("Привет, бот!")

        await handle_text(message)

        message.answer.assert_called_once()
        assert "токен" in message.answer.call_args[0][0].lower()

    async def test_valid_token_sends_to_celery(self) -> None:
        from app.bot.handlers import handle_text

        token = _make_valid_token()
        await self.fake_redis.set("token:12345", token)

        message = _make_message("Расскажи про Python")

        with patch("app.bot.handlers.llm_request") as mock_task:
            mock_task.delay = MagicMock()
            await handle_text(message)

            mock_task.delay.assert_called_once_with(12345, "Расскажи про Python")

        message.answer.assert_called_once()
        assert "принят" in message.answer.call_args[0][0].lower()

    async def test_expired_token_rejects(self) -> None:
        from app.bot.handlers import handle_text

        now = datetime.now(timezone.utc)
        payload = {
            "sub": "1",
            "role": "user",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        }
        expired_token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG
        )
        await self.fake_redis.set("token:12345", expired_token)

        message = _make_message("Привет!")

        await handle_text(message)

        message.answer.assert_called_once()
        assert "истёк" in message.answer.call_args[0][0].lower() or \
               "невалиден" in message.answer.call_args[0][0].lower()


class TestStartHandler:
    async def test_start_command(self) -> None:
        from app.bot.handlers import cmd_start

        message = _make_message("/start")
        await cmd_start(message)
        message.answer.assert_called_once()
        assert "токен" in message.answer.call_args[0][0].lower()
