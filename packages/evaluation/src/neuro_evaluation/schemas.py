from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class HumanRating(BaseModel):
    target_id: str
    rater_id: str
    dimension_scores: dict[str, float]


class PreferenceVote(BaseModel):
    winner_target_id: str
    loser_target_id: str
    rater_id: str
    reason: str | None = None


class VariantInput(BaseModel):
    variant_id: str
    body: str


class CalibrationDimensionMetric(BaseModel):
    dimension: str
    mean_absolute_error: float
    alignment_score: float


class CalibrationSummary(BaseModel):
    overall_alignment: float
    dimension_metrics: list[CalibrationDimensionMetric]


class PreferenceSummary(BaseModel):
    total_votes: int
    aligned_votes: int
    alignment_rate: float
    preferred_target_id: str | None = None


class DimensionValidation(BaseModel):
    dimension: str
    model_average: float
    human_average: float
    alignment_score: float
    status: Literal["strong", "mixed", "weak"]
    note: str


class EvaluationRun(BaseModel):
    evaluation_run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    source_analysis_run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExperimentRun(BaseModel):
    experiment_run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    project_id: str
    compared_target_ids: list[str]
    recommended_target_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvaluationReport(BaseModel):
    evaluation_report_id: str
    summary: str
    preference_summary: str
    calibration_summary: str
    strongest_dimensions: list[str]
    weakest_dimensions: list[str]
    notes: list[str] = Field(default_factory=list)


class TextEvaluationRequest(BaseModel):
    project_id: str
    content_type: str
    body: str
    audience: dict
    variants: list[VariantInput]
    human_ratings: list[HumanRating]
    preference_votes: list[PreferenceVote] = Field(default_factory=list)


class TextEvaluationResult(BaseModel):
    original_analysis: object
    variant_analyses: list[object]
    evaluation_run: EvaluationRun
    experiment_run: ExperimentRun
    calibration_metrics: CalibrationSummary
    preference_summary: PreferenceSummary
    dimension_validations: list[DimensionValidation]
    evaluation_report: EvaluationReport

