import pytest

from neuro_core.llm import ChatExecutionRequest, ChatMessage
from neuro_llm.registry import ProviderRegistry
from neuro_llm.service import ProviderExecutionError, ProviderService
from neuro_llm.settings import ProviderSettings


def test_provider_service_requires_credentials_for_openai() -> None:
    service = ProviderService(
        registry=ProviderRegistry.default(),
        settings=ProviderSettings(),
    )

    with pytest.raises(ProviderExecutionError) as exc:
        service.execute(
            ChatExecutionRequest(
                provider="openai",
                model="gpt-5",
                messages=[ChatMessage(role="user", content="test")],
            )
        )

    assert exc.value.status_code == 424
    assert exc.value.code == "provider_credentials_missing"


def test_provider_service_executes_local_openai_compatible_request(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        choices = [
            type(
                "Choice",
                (),
                {
                    "message": type("Message", (), {"content": "local reply"})(),
                    "finish_reason": "stop",
                },
            )()
        ]

    class FakeCompletions:
        def create(self, **kwargs: object) -> FakeResponse:
            captured["create_kwargs"] = kwargs
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, **kwargs: object) -> None:
            captured["client_kwargs"] = kwargs
            self.chat = FakeChat()

    monkeypatch.setattr("neuro_llm.service.OpenAI", FakeOpenAI)

    service = ProviderService(
        registry=ProviderRegistry.default(),
        settings=ProviderSettings(local_model_base_url="http://localhost:9999/v1"),
    )

    response = service.execute(
        ChatExecutionRequest(
            provider="local",
            model="llama3.1",
            messages=[ChatMessage(role="user", content="test")],
        )
    )

    assert response.provider == "local"
    assert response.output_text == "local reply"
    assert captured["client_kwargs"] == {
        "api_key": "local-dev",
        "base_url": "http://localhost:9999/v1",
    }
    assert captured["create_kwargs"] == {
        "model": "llama3.1",
        "messages": [{"role": "user", "content": "test"}],
    }

