from neuro_llm.settings import ProviderSettings
from neuro_prompts.policy import PromptRoutingPolicy, RoutingRequest
from neuro_prompts.registry import PromptRegistry


def test_prompt_registry_renders_analysis_template() -> None:
    registry = PromptRegistry.default()

    rendered = registry.render(
        task_type="analysis",
        variables={
            "content": "Hello audience.",
            "audience_summary": "Cold traffic founders on linkedin",
            "target_goals": "clarity=0.9, trust=0.8",
        },
    )

    assert rendered.version == "2026-04-04"
    assert "Hello audience." in rendered.user_prompt
    assert "Cold traffic founders" in rendered.user_prompt


def test_prompt_routing_policy_uses_heavy_route_for_high_quality_tasks() -> None:
    policy = PromptRoutingPolicy(
        ProviderSettings(
            default_analysis_provider="openrouter",
            default_analysis_model="openrouter/auto",
            default_heavy_provider="openai",
            default_heavy_model="gpt-5",
            default_local_provider="local",
            default_local_model="llama3.1",
        )
    )

    route = policy.select_route(RoutingRequest(task_type="revision", quality="high"))

    assert route.provider == "openai"
    assert route.model == "gpt-5"


def test_prompt_routing_policy_uses_local_route_when_requested() -> None:
    policy = PromptRoutingPolicy(ProviderSettings())

    route = policy.select_route(RoutingRequest(task_type="analysis", quality="local"))

    assert route.provider == "local"
    assert route.model == "llama3.1"

