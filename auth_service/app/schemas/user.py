"""Публичные схемы пользователя."""

import datetime

from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    """Публичное представление пользователя (без password_hash).

    Attributes:
        id: Идентификатор пользователя.
        email: Электронная почта.
        role: Роль пользователя.
        created_at: Дата и время регистрации.
    """
    id: int
    email: EmailStr
    role: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
