from __future__ import annotations

from neuro_core.providers import ProviderDescriptor


class ProviderRegistry:
    def __init__(self, providers: list[ProviderDescriptor]) -> None:
        self._providers = {provider.provider: provider for provider in providers}

    @classmethod
    def default(cls) -> "ProviderRegistry":
        return cls(
            providers=[
                ProviderDescriptor(
                    provider="anthropic",
                    display_name="Claude / Anthropic",
                    transport="anthropic_messages",
                    env_var="ANTHROPIC_API_KEY",
                    route_path="/v1/llm/providers/anthropic/chat",
                ),
                ProviderDescriptor(
                    provider="local",
                    display_name="Local OpenAI-Compatible",
                    transport="openai_compatible",
                    base_url="http://localhost:11434/v1",
                    env_var=None,
                    route_path="/v1/llm/providers/local/chat",
                ),
                ProviderDescriptor(
                    provider="openai",
                    display_name="OpenAI",
                    transport="openai_responses",
                    env_var="OPENAI_API_KEY",
                    route_path="/v1/llm/providers/openai/chat",
                ),
                ProviderDescriptor(
                    provider="openrouter",
                    display_name="OpenRouter",
                    transport="openai_compatible",
                    base_url="https://openrouter.ai/api/v1",
                    env_var="OPENROUTER_API_KEY",
                    route_path="/v1/llm/providers/openrouter/chat",
                ),
            ]
        )

    def get(self, provider_name: str) -> ProviderDescriptor:
        return self._providers[provider_name]

    def list(self) -> list[ProviderDescriptor]:
        return [self._providers[name] for name in self.provider_names()]

    def provider_names(self) -> list[str]:
        return sorted(self._providers.keys())

