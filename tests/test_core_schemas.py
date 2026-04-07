from neuro_core.schemas import (
    AnalysisRun,
    ArtifactLineage,
    ConfidenceSummary,
    ContentAsset,
    ContentSegment,
    RevisionInstruction,
    RevisionPlan,
    ScoreEvidence,
    ScoreValue,
    ScoreVector,
    TargetResponseGoal,
    VariantAsset,
)


def test_content_asset_and_segment_share_versioned_lineage_contract() -> None:
    asset = ContentAsset(
        asset_id="asset_1",
        project_id="project_1",
        content_type="speech",
        body="Hello audience.",
        title="Draft",
        source_kind="user_input",
        lineage=ArtifactLineage(),
    )
    segment = ContentSegment(
        segment_id="segment_1",
        asset_id="asset_1",
        index=0,
        kind="paragraph",
        text="Hello audience.",
        start_char=0,
        end_char=15,
        lineage=ArtifactLineage(source_asset_id="asset_1"),
    )

    assert asset.schema_version == "2026-04-04"
    assert segment.schema_version == "2026-04-04"
    assert segment.lineage.source_asset_id == "asset_1"


def test_analysis_run_captures_scores_confidence_and_evidence() -> None:
    analysis = AnalysisRun(
        analysis_run_id="run_1",
        project_id="project_1",
        asset_id="asset_1",
        audience_profile_id="aud_1",
        status="completed",
        score_vector=ScoreVector(
            score_vector_id="sv_1",
            asset_id="asset_1",
            confidence_summary=ConfidenceSummary(
                overall_confidence=0.76,
                low_confidence_dimensions=["novelty"],
                notes=["Baseline lexical scorer"],
            ),
            scores=[
                ScoreValue(
                    dimension="trust",
                    value=0.64,
                    confidence=0.72,
                    target_value=0.8,
                    explanation="Specificity helps, opener overclaims.",
                    evidence=[
                        ScoreEvidence(
                            segment_id="segment_1",
                            quote="Hello audience.",
                            start_char=0,
                            end_char=15,
                            reason="Direct claim establishes tone.",
                        )
                    ],
                )
            ],
        ),
        lineage=ArtifactLineage(source_asset_id="asset_1"),
    )

    assert analysis.score_vector.scores[0].dimension == "trust"
    assert analysis.score_vector.confidence_summary.overall_confidence == 0.76
    assert analysis.lineage.source_asset_id == "asset_1"


def test_revision_plan_and_variant_preserve_traceability() -> None:
    revision_plan = RevisionPlan(
        revision_plan_id="plan_1",
        asset_id="asset_1",
        analysis_run_id="run_1",
        target_goals=[
            TargetResponseGoal(dimension="clarity", target_value=0.85, priority=1)
        ],
        instructions=[
            RevisionInstruction(
                instruction_id="inst_1",
                dimension="clarity",
                priority=1,
                prompt="Reduce abstraction in the opener.",
                rationale="The opening is too vague for this audience.",
                segment_ids=["segment_1"],
            )
        ],
        lineage=ArtifactLineage(source_asset_id="asset_1", source_analysis_run_id="run_1"),
    )
    variant = VariantAsset(
        variant_id="variant_1",
        source_asset_id="asset_1",
        revision_plan_id="plan_1",
        body="Hello audience. Here is the concrete promise.",
        diff_summary="Made the opener more concrete.",
        applied_instruction_ids=["inst_1"],
        lineage=ArtifactLineage(
            source_asset_id="asset_1",
            source_analysis_run_id="run_1",
            source_revision_plan_id="plan_1",
        ),
    )

    assert revision_plan.target_goals[0].dimension == "clarity"
    assert variant.lineage.source_revision_plan_id == "plan_1"
    assert variant.applied_instruction_ids == ["inst_1"]

