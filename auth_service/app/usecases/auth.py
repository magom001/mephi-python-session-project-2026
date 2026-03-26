"""Бизнес-логика аутентификации и регистрации.

Реализует use-caseы: register, login, me.
"""

from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserPublic


class AuthUseCase:
    """Случаи использования для Auth Service.

    Отвечает за регистрацию, вход и получение профиля пользователя.
    Не содержит SQL-запросов — работает через репозиторий.
    """
    def __init__(self, users_repo: UsersRepository) -> None:
        """Инициализация use-case.

        Args:
            users_repo: Репозиторий пользователей.
        """
        self._users_repo = users_repo

    async def register(self, email: str, password: str) -> TokenResponse:
        """Регистрация нового пользователя.

        Создаёт пользователя в БД и возвращает JWT-токен.

        Args:
            email: Электронная почта.
            password: Пароль в открытом виде.

        Returns:
            TokenResponse с access_token.

        Raises:
            UserAlreadyExistsError: Если пользователь с таким email уже существует.
        """
        existing = await self._users_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        hashed = hash_password(password)
        user = await self._users_repo.create(email=email, password_hash=hashed)
        token = create_access_token(sub=str(user.id), role=user.role)
        return TokenResponse(access_token=token)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Аутентификация пользователя.

        Проверяет email и пароль, возвращает JWT-токен.

        Args:
            email: Электронная почта.
            password: Пароль в открытом виде.

        Returns:
            TokenResponse с access_token.

        Raises:
            InvalidCredentialsError: Если email не найден или пароль неверный.
        """
        user = await self._users_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(sub=str(user.id), role=user.role)
        return TokenResponse(access_token=token)

    async def me(self, user_id: int) -> UserPublic:
        """Получение профиля текущего пользователя.

        Args:
            user_id: Идентификатор пользователя из JWT.

        Returns:
            Публичный профиль пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
        """
        user = await self._users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)
