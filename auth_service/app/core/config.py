"""Модуль конфигурации Auth Service.

Читает переменные окружения и формирует единый объект настроек приложения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения Auth Service.

    Загружает параметры из переменных окружения и .env-файла.
    Содержит настройки JWT, базы данных и общие параметры приложения.
    """
    APP_NAME: str = "auth-service"
    ENV: str = "local"

    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SQLITE_PATH: str = "./auth.db"

    @property
    def database_url(self) -> str:
        """Формирует строку подключения к базе данных на основе SQLITE_PATH."""
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
