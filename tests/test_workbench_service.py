from neuro_analysis.optimization import TextOptimizationRequest
from neuro_evaluation.schemas import HumanRating, PreferenceVote, TextEvaluationRequest, VariantInput
from neuro_workbench.service import WorkbenchService


def test_workbench_service_records_runs_presets_profiles_and_diffs(tmp_path) -> None:
    service = WorkbenchService(repo_root=tmp_path)

    preset = service.save_audience_preset(
        project_id="project_1",
        preset_name="cold_traffic_founders",
        audience={
            "label": "Cold traffic founders",
            "platform_context": "linkedin",
            "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
        },
    )
    optimization_record = service.record_optimization(
        TextOptimizationRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience=preset.audience,
        )
    )
    recommended_variant = optimization_record.optimization_result.optimization_report.recommended_variant_id
    recommended_body = next(
        variant.body
        for variant in optimization_record.optimization_result.variants
        if variant.variant_id == recommended_variant
    )
    evaluation_record = service.record_evaluation(
        TextEvaluationRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience=preset.audience,
            variants=[VariantInput(variant_id=recommended_variant, body=recommended_body)],
            human_ratings=[
                HumanRating(target_id="original", rater_id="r1", dimension_scores={"trust": 0.58, "clarity": 0.62}),
                HumanRating(target_id=recommended_variant, rater_id="r1", dimension_scores={"trust": 0.84, "clarity": 0.7}),
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
    dashboard = service.get_project_dashboard("project_1")

    assert preset.preset_name == "cold_traffic_founders"
    assert optimization_record.history_entry.run_type == "optimization"
    assert optimization_record.diff_records
    assert evaluation_record.history_entry.run_type == "evaluation"
    assert dashboard.total_history_entries == 2
    assert dashboard.audience_preset_count == 1
    assert dashboard.saved_score_profile_count >= 2
    assert dashboard.diff_record_count >= 3
    assert dashboard.last_recommended_target_id

