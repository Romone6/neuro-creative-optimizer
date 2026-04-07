from neuro_analysis.optimization import OptimizationService, TextOptimizationRequest


def test_optimization_service_returns_ranked_variants() -> None:
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

    assert result.revision_plan.instructions
    assert len(result.variants) == 3
    assert len(result.variant_rankings) == 3
    assert result.variant_rankings[0].rank == 1
    assert result.variant_rankings[0].rationale

