from __future__ import annotations

from neuro_analysis import AnalysisService, TextAnalysisRequest
from neuro_core import ArtifactLineage

from neuro_audio.alignment import AudioAlignmentService
from neuro_audio.features import AcousticFeatureService
from neuro_audio.scoring import AudioScoringService
from neuro_audio.schemas import AudioAnalysisRequest, AudioAnalysisResult


class AudioAnalysisService:
    def __init__(
        self,
        alignment_service: AudioAlignmentService | None = None,
        feature_service: AcousticFeatureService | None = None,
        scoring_service: AudioScoringService | None = None,
        text_analysis_service: AnalysisService | None = None,
    ) -> None:
        self.alignment_service = alignment_service or AudioAlignmentService()
        self.feature_service = feature_service or AcousticFeatureService()
        self.scoring_service = scoring_service or AudioScoringService()
        self.text_analysis_service = text_analysis_service or AnalysisService()

    def analyze(self, request: AudioAnalysisRequest) -> AudioAnalysisResult:
        alignment = self.alignment_service.align(request)
        text_analysis = self.text_analysis_service.analyze_text(
            TextAnalysisRequest(
                project_id=request.project_id,
                content_type="lyrics",
                body=request.transcript,
                title=request.title,
                audience=request.audience,
            )
        )
        features = self.feature_service.extract(alignment)
        scorecard, timeline, comparison, report = self.scoring_service.score(
            alignment=alignment,
            features=features,
            text_analysis=text_analysis,
        )
        return AudioAnalysisResult(
            lineage=ArtifactLineage(
                source_project_id=request.project_id,
                source_asset_id=alignment.asset.asset_id,
                source_analysis_run_id=text_analysis.analysis_run.analysis_run_id,
            ),
            asset=alignment.asset,
            aligned_sections=alignment.sections,
            acoustic_features=features,
            text_analysis=text_analysis,
            audio_scorecard=scorecard,
            timeline=timeline,
            section_comparison=comparison,
            report=report,
        )
