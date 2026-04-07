from __future__ import annotations

from pydantic import BaseModel

from neuro_llm.settings import ProviderSettings


class RoutingRequest(BaseModel):
    task_type: str
    quality: str = "balanced"
    provider: str | None = None
    model: str | None = None


class RouteSelection(BaseModel):
    task_type: str
    quality: str
    provider: str
    model: str
    rationale: str


class PromptRoutingPolicy:
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings

    def select_route(self, request: RoutingRequest) -> RouteSelection:
        if request.provider and request.model:
            return RouteSelection(
                task_type=request.task_type,
                quality=request.quality,
                provider=request.provider,
                model=request.model,
                rationale="Explicit provider/model override supplied by caller.",
            )

        if request.quality == "local":
            return RouteSelection(
                task_type=request.task_type,
                quality=request.quality,
                provider=self.settings.default_local_provider,
                model=self.settings.default_local_model,
                rationale="Local route requested explicitly.",
            )

        if request.quality == "high" or request.task_type in {"revision", "heavy_reasoning"}:
            return RouteSelection(
                task_type=request.task_type,
                quality=request.quality,
                provider=self.settings.default_heavy_provider,
                model=self.settings.default_heavy_model,
                rationale="High-quality or revision task routed to heavy model path.",
            )

        return RouteSelection(
            task_type=request.task_type,
            quality=request.quality,
            provider=self.settings.default_analysis_provider,
            model=self.settings.default_analysis_model,
            rationale="Balanced analysis path uses the default analysis provider.",
        )

