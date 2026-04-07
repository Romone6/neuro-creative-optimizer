from __future__ import annotations

from hashlib import sha1

from pydantic import BaseModel

from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest, TextAnalysisResult
from neuro_analysis.revision import RevisionService
from neuro_analysis.variants import VariantGenerationService
from neuro_core import (
    ArtifactLineage,
    OptimizationReport,
    OptimizationRun,
    VariantComparison,
    VariantRanking,
)


class TextOptimizationRequest(BaseModel):
    project_id: str
    content_type: str
    body: str
    title: str | None = None
    audience: dict


class TextOptimizationResult(BaseModel):
    original_analysis: TextAnalysisResult
    optimization_run: OptimizationRun
    revision_plan: object
    variants: list[object]
    variant_analyses: list[TextAnalysisResult]
    variant_rankings: list[VariantRanking]
    optimization_report: OptimizationReport


class OptimizationService:
    def __init__(
        self,
        analysis_service: AnalysisService | None = None,
        revision_service: RevisionService | None = None,
        variant_generation_service: VariantGenerationService | None = None,
    ) -> None:
        self.analysis_service = analysis_service or AnalysisService()
        self.revision_service = revision_service or RevisionService()
        self.variant_generation_service = variant_generation_service or VariantGenerationService()

    def optimize_text(self, request: TextOptimizationRequest) -> TextOptimizationResult:
        original_analysis = self.analysis_service.analyze_text(
            TextAnalysisRequest(
                project_id=request.project_id,
                content_type=request.content_type,
                body=request.body,
                title=request.title,
                audience=request.audience,
            )
        )
        revision_plan = self.revision_service.build_plan(
            asset=original_analysis.asset,
            analysis_run=original_analysis.analysis_run,
            audience_profile=original_analysis.audience_profile,
        )
        route_provider = getattr(self.variant_generation_service, "provider_service", None)
        variants = self.variant_generation_service.generate_variants(
            asset=original_analysis.asset,
            revision_plan=revision_plan,
        )
        variant_analyses = [
            self.analysis_service.analyze_text(
                TextAnalysisRequest(
                    project_id=request.project_id,
                    content_type=request.content_type,
                    body=variant.body,
                    title=request.title,
                    audience=request.audience,
                )
            )
            for variant in variants
        ]
        rankings = self._rank_variants(
            original_analysis=original_analysis,
            variant_analyses=variant_analyses,
            variant_ids=[variant.variant_id for variant in variants],
        )
        optimization_run = OptimizationRun(
            optimization_run_id=self._stable_id("optimization_run", revision_plan.revision_plan_id),
            project_id=request.project_id,
            source_asset_id=original_analysis.asset.asset_id,
            source_analysis_run_id=original_analysis.analysis_run.analysis_run_id,
            revision_plan_id=revision_plan.revision_plan_id,
            status="completed",
            route_provider=rankings and next((variant.provider for variant in variants if variant.variant_id == rankings[0].variant_id), None),
            route_model=rankings and next((variant.model_name for variant in variants if variant.variant_id == rankings[0].variant_id), None),
            recommended_variant_id=rankings[0].variant_id if rankings else None,
            lineage=ArtifactLineage(
                source_project_id=request.project_id,
                source_asset_id=original_analysis.asset.asset_id,
                source_analysis_run_id=original_analysis.analysis_run.analysis_run_id,
                source_revision_plan_id=revision_plan.revision_plan_id,
            ),
        )
        optimization_report = self._build_optimization_report(
            optimization_run=optimization_run,
            rankings=rankings,
        )
        return TextOptimizationResult(
            original_analysis=original_analysis,
            optimization_run=optimization_run,
            revision_plan=revision_plan,
            variants=variants,
            variant_analyses=variant_analyses,
            variant_rankings=rankings,
            optimization_report=optimization_report,
        )

    def _rank_variants(
        self,
        original_analysis: TextAnalysisResult,
        variant_analyses: list[TextAnalysisResult],
        variant_ids: list[str],
    ) -> list[VariantRanking]:
        original_scores = {
            score.dimension: score.value for score in original_analysis.analysis_run.score_vector.scores
        }
        target_goals = original_analysis.audience_profile.target_goals
        weighted_rankings = []
        for variant_id, variant_analysis in zip(variant_ids, variant_analyses, strict=True):
            score_map = {
                score.dimension: score.value for score in variant_analysis.analysis_run.score_vector.scores
            }
            score = 0.0
            improvement_delta = 0.0
            for goal in target_goals:
                baseline = original_scores.get(goal.dimension, 0.0)
                candidate = score_map.get(goal.dimension, baseline)
                delta = candidate - baseline
                improvement_delta += delta
                score += candidate * (6 - goal.priority) + delta
            weighted_rankings.append((variant_id, score, improvement_delta))

        weighted_rankings.sort(key=lambda item: item[1], reverse=True)
        return [
            VariantRanking(
                variant_id=variant_id,
                rank=index,
                score=round(score, 4),
                improvement_delta=round(delta, 4),
                rationale=(
                    "Higher rank because the variant improves the requested target dimensions "
                    "more than the baseline."
                ),
            )
            for index, (variant_id, score, delta) in enumerate(weighted_rankings, start=1)
        ]

    def _build_optimization_report(
        self,
        optimization_run: OptimizationRun,
        rankings: list[VariantRanking],
    ) -> OptimizationReport:
        recommended = rankings[0]
        return OptimizationReport(
            optimization_report_id=self._stable_id("optimization_report", optimization_run.optimization_run_id),
            optimization_run_id=optimization_run.optimization_run_id,
            recommended_variant_id=recommended.variant_id,
            summary=(
                "Optimization completed with ranked variants and a recommended candidate "
                "based on target-goal-weighted improvement."
            ),
            recommendation_rationale=recommended.rationale,
            comparisons=[
                VariantComparison(
                    variant_id=ranking.variant_id,
                    rank=ranking.rank,
                    score=ranking.score,
                    improvement_delta=ranking.improvement_delta,
                    summary=ranking.rationale,
                )
                for ranking in rankings
            ],
            lineage=ArtifactLineage(
                source_asset_id=optimization_run.source_asset_id,
                source_analysis_run_id=optimization_run.source_analysis_run_id,
                source_revision_plan_id=optimization_run.revision_plan_id,
            ),
        )

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
