"""Зависимости FastAPI (Depends).

Реализует фабрики сессий, репозиториев, use-caseов и извлечение
текущего пользователя из JWT.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Фабрика асинхронных сессий БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UsersRepository:
    """Фабрика репозитория пользователей."""
    return UsersRepository(session)


async def get_auth_uc(
    repo: Annotated[UsersRepository, Depends(get_users_repo)],
) -> AuthUseCase:
    """Фабрика use-case аутентификации."""
    return AuthUseCase(repo)


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    """Извлекает идентификатор пользователя из JWT-токена.

    Декодирует токен из заголовка Authorization: Bearer ...,
    проверяет валидность и возвращает user_id.

    Args:
        token: JWT-токен из заголовка.

    Returns:
        Идентификатор пользователя.

    Raises:
        InvalidTokenError: Если токен невалиден.
        TokenExpiredError: Если токен истёк.
    """
    try:
        payload = decode_token(token)
    except ValueError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredError()
        raise InvalidTokenError()

    sub = payload.get("sub")
    if sub is None:
        raise InvalidTokenError()

    try:
        return int(sub)
    except (TypeError, ValueError):
        raise InvalidTokenError()
