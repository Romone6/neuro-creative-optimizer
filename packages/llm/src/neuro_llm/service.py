from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic
from openai import OpenAI

from neuro_core.llm import ChatExecutionRequest, ChatExecutionResponse
from neuro_llm.registry import ProviderRegistry
from neuro_llm.settings import ProviderSettings


@dataclass
class ProviderExecutionError(Exception):
    code: str
    message: str
    status_code: int

    def __str__(self) -> str:
        return self.message


class ProviderService:
    def __init__(self, registry: ProviderRegistry, settings: ProviderSettings) -> None:
        self.registry = registry
        self.settings = settings

    def execute(self, request: ChatExecutionRequest) -> ChatExecutionResponse:
        descriptor = self._get_descriptor(request.provider)

        if descriptor.provider == "anthropic":
            return self._execute_anthropic(request)
        if descriptor.transport == "openai_responses":
            return self._execute_openai_responses(request)
        if descriptor.transport == "openai_compatible":
            return self._execute_openai_compatible(request)

        raise ProviderExecutionError(
            code="provider_transport_unsupported",
            message=f"Unsupported provider transport: {descriptor.transport}",
            status_code=500,
        )

    def _get_descriptor(self, provider_name: str):
        if provider_name not in self.registry.provider_names():
            raise ProviderExecutionError(
                code="provider_unknown",
                message=f"Unknown provider: {provider_name}",
                status_code=404,
            )
        return self.registry.get(provider_name)

    def _execute_anthropic(self, request: ChatExecutionRequest) -> ChatExecutionResponse:
        api_key = self.settings.anthropic_api_key
        if not api_key:
            raise ProviderExecutionError(
                code="provider_credentials_missing",
                message="Missing ANTHROPIC_API_KEY for Anthropic provider",
                status_code=424,
            )

        client = Anthropic(api_key=api_key, base_url=self.settings.anthropic_base_url)
        response = client.messages.create(
            model=request.model,
            max_tokens=request.max_output_tokens or 1024,
            messages=[message.model_dump() for message in request.messages],
        )
        output_text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        return ChatExecutionResponse(
            provider=request.provider,
            model=request.model,
            output_text=output_text,
            finish_reason=getattr(response, "stop_reason", None),
            transport="anthropic_messages",
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
        )

    def _execute_openai_responses(self, request: ChatExecutionRequest) -> ChatExecutionResponse:
        api_key = self.settings.openai_api_key
        if not api_key:
            raise ProviderExecutionError(
                code="provider_credentials_missing",
                message="Missing OPENAI_API_KEY for OpenAI provider",
                status_code=424,
            )

        client = OpenAI(api_key=api_key, base_url=self.settings.openai_base_url)
        response = client.responses.create(
            model=request.model,
            input=[
                {
                    "role": message.role,
                    "content": [{"type": "input_text", "text": message.content}],
                }
                for message in request.messages
            ],
            max_output_tokens=request.max_output_tokens,
        )
        output_text = getattr(response, "output_text", "")
        return ChatExecutionResponse(
            provider=request.provider,
            model=request.model,
            output_text=output_text,
            finish_reason=None,
            transport="openai_responses",
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
        )

    def _execute_openai_compatible(self, request: ChatExecutionRequest) -> ChatExecutionResponse:
        client = self._build_openai_compatible_client(request.provider)
        response = client.chat.completions.create(
            model=request.model,
            messages=[message.model_dump() for message in request.messages],
        )
        choice = response.choices[0]
        return ChatExecutionResponse(
            provider=request.provider,
            model=request.model,
            output_text=choice.message.content or "",
            finish_reason=getattr(choice, "finish_reason", None),
            transport=self.registry.get(request.provider).transport,
            raw_response=_model_dump_if_available(response),
        )

    def _build_openai_compatible_client(self, provider_name: str) -> OpenAI:
        if provider_name == "local":
            local_api_key = self.settings.local_model_api_key or "local-dev"
            return OpenAI(
                api_key=local_api_key,
                base_url=self.settings.local_model_base_url,
            )

        if provider_name == "openrouter":
            if not self.settings.openrouter_api_key:
                raise ProviderExecutionError(
                    code="provider_credentials_missing",
                    message="Missing OPENROUTER_API_KEY for OpenRouter provider",
                    status_code=424,
                )
            return OpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url=self.settings.openrouter_base_url,
            )

        descriptor = self.registry.get(provider_name)
        raise ProviderExecutionError(
            code="provider_transport_unsupported",
            message=f"Provider {descriptor.provider} is not openai-compatible",
            status_code=500,
        )


def _model_dump_if_available(response: Any) -> dict | None:
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return None
