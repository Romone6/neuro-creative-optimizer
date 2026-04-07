from __future__ import annotations

from hashlib import sha1

from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest
from neuro_evaluation.metrics import EvaluationMetricsService
from neuro_evaluation.schemas import (
    EvaluationReport,
    EvaluationRun,
    ExperimentRun,
    TextEvaluationRequest,
    TextEvaluationResult,
)


class EvaluationService:
    def __init__(
        self,
        analysis_service: AnalysisService | None = None,
        metrics_service: EvaluationMetricsService | None = None,
    ) -> None:
        self.analysis_service = analysis_service or AnalysisService()
        self.metrics_service = metrics_service or EvaluationMetricsService()

    def evaluate_text(self, request: TextEvaluationRequest) -> TextEvaluationResult:
        original_analysis = self.analysis_service.analyze_text(
            TextAnalysisRequest(
                project_id=request.project_id,
                content_type=request.content_type,
                body=request.body,
                audience=request.audience,
            )
        )
        variant_analyses = [
            self.analysis_service.analyze_text(
                TextAnalysisRequest(
                    project_id=request.project_id,
                    content_type=request.content_type,
                    body=variant.body,
                    audience=request.audience,
                )
            )
            for variant in request.variants
        ]

        model_scores_by_target = {
            "original": {
                score.dimension: score.value
                for score in original_analysis.analysis_run.score_vector.scores
            }
        }
        for variant, analysis in zip(request.variants, variant_analyses, strict=True):
            model_scores_by_target[variant.variant_id] = {
                score.dimension: score.value for score in analysis.analysis_run.score_vector.scores
            }

        calibration = self.metrics_service.compute_calibration(
            model_scores_by_target=model_scores_by_target,
            human_ratings=request.human_ratings,
        )
        ranked_targets = self._rank_targets_by_model(model_scores_by_target, request.audience)
        preference_summary = self.metrics_service.compute_preference_summary(
            model_ranked_target_ids=ranked_targets,
            preference_votes=request.preference_votes,
        )
        dimension_validations = self.metrics_service.compute_dimension_validations(
            model_scores_by_target=model_scores_by_target,
            human_ratings=request.human_ratings,
            calibration=calibration,
        )

        evaluation_run = EvaluationRun(
            evaluation_run_id=self._stable_id("evaluation_run", request.project_id, original_analysis.analysis_run.analysis_run_id),
            status="completed",
            source_analysis_run_id=original_analysis.analysis_run.analysis_run_id,
        )
        experiment_run = ExperimentRun(
            experiment_run_id=self._stable_id("experiment_run", request.project_id, *ranked_targets),
            status="completed",
            project_id=request.project_id,
            compared_target_ids=ranked_targets,
            recommended_target_id=ranked_targets[0] if ranked_targets else None,
        )
        strongest = [item.dimension for item in sorted(dimension_validations, key=lambda x: x.alignment_score, reverse=True)[:2]]
        weakest = [item.dimension for item in sorted(dimension_validations, key=lambda x: x.alignment_score)[:2]]
        evaluation_report = EvaluationReport(
            evaluation_report_id=self._stable_id("evaluation_report", evaluation_run.evaluation_run_id),
            summary="Evaluation completed with calibration, preference alignment, and dimension validation summaries.",
            preference_summary=(
                f"Preference alignment rate: {preference_summary.alignment_rate:.2f} "
                f"across {preference_summary.total_votes} vote(s)."
            ),
            calibration_summary=(
                f"Overall calibration alignment: {calibration.overall_alignment:.2f} "
                f"across {len(calibration.dimension_metrics)} dimension(s)."
            ),
            strongest_dimensions=strongest,
            weakest_dimensions=weakest,
            notes=["evaluation_backbone_v1"],
        )
        return TextEvaluationResult(
            original_analysis=original_analysis,
            variant_analyses=variant_analyses,
            evaluation_run=evaluation_run,
            experiment_run=experiment_run,
            calibration_metrics=calibration,
            preference_summary=preference_summary,
            dimension_validations=dimension_validations,
            evaluation_report=evaluation_report,
        )

    def _rank_targets_by_model(self, model_scores_by_target: dict[str, dict[str, float]], audience: dict) -> list[str]:
        goals = audience.get("target_goals", [])
        scored_targets = []
        for target_id, scores in model_scores_by_target.items():
            total = 0.0
            for goal in goals:
                dimension = goal["dimension"]
                priority = goal["priority"]
                total += scores.get(dimension, 0.0) * (6 - priority)
            scored_targets.append((target_id, total))
        scored_targets.sort(key=lambda item: item[1], reverse=True)
        return [target_id for target_id, _ in scored_targets]

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

