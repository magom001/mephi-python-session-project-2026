import httpx
import pytest
import respx

from app.services.openrouter_client import call_openrouter


class TestOpenRouterClient:
    @respx.mock
    async def test_successful_response(self) -> None:
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Лев Толстой родился в 1828 году."
                    }
                }
            ]
        }
        respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await call_openrouter("Когда родился Толстой?")
        assert result == "Лев Толстой родился в 1828 году."

    @respx.mock
    async def test_api_error(self) -> None:
        respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="OpenRouter API error"):
            await call_openrouter("test prompt")

    @respx.mock
    async def test_malformed_response(self) -> None:
        respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={"unexpected": "format"})
        )

        with pytest.raises(RuntimeError, match="Unexpected"):
            await call_openrouter("test prompt")
