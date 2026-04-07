from pathlib import Path

from neuro_analysis.optimization import TextOptimizationRequest
from neuro_decision.service import CommercialDecisionService
from neuro_evaluation.schemas import HumanRating, PreferenceVote, TextEvaluationRequest, VariantInput
from neuro_workbench.service import WorkbenchService


def test_commercial_decision_service_emits_license_aware_readiness_report(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "setup"
    artifacts.mkdir(parents=True)
    (artifacts / "latest.json").write_text(
        """
        {
          "mode": "tribe_degraded",
          "python_version_ok": true,
          "tribe_repo_present": true,
          "tribe_commit": "abc123",
          "tribe_install_ok": true,
          "pretrained_load_ok": true,
          "smoke_test_ok": false
        }
        """,
        encoding="utf-8",
    )

    workbench = WorkbenchService(repo_root=tmp_path)
    audience = {
        "label": "Cold traffic founders",
        "platform_context": "linkedin",
        "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
    }
    optimization_record = workbench.record_optimization(
        TextOptimizationRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience=audience,
        )
    )
    recommended_variant = optimization_record.optimization_result.optimization_report.recommended_variant_id
    recommended_body = next(
        variant.body
        for variant in optimization_record.optimization_result.variants
        if variant.variant_id == recommended_variant
    )
    workbench.record_evaluation(
        TextEvaluationRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience=audience,
            variants=[VariantInput(variant_id=recommended_variant, body=recommended_body)],
            human_ratings=[
                HumanRating(target_id="original", rater_id="r1", dimension_scores={"trust": 0.58}),
                HumanRating(target_id=recommended_variant, rater_id="r1", dimension_scores={"trust": 0.84}),
            ],
            preference_votes=[
                PreferenceVote(
                    winner_target_id=recommended_variant,
                    loser_target_id="original",
                    rater_id="r1",
                    reason="More credible",
                )
            ],
        )
    )

    report = CommercialDecisionService(repo_root=tmp_path, workbench_service=workbench).assess_project("project_1")

    assert report.project_id == "project_1"
    assert report.recommendation in {"replace_licensed_components_first", "keep_as_research_system", "proceed_with_product_hardening"}
    assert report.summary
    assert report.blockers

