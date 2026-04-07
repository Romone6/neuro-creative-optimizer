from __future__ import annotations

from collections import defaultdict

from neuro_evaluation.schemas import (
    CalibrationDimensionMetric,
    CalibrationSummary,
    DimensionValidation,
    HumanRating,
    PreferenceSummary,
    PreferenceVote,
)


class EvaluationMetricsService:
    def compute_calibration(
        self,
        model_scores_by_target: dict[str, dict[str, float]],
        human_ratings: list[HumanRating],
    ) -> CalibrationSummary:
        by_dimension: dict[str, list[float]] = defaultdict(list)
        for rating in human_ratings:
            model_scores = model_scores_by_target.get(rating.target_id, {})
            for dimension, human_value in rating.dimension_scores.items():
                if dimension in model_scores:
                    by_dimension[dimension].append(abs(model_scores[dimension] - human_value))

        dimension_metrics = []
        for dimension, errors in by_dimension.items():
            mae = sum(errors) / len(errors)
            alignment = max(0.0, min(1.0, 1 - mae))
            dimension_metrics.append(
                CalibrationDimensionMetric(
                    dimension=dimension,
                    mean_absolute_error=round(mae, 4),
                    alignment_score=round(alignment, 4),
                )
            )

        overall_alignment = (
            round(sum(metric.alignment_score for metric in dimension_metrics) / len(dimension_metrics), 4)
            if dimension_metrics
            else 0.0
        )
        return CalibrationSummary(
            overall_alignment=overall_alignment,
            dimension_metrics=sorted(dimension_metrics, key=lambda metric: metric.dimension),
        )

    def compute_preference_summary(
        self,
        model_ranked_target_ids: list[str],
        preference_votes: list[PreferenceVote],
    ) -> PreferenceSummary:
        if not preference_votes:
            return PreferenceSummary(total_votes=0, aligned_votes=0, alignment_rate=0.0)

        aligned = 0
        preferred_target_id = None
        if model_ranked_target_ids:
            preferred_target_id = model_ranked_target_ids[0]
        for vote in preference_votes:
            winner_index = model_ranked_target_ids.index(vote.winner_target_id) if vote.winner_target_id in model_ranked_target_ids else None
            loser_index = model_ranked_target_ids.index(vote.loser_target_id) if vote.loser_target_id in model_ranked_target_ids else None
            if winner_index is not None and loser_index is not None and winner_index < loser_index:
                aligned += 1

        total_votes = len(preference_votes)
        return PreferenceSummary(
            total_votes=total_votes,
            aligned_votes=aligned,
            alignment_rate=round(aligned / total_votes, 4),
            preferred_target_id=preferred_target_id,
        )

    def compute_dimension_validations(
        self,
        model_scores_by_target: dict[str, dict[str, float]],
        human_ratings: list[HumanRating],
        calibration: CalibrationSummary,
    ) -> list[DimensionValidation]:
        human_by_dimension: dict[str, list[float]] = defaultdict(list)
        model_by_dimension: dict[str, list[float]] = defaultdict(list)
        for rating in human_ratings:
            model_scores = model_scores_by_target.get(rating.target_id, {})
            for dimension, human_value in rating.dimension_scores.items():
                human_by_dimension[dimension].append(human_value)
                if dimension in model_scores:
                    model_by_dimension[dimension].append(model_scores[dimension])

        calibration_by_dimension = {metric.dimension: metric for metric in calibration.dimension_metrics}
        validations = []
        for dimension, human_values in human_by_dimension.items():
            model_values = model_by_dimension.get(dimension, [])
            human_avg = sum(human_values) / len(human_values)
            model_avg = sum(model_values) / len(model_values) if model_values else 0.0
            alignment = calibration_by_dimension.get(dimension)
            alignment_score = alignment.alignment_score if alignment else 0.0
            status = "strong" if alignment_score >= 0.8 else "mixed" if alignment_score >= 0.6 else "weak"
            validations.append(
                DimensionValidation(
                    dimension=dimension,
                    model_average=round(model_avg, 4),
                    human_average=round(human_avg, 4),
                    alignment_score=alignment_score,
                    status=status,
                    note=f"{dimension} shows {status} alignment in the current sample.",
                )
            )
        return sorted(validations, key=lambda item: item.dimension)

