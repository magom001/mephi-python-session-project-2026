from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def _make_token(sub: str = "1", role: str = "user", expired: bool = False) -> str:
    now = datetime.now(timezone.utc)
    if expired:
        exp = now - timedelta(hours=1)
    else:
        exp = now + timedelta(hours=1)
    payload = {"sub": sub, "role": role, "iat": now, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class TestDecodeAndValidate:
    def test_valid_token(self) -> None:
        token = _make_token(sub="42", role="admin")
        payload = decode_and_validate(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_invalid_token_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate("garbage.string.here")

    def test_expired_token_raises(self) -> None:
        token = _make_token(expired=True)
        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate(token)

    def test_token_without_sub_raises(self) -> None:
        now = datetime.now(timezone.utc)
        payload = {"role": "user", "iat": now, "exp": now + timedelta(hours=1)}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        with pytest.raises(ValueError, match="sub"):
            decode_and_validate(token)
