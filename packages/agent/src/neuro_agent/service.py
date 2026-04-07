from __future__ import annotations

from hashlib import sha1
from pathlib import Path

from neuro_analysis import AnalysisService, OptimizationService, TextAnalysisRequest, TextOptimizationRequest
from neuro_agent.schemas import (
    AgentApprovalRecord,
    AgentApprovalRequest,
    AgentCampaignRequest,
    AgentCampaignResult,
    BatchScoreRequest,
    BatchScoreResult,
    CampaignComparison,
    OptimizedCandidate,
    RankedCandidate,
)
from neuro_agent.store import AgentStore


class AgentWorkflowService:
    def __init__(
        self,
        repo_root: Path,
        analysis_service: AnalysisService | None = None,
        optimization_service: OptimizationService | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.analysis_service = analysis_service or AnalysisService()
        self.optimization_service = optimization_service or OptimizationService()
        self.store = AgentStore(repo_root)

    def batch_score(self, request: BatchScoreRequest) -> BatchScoreResult:
        ranked: list[RankedCandidate] = []
        for candidate in request.candidates:
            analysis = self.analysis_service.analyze_text(
                TextAnalysisRequest(
                    project_id=request.project_id,
                    content_type=request.content_type,
                    body=candidate.body,
                    title=candidate.title,
                    audience=request.audience,
                )
            )
            base_score = self._goal_weighted_score(analysis.analysis_run.score_vector.scores, request.audience)
            channel_penalty = self._channel_penalty(candidate.body, request.channel_constraints)
            final_score = round(base_score - channel_penalty, 4)
            ranked.append(
                RankedCandidate(
                    candidate_id=candidate.candidate_id,
                    final_score=final_score,
                    channel_penalty=channel_penalty,
                    summary="Candidate scored against audience goals with optional channel constraints.",
                )
            )
        ranked.sort(key=lambda item: item.final_score, reverse=True)
        return BatchScoreResult(
            ranked_candidates=ranked,
            recommended_candidate_id=ranked[0].candidate_id if ranked else None,
            notes=["agent_batch_scoring_v1"],
        )

    def optimize_campaign(self, request: AgentCampaignRequest) -> AgentCampaignResult:
        batch_result = self.batch_score(
            BatchScoreRequest(
                project_id=request.project_id,
                content_type=request.content_type,
                audience=request.audience,
                candidates=request.candidates,
                channel_constraints=request.channel_constraints,
            )
        )
        optimized_candidates: list[OptimizedCandidate] = []
        for candidate in request.candidates:
            optimization = self.optimization_service.optimize_text(
                TextOptimizationRequest(
                    project_id=request.project_id,
                    content_type=request.content_type,
                    body=candidate.body,
                    title=candidate.title,
                    audience=request.audience,
                )
            )
            best_variant_id = optimization.optimization_report.recommended_variant_id
            best_variant = next(variant for variant in optimization.variants if variant.variant_id == best_variant_id)
            best_analysis = next(
                analysis for variant, analysis in zip(optimization.variants, optimization.variant_analyses, strict=True) if variant.variant_id == best_variant_id
            )
            final_score = self._goal_weighted_score(best_analysis.analysis_run.score_vector.scores, request.audience)
            penalty = self._channel_penalty(best_variant.body, request.channel_constraints)
            optimized_candidates.append(
                OptimizedCandidate(
                    source_candidate_id=candidate.candidate_id,
                    recommended_target_id=best_variant_id,
                    recommended_body=best_variant.body,
                    final_score=round(final_score - penalty, 4),
                    channel_penalty=penalty,
                )
            )
        optimized_candidates.sort(key=lambda item: item.final_score, reverse=True)
        comparison = CampaignComparison(
            summary="Campaign loop completed by optimize-score-rank across source candidates.",
            recommended_target_id=optimized_candidates[0].recommended_target_id if optimized_candidates else None,
            ranked_target_ids=[candidate.recommended_target_id for candidate in optimized_candidates],
            notes=["agent_campaign_loop_v1"],
        )
        return AgentCampaignResult(
            batch_score_result=batch_result,
            optimized_candidates=optimized_candidates,
            campaign_comparison=comparison,
            notes=["approval_workflow_ready"],
        )

    def record_approval(self, request: AgentApprovalRequest) -> AgentApprovalRecord:
        record = AgentApprovalRecord(
            approval_id=self._stable_id("approval", request.project_id, request.target_id, request.status, request.reviewer_id),
            project_id=request.project_id,
            target_id=request.target_id,
            status=request.status,
            reviewer_id=request.reviewer_id,
            reason=request.reason,
        )
        approvals = self.store.load_approvals(request.project_id)
        approvals.append(record.model_dump(mode="json"))
        self.store.save_approvals(request.project_id, approvals)
        return record

    def _goal_weighted_score(self, score_values, audience: dict) -> float:
        goals = audience.get("target_goals", [])
        score_map = {score.dimension: score.value for score in score_values}
        total = 0.0
        for goal in goals:
            total += score_map.get(goal["dimension"], 0.0) * (6 - goal["priority"])
        return total

    def _channel_penalty(self, body: str, constraints) -> float:
        penalty = 0.0
        for constraint in constraints:
            if constraint.max_chars is not None and len(body) > constraint.max_chars:
                penalty += min(0.4, (len(body) - constraint.max_chars) / max(1, constraint.max_chars))
        return round(penalty, 4)

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
