from neuro_agent.schemas import (
    AgentApprovalRequest,
    AgentCampaignRequest,
    AgentCandidateInput,
    ChannelConstraint,
)
from neuro_agent.service import AgentWorkflowService


def test_agent_workflow_service_runs_campaign_loop_and_records_approval(tmp_path) -> None:
    service = AgentWorkflowService(repo_root=tmp_path)

    result = service.optimize_campaign(
        AgentCampaignRequest(
            project_id="project_campaign",
            content_type="ad_copy",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [{"dimension": "trust", "target_value": 0.82, "priority": 1}],
            },
            candidates=[
                AgentCandidateInput(candidate_id="candidate_a", body="Act now. This offer is specific and credible."),
                AgentCandidateInput(candidate_id="candidate_b", body="Build momentum fast with a concrete reason to believe this works."),
            ],
            channel_constraints=[
                ChannelConstraint(platform="linkedin", max_chars=140),
            ],
        )
    )

    approval = service.record_approval(
        AgentApprovalRequest(
            project_id="project_campaign",
            target_id=result.campaign_comparison.recommended_target_id,
            status="approved",
            reviewer_id="editor_1",
            reason="Best fit for channel and trust goal.",
        )
    )

    assert result.batch_score_result.ranked_candidates
    assert result.campaign_comparison.recommended_target_id
    assert result.optimized_candidates
    assert approval.status == "approved"
    assert approval.target_id == result.campaign_comparison.recommended_target_id

