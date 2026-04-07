from __future__ import annotations

from hashlib import sha1

from neuro_core import ArtifactLineage, ContentAsset

from neuro_audio.schemas import (
    AlignedAudioSection,
    AudioAlignmentResult,
    AudioAnalysisRequest,
)


class AudioAlignmentService:
    def align(self, request: AudioAnalysisRequest) -> AudioAlignmentResult:
        ordered_sections = sorted(request.sections, key=lambda section: section.start_ms)
        aligned_sections = [
            AlignedAudioSection(
                section_id=self._stable_id("audio_section", request.project_id, section.label, section.start_ms),
                label=section.label,
                start_ms=section.start_ms,
                end_ms=section.end_ms,
                duration_ms=section.end_ms - section.start_ms,
                lyrics=section.lyrics.strip(),
                lyric_word_count=len(section.lyrics.split()),
                energy=section.energy,
                loudness=section.loudness,
                spectral_contrast=section.spectral_contrast,
                is_hook_candidate=section.label.lower() in {"chorus", "hook", "drop", "refrain"},
            )
            for section in ordered_sections
        ]
        asset = ContentAsset(
            asset_id=self._stable_id("asset", request.project_id, request.title or request.content_type, request.transcript),
            project_id=request.project_id,
            content_type=request.content_type,
            body=request.transcript.strip(),
            title=request.title,
            source_kind="imported",
            metadata={
                "modality": "audio",
                "section_count": len(aligned_sections),
                "bpm": request.bpm,
            },
            lineage=ArtifactLineage(source_project_id=request.project_id),
        )
        total_duration_ms = max((section.end_ms for section in aligned_sections), default=0)
        return AudioAlignmentResult(
            asset=asset,
            sections=aligned_sections,
            transcript=request.transcript.strip(),
            total_duration_ms=total_duration_ms,
            bpm=request.bpm,
        )

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
