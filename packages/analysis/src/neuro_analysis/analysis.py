from __future__ import annotations

from hashlib import sha1

from pydantic import BaseModel

from neuro_analysis.audience import AudienceProfileInput, AudienceService
from neuro_analysis.features import FeatureService
from neuro_analysis.ingestion import IngestionService, TextIngestionRequest
from neuro_analysis.scoring import ScoringService
from neuro_core import (
    AnalysisReport,
    AnalysisRun,
    ArtifactLineage,
    SegmentHighlight,
    TextFeatureBundle,
)


class TextAnalysisRequest(BaseModel):
    project_id: str
    content_type: str
    body: str
    title: str | None = None
    audience: AudienceProfileInput | dict


class TextAnalysisResult(BaseModel):
    asset: object
    segments: list[object]
    audience_profile: object
    feature_bundle: TextFeatureBundle
    analysis_run: AnalysisRun
    report: AnalysisReport


class AnalysisService:
    def __init__(
        self,
        ingestion_service: IngestionService | None = None,
        audience_service: AudienceService | None = None,
        feature_service: FeatureService | None = None,
        scoring_service: ScoringService | None = None,
    ) -> None:
        self.ingestion_service = ingestion_service or IngestionService()
        self.audience_service = audience_service or AudienceService()
        self.feature_service = feature_service or FeatureService()
        self.scoring_service = scoring_service or ScoringService()

    def analyze_text(self, request: TextAnalysisRequest) -> TextAnalysisResult:
        ingestion_result = self.ingestion_service.ingest_text(
            TextIngestionRequest(
                project_id=request.project_id,
                content_type=request.content_type,
                body=request.body,
                title=request.title,
            )
        )
        audience_input = (
            request.audience
            if isinstance(request.audience, AudienceProfileInput)
            else AudienceProfileInput(**request.audience)
        )
        audience_result = self.audience_service.validate_profile(audience_input)
        feature_bundle = self.feature_service.extract_text_features(
            asset=ingestion_result.asset,
            segments=ingestion_result.segments,
        )
        scoring_result = self.scoring_service.score_text(
            asset=ingestion_result.asset,
            segments=ingestion_result.segments,
            audience_profile=audience_result.profile,
            modifier_context=audience_result.modifier_context,
            features=feature_bundle,
        )
        analysis_run_id = self._stable_id(
            "analysis",
            ingestion_result.asset.asset_id,
            audience_result.profile.audience_profile_id,
        )
        analysis_run = AnalysisRun(
            analysis_run_id=analysis_run_id,
            project_id=request.project_id,
            asset_id=ingestion_result.asset.asset_id,
            audience_profile_id=audience_result.profile.audience_profile_id,
            status="completed",
            score_vector=scoring_result.score_vector,
            segment_score_vectors=scoring_result.segment_score_vectors,
            notes=["baseline_analysis_pipeline_v1"],
            lineage=ArtifactLineage(
                source_project_id=request.project_id,
                source_asset_id=ingestion_result.asset.asset_id,
            ),
        )
        report = self._build_report(analysis_run=analysis_run, segments=ingestion_result.segments)
        return TextAnalysisResult(
            asset=ingestion_result.asset,
            segments=ingestion_result.segments,
            audience_profile=audience_result.profile,
            feature_bundle=feature_bundle,
            analysis_run=analysis_run,
            report=report,
        )

    def _build_report(self, analysis_run: AnalysisRun, segments: list) -> AnalysisReport:
        sorted_scores = sorted(analysis_run.score_vector.scores, key=lambda score: score.value, reverse=True)
        strongest = [score.dimension for score in sorted_scores[:2]]
        weakest = [score.dimension for score in sorted_scores[-2:]]
        risk_flags = []
        if any(score.dimension == "cognitive_load" and score.value > 0.65 for score in sorted_scores):
            risk_flags.append("High cognitive load may reduce retention.")
        if any(score.dimension == "trust" and score.value < 0.5 for score in sorted_scores):
            risk_flags.append("Trust is weak for the intended audience.")

        highlight_segments = [segment for segment in segments if getattr(segment, "kind", None) == "paragraph"][:2]
        highlights = [
            SegmentHighlight(
                segment_id=segment.segment_id,
                label="highlight",
                reason="Representative paragraph for the current score profile.",
            )
            for segment in highlight_segments
        ]

        summary = (
            f"Baseline analysis completed with strongest dimensions in {', '.join(strongest)} "
            f"and weakest dimensions in {', '.join(weakest)}."
        )
        return AnalysisReport(
            report_id=self._stable_id("report", analysis_run.analysis_run_id),
            analysis_run_id=analysis_run.analysis_run_id,
            summary=summary,
            strongest_dimensions=strongest,
            weakest_dimensions=weakest,
            risk_flags=risk_flags,
            segment_highlights=highlights,
            lineage=ArtifactLineage(
                source_asset_id=analysis_run.asset_id,
                source_analysis_run_id=analysis_run.analysis_run_id,
            ),
        )

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

