from __future__ import annotations

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    template_id: str
    task_type: str
    version: str
    system_prompt: str
    user_prompt_template: str


class RenderedPrompt(BaseModel):
    template_id: str
    task_type: str
    version: str
    system_prompt: str
    user_prompt: str


class PromptRegistry:
    def __init__(self, templates: list[PromptTemplate]) -> None:
        self._templates = {template.task_type: template for template in templates}

    @classmethod
    def default(cls) -> "PromptRegistry":
        version = "2026-04-04"
        return cls(
            templates=[
                PromptTemplate(
                    template_id="prompt_analysis_v1",
                    task_type="analysis",
                    version=version,
                    system_prompt=(
                        "You are a neuro-informed creative analyst. Work from evidence, "
                        "keep uncertainty explicit, and avoid fake psychological certainty."
                    ),
                    user_prompt_template=(
                        "Content:\n{content}\n\nAudience:\n{audience_summary}\n\n"
                        "Target goals:\n{target_goals}"
                    ),
                ),
                PromptTemplate(
                    template_id="prompt_revision_v1",
                    task_type="revision",
                    version=version,
                    system_prompt=(
                        "You are a revision engine. Produce concrete edits tied to scored "
                        "weaknesses and target deltas."
                    ),
                    user_prompt_template=(
                        "Original content:\n{content}\n\nAudience:\n{audience_summary}\n\n"
                        "Target goals:\n{target_goals}\n\nWeakness summary:\n{weakness_summary}"
                    ),
                ),
                PromptTemplate(
                    template_id="prompt_variant_generation_v1",
                    task_type="variant_generation",
                    version=version,
                    system_prompt=(
                        "You are an optimization writer. Produce a stronger variant that follows "
                        "the revision instructions while preserving the core message."
                    ),
                    user_prompt_template=(
                        "Original content:\n{content}\n\nInstructions:\n{instructions}\n\n"
                        "Audience:\n{audience_summary}\n\nVariant angle:\n{variant_angle}"
                    ),
                ),
            ]
        )

    def render(self, task_type: str, variables: dict[str, str]) -> RenderedPrompt:
        template = self._templates[task_type]
        return RenderedPrompt(
            template_id=template.template_id,
            task_type=template.task_type,
            version=template.version,
            system_prompt=template.system_prompt,
            user_prompt=template.user_prompt_template.format(**variables),
        )
