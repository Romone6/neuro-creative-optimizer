from __future__ import annotations

from hashlib import sha1

from neuro_analysis.analysis import TextAnalysisResult

from neuro_audio.schemas import (
    AcousticFeatureBundle,
    AudioAlignmentResult,
    AudioAnalysisReport,
    AudioDimensionScore,
    AudioScorecard,
    AudioTimeline,
    SectionComparisonItem,
    SectionComparisonReport,
)


class AudioScoringService:
    def score(
        self,
        alignment: AudioAlignmentResult,
        features: AcousticFeatureBundle,
        text_analysis: TextAnalysisResult,
    ) -> tuple[AudioScorecard, AudioTimeline, SectionComparisonReport, AudioAnalysisReport]:
        clarity = self._dimension_value(text_analysis, "clarity")
        novelty = self._dimension_value(text_analysis, "novelty")
        hook_strength = self._clamp(
            0.35 + (0.18 if features.hook_section_label == "chorus" else 0.08) + features.avg_energy * 0.18 + features.repetition_ratio * 0.24
        )
        emotional_pacing = self._clamp(
            0.3 + features.energy_variability * 0.25 + features.loudness_variability * 0.18 + self._average_release(features) * 0.22
        )
        section_contrast = self._clamp(0.25 + features.energy_variability * 0.3 + features.avg_spectral_contrast * 0.18)
        release_payoff = self._clamp(0.24 + self._max_release(features) * 0.4 + (0.1 if features.hook_section_label else 0.0))
        memorability = self._clamp(0.28 + hook_strength * 0.32 + novelty * 0.14 + features.repetition_ratio * 0.18)

        scorecard = AudioScorecard(
            scorecard_id=self._stable_id("audio_scorecard", alignment.asset.asset_id),
            asset_id=alignment.asset.asset_id,
            dimension_scores=[
                AudioDimensionScore(dimension="lyric_clarity", value=clarity, explanation="Transcript clarity inherited from the text analysis path."),
                AudioDimensionScore(dimension="hook_strength", value=hook_strength, explanation="Hook strength is driven by chorus candidacy, repetition, and section lift."),
                AudioDimensionScore(dimension="emotional_pacing", value=emotional_pacing, explanation="Energy and loudness variation create movement across sections."),
                AudioDimensionScore(dimension="section_contrast", value=section_contrast, explanation="Contrast estimates how clearly sections differentiate from each other."),
                AudioDimensionScore(dimension="release_payoff", value=release_payoff, explanation="Release payoff tracks whether later sections cash in the build."),
                AudioDimensionScore(dimension="memorability", value=memorability, explanation="Memorability blends lyrical novelty with a strong repeated hook."),
            ],
            notes=["audio_scoring_v1"],
        )
        comparison = self._compare_sections(alignment, features)
        report = self._build_report(features, comparison, scorecard)
        return scorecard, AudioTimeline(points=features.tension_timeline), comparison, report

    def _compare_sections(
        self,
        alignment: AudioAlignmentResult,
        features: AcousticFeatureBundle,
    ) -> SectionComparisonReport:
        section_scores = []
        for section, point in zip(alignment.sections, features.tension_timeline, strict=False):
            hook_bonus = 0.08 if section.is_hook_candidate else 0.0
            score = self._clamp(section.energy * 0.32 + section.loudness * 0.24 + section.spectral_contrast * 0.18 + point.release * 0.18 + hook_bonus)
            section_scores.append(
                SectionComparisonItem(
                    section_id=section.section_id,
                    label=section.label,
                    section_score=score,
                    summary=f"{section.label} carries energy={section.energy:.2f}, loudness={section.loudness:.2f}, release={point.release:.2f}.",
                )
            )
        strongest = max(section_scores, key=lambda item: item.section_score, default=None)
        weakest = min(section_scores, key=lambda item: item.section_score, default=None)
        chorus = next((item for item in section_scores if item.label.lower() == "chorus"), None)
        verse = next((item for item in section_scores if item.label.lower() == "verse"), None)
        chorus_vs_verse_summary = None
        if chorus and verse:
            delta = round(chorus.section_score - verse.section_score, 4)
            chorus_vs_verse_summary = f"Chorus outperforms verse by {delta} on the current section score." if delta >= 0 else f"Verse outperforms chorus by {abs(delta)} on the current section score."

        summary = "Section comparison highlights where the song currently peaks and where it needs stronger lift."
        return SectionComparisonReport(
            summary=summary,
            strongest_section_label=strongest.label if strongest else None,
            weakest_section_label=weakest.label if weakest else None,
            chorus_vs_verse_summary=chorus_vs_verse_summary,
            items=section_scores,
        )

    def _build_report(
        self,
        features: AcousticFeatureBundle,
        comparison: SectionComparisonReport,
        scorecard: AudioScorecard,
    ) -> AudioAnalysisReport:
        recommendations: list[str] = []
        risk_flags: list[str] = []
        if features.hook_section_label != "chorus":
            recommendations.append("Strengthen the chorus or refrain so the hook becomes the obvious focal section.")
        if features.energy_variability < 0.12:
            recommendations.append("Increase dynamic contrast between sections to create clearer lift and release.")
        if self._dimension_from_scorecard(scorecard, "release_payoff") < 0.58:
            recommendations.append("Push more payoff into the late section so the build resolves more decisively.")
        if self._dimension_from_scorecard(scorecard, "lyric_clarity") < 0.5:
            risk_flags.append("Lyric clarity is low enough to blunt memorability.")
        if comparison.weakest_section_label:
            recommendations.append(f"Rewrite or re-arrange the {comparison.weakest_section_label} to better support the chorus.")
        summary = (
            f"Audio analysis found the strongest section in {comparison.strongest_section_label or 'the current hook'} "
            f"with overall hook focus on {features.hook_section_label or 'an unlabeled section'}."
        )
        return AudioAnalysisReport(
            summary=summary,
            recommendations=recommendations,
            risk_flags=risk_flags,
        )

    def _dimension_value(self, text_analysis: TextAnalysisResult, dimension: str) -> float:
        for score in text_analysis.analysis_run.score_vector.scores:
            if score.dimension == dimension:
                return score.value
        return 0.0

    def _dimension_from_scorecard(self, scorecard: AudioScorecard, dimension: str) -> float:
        for score in scorecard.dimension_scores:
            if score.dimension == dimension:
                return score.value
        return 0.0

    def _average_release(self, features: AcousticFeatureBundle) -> float:
        releases = [point.release for point in features.tension_timeline]
        return sum(releases) / len(releases) if releases else 0.0

    def _max_release(self, features: AcousticFeatureBundle) -> float:
        return max((point.release for point in features.tension_timeline), default=0.0)

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 4)))
