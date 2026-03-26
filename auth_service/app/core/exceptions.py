"""Модуль HTTP-исключений Auth Service.

Определяет иерархию исключений для обработки ошибок аутентификации и авторизации.
"""

from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение.

    Все доменные исключения наследуются от этого класса.
    Позволяет задавать status_code и detail на уровне класса.
    """
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь с таким email уже существует (409)."""

    status_code = 409
    detail = "User with this email already exists"


class InvalidCredentialsError(BaseHTTPException):
    """Неверный email или пароль (401)."""

    status_code = 401
    detail = "Invalid email or password"


class InvalidTokenError(BaseHTTPException):
    """Невалидный токен (401)."""

    status_code = 401
    detail = "Invalid token"


class TokenExpiredError(BaseHTTPException):
    """Токен истёк (401)."""

    status_code = 401
    detail = "Token has expired"


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден (404)."""

    status_code = 404
    detail = "User not found"


class PermissionDeniedError(BaseHTTPException):
    """Доступ запрещён (403)."""

    status_code = 403
    detail = "Permission denied"
