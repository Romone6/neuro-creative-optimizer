from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentCandidateInput(BaseModel):
    candidate_id: str
    body: str
    title: str | None = None


class ChannelConstraint(BaseModel):
    platform: str
    max_chars: int | None = Field(default=None, gt=0)


class RankedCandidate(BaseModel):
    candidate_id: str
    final_score: float
    channel_penalty: float
    summary: str


class BatchScoreRequest(BaseModel):
    project_id: str
    content_type: str
    audience: dict
    candidates: list[AgentCandidateInput]
    channel_constraints: list[ChannelConstraint] = Field(default_factory=list)


class BatchScoreResult(BaseModel):
    ranked_candidates: list[RankedCandidate] = Field(default_factory=list)
    recommended_candidate_id: str | None = None
    notes: list[str] = Field(default_factory=list)


class OptimizedCandidate(BaseModel):
    source_candidate_id: str
    recommended_target_id: str
    recommended_body: str
    final_score: float
    channel_penalty: float


class CampaignComparison(BaseModel):
    summary: str
    recommended_target_id: str | None = None
    ranked_target_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AgentCampaignRequest(BaseModel):
    project_id: str
    content_type: str
    audience: dict
    candidates: list[AgentCandidateInput]
    channel_constraints: list[ChannelConstraint] = Field(default_factory=list)


class AgentApprovalRequest(BaseModel):
    project_id: str
    target_id: str
    status: Literal["approved", "rejected", "needs_review"]
    reviewer_id: str
    reason: str | None = None


class AgentApprovalRecord(BaseModel):
    approval_id: str
    project_id: str
    target_id: str
    status: Literal["approved", "rejected", "needs_review"]
    reviewer_id: str
    reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentCampaignResult(BaseModel):
    batch_score_result: BatchScoreResult
    optimized_candidates: list[OptimizedCandidate] = Field(default_factory=list)
    campaign_comparison: CampaignComparison
    notes: list[str] = Field(default_factory=list)
