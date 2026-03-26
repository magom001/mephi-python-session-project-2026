"""Модуль ORM-моделей Auth Service."""

import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Модель пользователя.

    Attributes:
        id: Уникальный идентификатор пользователя.
        email: Электронная почта (уникальное поле).
        password_hash: Безопасный хеш пароля (bcrypt).
        role: Роль пользователя (по умолчанию 'user').
        created_at: Дата и время создания записи.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="user")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
