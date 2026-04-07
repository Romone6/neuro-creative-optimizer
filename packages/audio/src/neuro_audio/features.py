from __future__ import annotations

from hashlib import sha1

from neuro_audio.schemas import AcousticFeatureBundle, AudioAlignmentResult, TensionTimelinePoint


class AcousticFeatureService:
    def extract(self, alignment: AudioAlignmentResult) -> AcousticFeatureBundle:
        sections = alignment.sections
        section_count = len(sections)
        avg_energy = self._average([section.energy for section in sections])
        avg_loudness = self._average([section.loudness for section in sections])
        avg_spectral_contrast = self._average([section.spectral_contrast for section in sections])
        energy_variability = min(1.0, self._average([abs(section.energy - avg_energy) for section in sections]) * 2)
        loudness_variability = min(1.0, self._average([abs(section.loudness - avg_loudness) for section in sections]) * 2)
        repetition_ratio = self._repetition_ratio(sections)
        tension_timeline = self._build_timeline(sections)
        hook_section = max(
            sections,
            key=lambda section: (
                0.2 if section.is_hook_candidate else 0.0
            ) + section.energy * 0.45 + section.loudness * 0.3 + section.spectral_contrast * 0.25,
            default=None,
        )
        return AcousticFeatureBundle(
            feature_bundle_id=self._stable_id("audio_features", alignment.asset.asset_id),
            asset_id=alignment.asset.asset_id,
            section_count=section_count,
            duration_ms=alignment.total_duration_ms,
            bpm=alignment.bpm,
            avg_energy=round(avg_energy, 4),
            avg_loudness=round(avg_loudness, 4),
            avg_spectral_contrast=round(avg_spectral_contrast, 4),
            energy_variability=round(energy_variability, 4),
            loudness_variability=round(loudness_variability, 4),
            repetition_ratio=round(repetition_ratio, 4),
            hook_section_label=hook_section.label if hook_section else None,
            tension_timeline=tension_timeline,
            feature_notes=[
                "audio_feature_pipeline_v1",
                f"sections={section_count}",
            ],
        )

    def _build_timeline(self, sections) -> list[TensionTimelinePoint]:
        timeline: list[TensionTimelinePoint] = []
        previous_tension = 0.0
        for section in sections:
            hook_bonus = 0.08 if section.is_hook_candidate else 0.0
            build_bonus = 0.06 if section.label.lower() in {"pre_chorus", "build"} else 0.0
            tension = min(
                1.0,
                section.energy * 0.42 + section.loudness * 0.28 + section.spectral_contrast * 0.22 + hook_bonus + build_bonus,
            )
            release = min(1.0, max(0.0, tension - previous_tension + (0.08 if section.is_hook_candidate else 0.0)))
            timeline.append(
                TensionTimelinePoint(
                    section_id=section.section_id,
                    label=section.label,
                    start_ms=section.start_ms,
                    end_ms=section.end_ms,
                    tension=round(tension, 4),
                    release=round(release, 4),
                )
            )
            previous_tension = tension
        return timeline

    def _average(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _repetition_ratio(self, sections) -> float:
        if not sections:
            return 0.0
        normalized = [" ".join(section.lyrics.lower().split()) for section in sections]
        unique = len(set(normalized))
        return 1 - (unique / len(normalized))

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
