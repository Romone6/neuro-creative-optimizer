from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "2026-04-04"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ArtifactLineage(StrictModel):
    source_project_id: str | None = None
    source_asset_id: str | None = None
    source_variant_id: str | None = None
    source_analysis_run_id: str | None = None
    source_revision_plan_id: str | None = None
    generated_by_run_id: str | None = None


class VersionedRecord(StrictModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lineage: ArtifactLineage


class TargetResponseGoal(StrictModel):
    dimension: str
    target_value: float
    priority: int = Field(ge=1, le=5)
    min_delta: float | None = None


class ContentAsset(VersionedRecord):
    asset_id: str
    project_id: str
    content_type: str
    body: str
    title: str | None = None
    source_kind: Literal["user_input", "generated", "imported"]
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class ContentSegment(VersionedRecord):
    segment_id: str
    asset_id: str
    index: int = Field(ge=0)
    kind: Literal["sentence", "paragraph", "rhetorical_block", "line", "section"]
    text: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    label: str | None = None


class AudienceProfile(VersionedRecord):
    audience_profile_id: str
    label: str
    age_band: str | None = None
    cultural_context: str | None = None
    topic_familiarity: str | None = None
    literacy_assumption: str | None = None
    platform_context: str | None = None
    tone_preference: str | None = None
    genre_preference: str | None = None
    brand_affinity: str | None = None
    target_goals: list[TargetResponseGoal] = Field(default_factory=list)


class ScoreEvidence(StrictModel):
    segment_id: str | None = None
    quote: str | None = None
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)
    reason: str


class ScoreValue(StrictModel):
    dimension: str
    value: float
    confidence: float = Field(ge=0.0, le=1.0)
    target_value: float | None = None
    explanation: str
    evidence: list[ScoreEvidence] = Field(default_factory=list)


class ConfidenceSummary(StrictModel):
    overall_confidence: float = Field(ge=0.0, le=1.0)
    low_confidence_dimensions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ScoreVector(StrictModel):
    score_vector_id: str
    asset_id: str
    confidence_summary: ConfidenceSummary
    scores: list[ScoreValue] = Field(default_factory=list)


class SegmentScoreVector(StrictModel):
    segment_id: str
    scores: list[ScoreValue] = Field(default_factory=list)


class AnalysisRun(VersionedRecord):
    analysis_run_id: str
    project_id: str
    asset_id: str
    audience_profile_id: str
    status: Literal["queued", "running", "completed", "failed"]
    provider: str | None = None
    model_name: str | None = None
    score_vector: ScoreVector
    segment_score_vectors: list[SegmentScoreVector] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RevisionInstruction(StrictModel):
    instruction_id: str
    dimension: str
    priority: int = Field(ge=1, le=5)
    prompt: str
    rationale: str
    segment_ids: list[str] = Field(default_factory=list)


class RevisionPlan(VersionedRecord):
    revision_plan_id: str
    asset_id: str
    analysis_run_id: str
    target_goals: list[TargetResponseGoal] = Field(default_factory=list)
    instructions: list[RevisionInstruction] = Field(default_factory=list)
    constraints: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class VariantAsset(VersionedRecord):
    variant_id: str
    source_asset_id: str
    revision_plan_id: str
    provider: str | None = None
    model_name: str | None = None
    body: str
    diff_summary: str
    applied_instruction_ids: list[str] = Field(default_factory=list)


class VariantRanking(StrictModel):
    variant_id: str
    rank: int = Field(ge=1)
    score: float
    improvement_delta: float
    rationale: str


class OptimizationRun(VersionedRecord):
    optimization_run_id: str
    project_id: str
    source_asset_id: str
    source_analysis_run_id: str
    revision_plan_id: str
    status: Literal["queued", "running", "completed", "failed"]
    route_provider: str | None = None
    route_model: str | None = None
    recommended_variant_id: str | None = None


class VariantComparison(StrictModel):
    variant_id: str
    rank: int
    score: float
    improvement_delta: float
    summary: str


class OptimizationReport(VersionedRecord):
    optimization_report_id: str
    optimization_run_id: str
    recommended_variant_id: str
    summary: str
    recommendation_rationale: str
    comparisons: list[VariantComparison] = Field(default_factory=list)


class TextFeatureBundle(VersionedRecord):
    feature_bundle_id: str
    asset_id: str
    word_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    paragraph_count: int = Field(ge=0)
    avg_sentence_length: float = Field(ge=0.0)
    avg_word_length: float = Field(ge=0.0)
    question_count: int = Field(ge=0)
    exclamation_count: int = Field(ge=0)
    uppercase_ratio: float = Field(ge=0.0, le=1.0)
    unique_token_ratio: float = Field(ge=0.0, le=1.0)
    repeated_token_ratio: float = Field(ge=0.0, le=1.0)
    long_sentence_ratio: float = Field(ge=0.0, le=1.0)
    urgency_term_count: int = Field(ge=0)
    trust_term_count: int = Field(ge=0)
    sensory_term_count: int = Field(ge=0)
    feature_notes: list[str] = Field(default_factory=list)


class SegmentHighlight(StrictModel):
    segment_id: str
    label: str
    reason: str


class AnalysisReport(VersionedRecord):
    report_id: str
    analysis_run_id: str
    summary: str
    strongest_dimensions: list[str] = Field(default_factory=list)
    weakest_dimensions: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    segment_highlights: list[SegmentHighlight] = Field(default_factory=list)
