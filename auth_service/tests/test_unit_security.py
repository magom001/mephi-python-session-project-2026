from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_not_equal_to_plain(self) -> None:
        password = "my_secure_password"
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_correct_password(self) -> None:
        password = "my_secure_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    def test_create_and_decode_token(self) -> None:
        token = create_access_token(sub="42", role="user")
        payload = decode_token(token)

        assert payload["sub"] == "42"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload

    def test_decode_invalid_token_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            decode_token("totally.invalid.token")

    def test_token_with_admin_role(self) -> None:
        token = create_access_token(sub="1", role="admin")
        payload = decode_token(token)
        assert payload["role"] == "admin"
        assert payload["sub"] == "1"
