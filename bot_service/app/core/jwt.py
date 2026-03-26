"""Модуль проверки JWT-токенов в Bot Service.

Токены в Bot Service не создаются — только валидируются.
"""

from jose import JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    """Декодирует и валидирует JWT-токен.

    Проверяет подпись, срок действия и наличие поля sub.

    Args:
        token: JWT-токен в виде строки.

    Returns:
        Словарь с payload токена.

    Raises:
        ValueError: Если токен невалиден, истёк или не содержит sub.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc

    if "sub" not in payload:
        raise ValueError("Token missing 'sub' claim")

    return payload
