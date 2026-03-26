"""Модуль безопасности Auth Service.

Реализует хеширование паролей через bcrypt, а также создание и декодирование JWT-токенов.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt.

    Args:
        password: Исходный пароль в виде строки.

    Returns:
        Хеш пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хеш пароля из базы данных.

    Returns:
        True, если пароль совпадает; False — в противном случае.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(sub: str, role: str) -> str:
    """Создаёт JWT access-токен.

    Токен содержит поля sub, role, iat (время выпуска) и exp (время истечения).

    Args:
        sub: Идентификатор пользователя (строка).
        role: Роль пользователя (например, 'user' или 'admin').

    Returns:
        Подписанный JWT-токен в виде строки.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict:
    """Декодирует и валидирует JWT-токен.

    Проверяет подпись и срок действия токена.

    Args:
        token: JWT-токен в виде строки.

    Returns:
        Словарь с payload токена.

    Raises:
        ValueError: Если токен невалиден или истёк.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        return payload
    except JWTError as exc:
        raise ValueError(str(exc)) from exc
