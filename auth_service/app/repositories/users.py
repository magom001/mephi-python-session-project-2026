"""Репозиторий доступа к пользователям.

Реализует операции уровня БД: чтение и создание пользователей.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UsersRepository:
    """Репозиторий для работы с таблицей пользователей.

    Репозиторий не содержит бизнес-логики и не выбрасывает HTTP-исключения.
    Возвращает данные или None.
    """
    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Получает пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Объект User или None, если не найден.
        """
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Получает пользователя по email.

        Args:
            email: Электронная почта.

        Returns:
            Объект User или None, если не найден.
        """
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        """Создаёт нового пользователя в базе данных.

        Args:
            email: Электронная почта.
            password_hash: Хеш пароля.
            role: Роль пользователя (по умолчанию 'user').

        Returns:
            Созданный объект User.
        """
        user = User(email=email, password_hash=password_hash, role=role)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
