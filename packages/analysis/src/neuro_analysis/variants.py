from __future__ import annotations

from hashlib import sha1

from neuro_core import ChatExecutionRequest, ChatMessage
from neuro_llm import ProviderExecutionError
from neuro_prompts import PromptRegistry, PromptRoutingPolicy, RoutingRequest
from neuro_core import ArtifactLineage, RevisionPlan, VariantAsset


class VariantGenerationService:
    def __init__(
        self,
        provider_service=None,
        prompt_registry: PromptRegistry | None = None,
        prompt_policy: PromptRoutingPolicy | None = None,
    ) -> None:
        self.provider_service = provider_service
        self.prompt_registry = prompt_registry
        self.prompt_policy = prompt_policy

    def generate_variants(self, asset, revision_plan: RevisionPlan) -> list[VariantAsset]:
        instructions = revision_plan.instructions
        strategies = ["credible", "clear", "urgent"]
        variant_bodies: list[tuple[str, str | None, str | None]] = []
        for strategy in strategies:
            llm_body, provider, model_name = self._try_generate_with_llm(
                asset=asset,
                revision_plan=revision_plan,
                strategy=strategy,
            )
            if llm_body is None:
                llm_body = self._apply_variant_strategy(asset.body, instructions, strategy=strategy)
            variant_bodies.append((llm_body, provider, model_name))
        return [
            VariantAsset(
                variant_id=self._stable_id("variant", revision_plan.revision_plan_id, index),
                source_asset_id=asset.asset_id,
                revision_plan_id=revision_plan.revision_plan_id,
                provider=provider,
                model_name=model_name,
                body=body,
                diff_summary=summary,
                applied_instruction_ids=[instruction.instruction_id for instruction in instructions[:2]],
                lineage=ArtifactLineage(
                    source_project_id=asset.project_id,
                    source_asset_id=asset.asset_id,
                    source_revision_plan_id=revision_plan.revision_plan_id,
                ),
            )
            for index, ((body, provider, model_name), summary) in enumerate(
                [
                    (
                        variant_bodies[0],
                        "Strengthened trust with more concrete proof and steadier tone.",
                    ),
                    (
                        variant_bodies[1],
                        "Improved clarity by simplifying phrasing and making the promise more explicit.",
                    ),
                    (
                        variant_bodies[2],
                        "Raised urgency by tightening the call to action and sharpening the close.",
                    ),
                ],
                start=1,
            )
        ]

    def _apply_variant_strategy(self, body: str, instructions, strategy: str) -> str:
        base = " ".join(part.strip() for part in body.splitlines() if part.strip())
        if strategy == "credible":
            return (
                f"{base} Here is the concrete promise, stated plainly and with credible specificity."
            )
        if strategy == "clear":
            return (
                f"{base} In plain terms: this is the direct benefit and the reason to believe it."
            )
        return (
            f"{base} Take the next step now while the opportunity is still current and easy to act on."
        )

    def _try_generate_with_llm(self, asset, revision_plan: RevisionPlan, strategy: str) -> tuple[str | None, str | None, str | None]:
        if self.provider_service is None or self.prompt_registry is None or self.prompt_policy is None:
            return None, None, None

        rendered = self.prompt_registry.render(
            task_type="variant_generation",
            variables={
                "content": asset.body,
                "instructions": "\n".join(
                    f"- {instruction.dimension}: {instruction.prompt}" for instruction in revision_plan.instructions
                ),
                "audience_summary": ", ".join(goal.dimension for goal in revision_plan.target_goals) or "general audience",
                "variant_angle": strategy,
            },
        )
        route = self.prompt_policy.select_route(
            RoutingRequest(task_type="variant_generation", quality="balanced")
        )
        try:
            response = self.provider_service.execute(
                ChatExecutionRequest(
                    provider=route.provider,
                    model=route.model,
                    messages=[
                        ChatMessage(role="system", content=rendered.system_prompt),
                        ChatMessage(role="user", content=rendered.user_prompt),
                    ],
                )
            )
            body = response.output_text.strip()
            return (body or None), response.provider, response.model
        except ProviderExecutionError:
            return None, None, None

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
