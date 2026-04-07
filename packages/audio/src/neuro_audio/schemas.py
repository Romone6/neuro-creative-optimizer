from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from neuro_analysis.analysis import TextAnalysisResult
from neuro_core import ArtifactLineage, ContentAsset


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AudioSectionInput(StrictModel):
    label: str
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    lyrics: str
    energy: float = Field(ge=0.0, le=1.0)
    loudness: float = Field(ge=0.0, le=1.0)
    spectral_contrast: float = Field(ge=0.0, le=1.0)


class AudioAnalysisRequest(BaseModel):
    project_id: str
    content_type: str
    transcript: str
    sections: list[AudioSectionInput]
    audience: dict
    title: str | None = None
    bpm: float | None = Field(default=None, gt=0)


class AlignedAudioSection(StrictModel):
    section_id: str
    label: str
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    duration_ms: int = Field(gt=0)
    lyrics: str
    lyric_word_count: int = Field(ge=0)
    energy: float = Field(ge=0.0, le=1.0)
    loudness: float = Field(ge=0.0, le=1.0)
    spectral_contrast: float = Field(ge=0.0, le=1.0)
    is_hook_candidate: bool = False


class AudioAlignmentResult(StrictModel):
    asset: ContentAsset
    sections: list[AlignedAudioSection] = Field(default_factory=list)
    transcript: str
    total_duration_ms: int = Field(ge=0)
    bpm: float | None = None


class TensionTimelinePoint(StrictModel):
    section_id: str
    label: str
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    tension: float = Field(ge=0.0, le=1.0)
    release: float = Field(ge=0.0, le=1.0)


class AcousticFeatureBundle(StrictModel):
    feature_bundle_id: str
    asset_id: str
    section_count: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    bpm: float | None = None
    avg_energy: float = Field(ge=0.0, le=1.0)
    avg_loudness: float = Field(ge=0.0, le=1.0)
    avg_spectral_contrast: float = Field(ge=0.0, le=1.0)
    energy_variability: float = Field(ge=0.0, le=1.0)
    loudness_variability: float = Field(ge=0.0, le=1.0)
    repetition_ratio: float = Field(ge=0.0, le=1.0)
    hook_section_label: str | None = None
    tension_timeline: list[TensionTimelinePoint] = Field(default_factory=list)
    feature_notes: list[str] = Field(default_factory=list)


class AudioDimensionScore(StrictModel):
    dimension: str
    value: float = Field(ge=0.0, le=1.0)
    explanation: str


class AudioScorecard(StrictModel):
    scorecard_id: str
    asset_id: str
    dimension_scores: list[AudioDimensionScore] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SectionComparisonItem(StrictModel):
    section_id: str
    label: str
    section_score: float = Field(ge=0.0, le=1.0)
    summary: str


class SectionComparisonReport(StrictModel):
    summary: str
    strongest_section_label: str | None = None
    weakest_section_label: str | None = None
    chorus_vs_verse_summary: str | None = None
    items: list[SectionComparisonItem] = Field(default_factory=list)


class AudioTimeline(StrictModel):
    points: list[TensionTimelinePoint] = Field(default_factory=list)


class AudioAnalysisReport(StrictModel):
    summary: str
    recommendations: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class AudioAnalysisResult(StrictModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lineage: ArtifactLineage
    asset: ContentAsset
    aligned_sections: list[AlignedAudioSection] = Field(default_factory=list)
    acoustic_features: AcousticFeatureBundle
    text_analysis: TextAnalysisResult
    audio_scorecard: AudioScorecard
    timeline: AudioTimeline
    section_comparison: SectionComparisonReport
    report: AudioAnalysisReport
