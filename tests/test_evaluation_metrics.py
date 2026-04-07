from neuro_evaluation.metrics import EvaluationMetricsService
from neuro_evaluation.schemas import HumanRating, PreferenceVote


def test_metrics_service_computes_calibration_and_preference_alignment() -> None:
    service = EvaluationMetricsService()

    calibration = service.compute_calibration(
        model_scores_by_target={
            "original": {"trust": 0.5},
            "variant_a": {"trust": 0.85},
        },
        human_ratings=[
            HumanRating(target_id="original", rater_id="r1", dimension_scores={"trust": 0.55}),
            HumanRating(target_id="variant_a", rater_id="r1", dimension_scores={"trust": 0.9}),
        ],
    )
    preference_summary = service.compute_preference_summary(
        model_ranked_target_ids=["variant_a", "original"],
        preference_votes=[
            PreferenceVote(
                winner_target_id="variant_a",
                loser_target_id="original",
                rater_id="r1",
                reason="better",
            )
        ],
    )

    assert calibration.overall_alignment > 0
    assert calibration.dimension_metrics[0].dimension == "trust"
    assert preference_summary.alignment_rate == 1.0

