from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestRegister:
    async def test_register_success(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        resp = await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "other_password"},
        )
        assert resp.status_code == 409


class TestLogin:
    async def test_login_success(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        resp = await client.post(
            "/auth/login",
            data={"username": "magomadov@email.com", "password": "secret123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        resp = await client.post(
            "/auth/login",
            data={"username": "magomadov@email.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/auth/login",
            data={"username": "nobody@email.com", "password": "secret123"},
        )
        assert resp.status_code == 401


class TestMe:
    async def test_me_success(self, client: AsyncClient) -> None:
        reg_resp = await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        token = reg_resp.json()["access_token"]
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "magomadov@email.com"
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data

    async def test_me_no_token(self, client: AsyncClient) -> None:
        resp = await client.get("/auth/me")
        assert resp.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


class TestFullFlow:
    """Сквозной тест: register → login → me в одном сценарии."""

    async def test_register_then_login_then_me(self, client: AsyncClient) -> None:
        # 1. Регистрация
        reg_resp = await client.post(
            "/auth/register",
            json={"email": "magomadov@email.com", "password": "secret123"},
        )
        assert reg_resp.status_code == 201
        reg_token = reg_resp.json()["access_token"]
        assert reg_token

        # 2. Логин (form-data, OAuth2PasswordRequestForm)
        login_resp = await client.post(
            "/auth/login",
            data={"username": "magomadov@email.com", "password": "secret123"},
        )
        assert login_resp.status_code == 200
        login_token = login_resp.json()["access_token"]
        assert login_token

        # 3. Получение профиля по токену из логина
        me_resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == "magomadov@email.com"
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data
