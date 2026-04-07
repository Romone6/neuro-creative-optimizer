from neuro_analysis.optimization import OptimizationService, TextOptimizationRequest


def test_optimization_service_returns_traceable_run_and_report() -> None:
    service = OptimizationService()

    result = service.optimize_text(
        TextOptimizationRequest(
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

    assert result.optimization_run.status == "completed"
    assert result.optimization_report.recommended_variant_id == result.variant_rankings[0].variant_id
    assert result.optimization_report.comparisons
    assert result.optimization_report.summary

