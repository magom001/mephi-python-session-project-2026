"""Схемы Pydantic для аутентификации."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию пользователя.

    Attributes:
        email: Электронная почта пользователя.
        password: Пароль в открытом виде.
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с JWT-токеном.

    Attributes:
        access_token: JWT access-токен.
        token_type: Тип токена (всегда 'bearer').
    """
    access_token: str
    token_type: str = "bearer"
