from __future__ import annotations

from hashlib import sha1

from neuro_core import (
    ArtifactLineage,
    AudienceProfile,
    ConfidenceSummary,
    ContentAsset,
    ContentSegment,
    ScoreEvidence,
    ScoreValue,
    ScoreVector,
    SegmentScoreVector,
    TextFeatureBundle,
)


class ScoringResult:
    def __init__(self, score_vector: ScoreVector, segment_score_vectors: list[SegmentScoreVector]) -> None:
        self.score_vector = score_vector
        self.segment_score_vectors = segment_score_vectors


class ScoringService:
    def score_text(
        self,
        asset: ContentAsset,
        segments: list[ContentSegment],
        audience_profile: AudienceProfile,
        modifier_context: dict[str, object],
        features: TextFeatureBundle,
    ) -> ScoringResult:
        paragraph_segments = [segment for segment in segments if segment.kind == "paragraph"]
        strongest_segment = max(paragraph_segments or segments, key=lambda s: len(s.text))
        question_segment = next((segment for segment in segments if "?" in segment.text), strongest_segment)

        clarity = self._clamp(0.9 - (features.avg_sentence_length / 25) - features.long_sentence_ratio * 0.2)
        trust = self._clamp(0.42 + features.trust_term_count * 0.09 + features.unique_token_ratio * 0.2)
        urgency = self._clamp(0.25 + features.urgency_term_count * 0.15 + features.question_count * 0.08)
        novelty = self._clamp(0.3 + features.unique_token_ratio * 0.5 - features.repeated_token_ratio * 0.15)
        cognitive_load = self._clamp(0.25 + (features.avg_sentence_length / 30) + features.long_sentence_ratio * 0.3)
        narrative_momentum = self._clamp(0.35 + min(features.paragraph_count, 4) * 0.08 + urgency * 0.2)

        target_dimensions = modifier_context.get("target_dimensions", {})
        if isinstance(target_dimensions, dict):
            trust_goal = target_dimensions.get("trust")
            if isinstance(trust_goal, dict):
                trust = self._clamp(trust + 0.04)

        confidence_summary = ConfidenceSummary(
            overall_confidence=0.74,
            low_confidence_dimensions=["novelty"] if novelty < 0.45 else [],
            notes=["baseline_heuristic_scoring_v1"],
        )

        score_vector = ScoreVector(
            score_vector_id=self._stable_id("score_vector", asset.asset_id, audience_profile.audience_profile_id),
            asset_id=asset.asset_id,
            confidence_summary=confidence_summary,
            scores=[
                self._score("clarity", clarity, strongest_segment, "Sentence length and structure drive readability."),
                self._score("trust", trust, strongest_segment, "Specific and concrete language improves credibility."),
                self._score("urgency", urgency, question_segment, "Calls to action and pressure cues increase urgency."),
                self._score("novelty", novelty, strongest_segment, "Lexical variety acts as a novelty prior."),
                self._score(
                    "cognitive_load",
                    cognitive_load,
                    strongest_segment,
                    "Longer and denser phrasing increases processing effort.",
                ),
                self._score(
                    "narrative_momentum",
                    narrative_momentum,
                    strongest_segment,
                    "Pacing and forward motion are inferred from segment progression.",
                ),
            ],
        )

        segment_score_vectors = [
            SegmentScoreVector(
                segment_id=segment.segment_id,
                scores=[
                    ScoreValue(
                        dimension="clarity",
                        value=self._clamp(0.92 - (len(segment.text.split()) / 28)),
                        confidence=0.68,
                        explanation="Segment-level clarity estimate from local density.",
                        evidence=[
                            ScoreEvidence(
                                segment_id=segment.segment_id,
                                quote=segment.text,
                                start_char=segment.start_char,
                                end_char=segment.end_char,
                                reason="Direct segment evidence.",
                            )
                        ],
                    )
                ],
            )
            for segment in paragraph_segments
        ]

        return ScoringResult(score_vector=score_vector, segment_score_vectors=segment_score_vectors)

    def _score(self, dimension: str, value: float, segment: ContentSegment, explanation: str) -> ScoreValue:
        return ScoreValue(
            dimension=dimension,
            value=value,
            confidence=0.72 if dimension != "novelty" else 0.61,
            explanation=explanation,
            evidence=[
                ScoreEvidence(
                    segment_id=segment.segment_id,
                    quote=segment.text,
                    start_char=segment.start_char,
                    end_char=segment.end_char,
                    reason=f"{dimension} evidence selected from a representative segment.",
                )
            ],
        )

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 4)))

