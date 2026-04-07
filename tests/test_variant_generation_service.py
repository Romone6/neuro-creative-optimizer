from neuro_analysis.analysis import AnalysisService, TextAnalysisRequest
from neuro_analysis.revision import RevisionService
from neuro_analysis.variants import VariantGenerationService


def test_variant_generation_service_creates_multiple_traceable_variants() -> None:
    analysis_service = AnalysisService()
    revision_service = RevisionService()
    variant_service = VariantGenerationService()
    analysis_result = analysis_service.analyze_text(
        TextAnalysisRequest(
            project_id="project_1",
            content_type="ad_copy",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
            },
        )
    )
    revision_plan = revision_service.build_plan(
        asset=analysis_result.asset,
        analysis_run=analysis_result.analysis_run,
        audience_profile=analysis_result.audience_profile,
    )

    variants = variant_service.generate_variants(
        asset=analysis_result.asset,
        revision_plan=revision_plan,
    )

    assert len(variants) == 3
    assert all(variant.revision_plan_id == revision_plan.revision_plan_id for variant in variants)
    assert len({variant.body for variant in variants}) == 3

