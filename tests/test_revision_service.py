from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest
from neuro_analysis.revision import RevisionService


def test_revision_service_builds_prioritized_revision_plan() -> None:
    analysis_service = AnalysisService()
    revision_service = RevisionService()
    analysis_result = analysis_service.analyze_text(
        TextAnalysisRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1},
                    {"dimension": "clarity", "target_value": 0.9, "priority": 2},
                ],
            },
        )
    )

    revision_plan = revision_service.build_plan(
        asset=analysis_result.asset,
        analysis_run=analysis_result.analysis_run,
        audience_profile=analysis_result.audience_profile,
    )

    assert revision_plan.target_goals[0].dimension == "trust"
    assert revision_plan.instructions
    assert revision_plan.instructions[0].segment_ids

