from neuro_llm.registry import ProviderRegistry


def test_default_registry_exposes_all_required_providers() -> None:
    registry = ProviderRegistry.default()

    assert registry.provider_names() == [
        "anthropic",
        "local",
        "openai",
        "openrouter",
    ]


def test_local_provider_is_openai_compatible() -> None:
    registry = ProviderRegistry.default()
    provider = registry.get("local")

    assert provider.provider == "local"
    assert provider.transport == "openai_compatible"
    assert provider.base_url == "http://localhost:11434/v1"

