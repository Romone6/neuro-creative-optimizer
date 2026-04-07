from neuro_evaluation.service import EvaluationService, TextEvaluationRequest


def test_evaluation_service_returns_metrics_and_report() -> None:
    service = EvaluationService()

    result = service.evaluate_text(
        TextEvaluationRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
            },
            variants=[
                {
                    "variant_id": "variant_a",
                    "body": "Act now. Here is the concrete promise and why it is credible.",
                },
                {
                    "variant_id": "variant_b",
                    "body": "Act now. Here is the direct benefit in plain language.",
                },
            ],
            human_ratings=[
                {
                    "target_id": "original",
                    "rater_id": "r1",
                    "dimension_scores": {"trust": 0.55, "clarity": 0.62},
                },
                {
                    "target_id": "variant_a",
                    "rater_id": "r1",
                    "dimension_scores": {"trust": 0.86, "clarity": 0.71},
                },
                {
                    "target_id": "variant_b",
                    "rater_id": "r1",
                    "dimension_scores": {"trust": 0.74, "clarity": 0.9},
                },
            ],
            preference_votes=[
                {
                    "winner_target_id": "variant_a",
                    "loser_target_id": "original",
                    "rater_id": "r1",
                    "reason": "More credible",
                }
            ],
        )
    )

    assert result.evaluation_run.status == "completed"
    assert result.experiment_run.status == "completed"
    assert result.evaluation_report.summary
    assert result.evaluation_report.preference_summary
    assert result.calibration_metrics
    assert result.dimension_validations

