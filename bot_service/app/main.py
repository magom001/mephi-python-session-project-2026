"""Точка входа FastAPI-приложения Bot Service."""

from fastapi import FastAPI

app = FastAPI(title="Bot Service")


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}
