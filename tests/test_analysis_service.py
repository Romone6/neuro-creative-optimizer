from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest


def test_analysis_service_returns_complete_report_contract() -> None:
    service = AnalysisService()

    result = service.analyze_text(
        TextAnalysisRequest(
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

    assert result.analysis_run.status == "completed"
    assert result.report.summary
    assert result.report.strongest_dimensions
    assert result.report.weakest_dimensions
    assert result.report.risk_flags is not None

