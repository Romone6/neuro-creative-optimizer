from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest
from neuro_analysis.revision import RevisionService
from neuro_analysis.variants import VariantGenerationService
from neuro_core.llm import ChatExecutionResponse
from neuro_prompts.policy import RouteSelection


def test_variant_generation_service_uses_llm_route_when_available() -> None:
    analysis_service = AnalysisService()
    revision_service = RevisionService()
    analysis_result = analysis_service.analyze_text(
        TextAnalysisRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
            },
        )
    )
    revision_plan = revision_service.build_plan(
        asset=analysis_result.asset,
        analysis_run=analysis_result.analysis_run,
        audience_profile=analysis_result.audience_profile,
    )

    class FakeProviderService:
        def __init__(self) -> None:
            self.calls = 0

        def execute(self, request):
            self.calls += 1
            return ChatExecutionResponse(
                provider=request.provider,
                model=request.model,
                output_text=f"LLM variant {self.calls}",
                finish_reason="stop",
                transport="openai_compatible",
                raw_response=None,
            )

    class FakePromptRegistry:
        def render(self, task_type, variables):
            return type(
                "RenderedPrompt",
                (),
                {
                    "system_prompt": f"system::{task_type}",
                    "user_prompt": f"user::{variables['content']}",
                    "version": "2026-04-04",
                    "template_id": "prompt_variant_v1",
                },
            )()

    class FakePolicy:
        def select_route(self, request):
            return RouteSelection(
                task_type=request.task_type,
                quality=request.quality,
                provider="local",
                model="llama3.1",
                rationale="test route",
            )

    service = VariantGenerationService(
        provider_service=FakeProviderService(),
        prompt_registry=FakePromptRegistry(),
        prompt_policy=FakePolicy(),
    )

    variants = service.generate_variants(
        asset=analysis_result.asset,
        revision_plan=revision_plan,
    )

    assert [variant.body for variant in variants] == ["LLM variant 1", "LLM variant 2", "LLM variant 3"]
    assert all(variant.provider == "local" for variant in variants)
    assert all(variant.model_name == "llama3.1" for variant in variants)

