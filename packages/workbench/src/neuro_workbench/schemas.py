from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class AudiencePresetRequest(BaseModel):
    project_id: str
    preset_name: str
    audience: dict


class AudiencePreset(BaseModel):
    preset_id: str
    project_id: str
    preset_name: str
    audience: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectHistoryEntry(BaseModel):
    entry_id: str
    project_id: str
    run_type: Literal["analysis", "optimization", "evaluation", "audio_analysis", "tribe_analysis", "agent_campaign"]
    run_id: str
    summary: str
    recommended_target_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SavedScoreProfile(BaseModel):
    profile_id: str
    project_id: str
    target_id: str
    label: str
    scores: dict[str, float]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DiffRecord(BaseModel):
    diff_id: str
    project_id: str
    source_target_id: str
    target_id: str
    added_word_count: int = 0
    removed_word_count: int = 0
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExperimentNotebookEntry(BaseModel):
    notebook_id: str
    project_id: str
    source_run_id: str
    notebook_type: Literal["optimization", "evaluation", "audio_analysis", "tribe_analysis", "agent_campaign"]
    summary: str
    highlights: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectDashboard(BaseModel):
    project_id: str
    total_history_entries: int
    audience_preset_count: int
    saved_score_profile_count: int
    diff_record_count: int
    experiment_notebook_count: int
    optimization_run_count: int
    evaluation_run_count: int
    recent_history: list[ProjectHistoryEntry] = Field(default_factory=list)
    audience_presets: list[AudiencePreset] = Field(default_factory=list)
    last_recommended_target_id: str | None = None
    notes: list[str] = Field(default_factory=list)


class WorkbenchOptimizationRecordResult(BaseModel):
    optimization_result: object
    history_entry: ProjectHistoryEntry
    score_profiles: list[SavedScoreProfile]
    diff_records: list[DiffRecord]
    notebook_entry: ExperimentNotebookEntry


class WorkbenchEvaluationRecordResult(BaseModel):
    evaluation_result: object
    history_entry: ProjectHistoryEntry
    notebook_entry: ExperimentNotebookEntry

