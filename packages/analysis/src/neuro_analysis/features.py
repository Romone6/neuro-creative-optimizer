from __future__ import annotations

from collections import Counter
from hashlib import sha1
import re

from neuro_core import ArtifactLineage, ContentAsset, ContentSegment, TextFeatureBundle

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")
URGENCY_TERMS = {"act", "now", "today", "urgent", "limited", "wait"}
TRUST_TERMS = {"specific", "credible", "proven", "evidence", "trust", "guarantee"}
SENSORY_TERMS = {"see", "hear", "feel", "taste", "touch", "bright", "warm"}


class FeatureService:
    def extract_text_features(
        self,
        asset: ContentAsset,
        segments: list[ContentSegment],
    ) -> TextFeatureBundle:
        tokens = TOKEN_PATTERN.findall(asset.body)
        normalized_tokens = [token.lower() for token in tokens]
        sentence_segments = [segment for segment in segments if segment.kind == "sentence"]
        paragraph_segments = [segment for segment in segments if segment.kind == "paragraph"]

        word_count = len(tokens)
        sentence_count = len(sentence_segments)
        paragraph_count = len(paragraph_segments)
        avg_sentence_length = word_count / sentence_count if sentence_count else 0.0
        avg_word_length = sum(len(token) for token in tokens) / word_count if word_count else 0.0
        question_count = asset.body.count("?")
        exclamation_count = asset.body.count("!")
        uppercase_chars = sum(1 for char in asset.body if char.isupper())
        alpha_chars = sum(1 for char in asset.body if char.isalpha())
        uppercase_ratio = uppercase_chars / alpha_chars if alpha_chars else 0.0

        counter = Counter(normalized_tokens)
        unique_token_ratio = len(counter) / word_count if word_count else 0.0
        repeated_token_ratio = (
            sum(count - 1 for count in counter.values() if count > 1) / word_count if word_count else 0.0
        )
        long_sentence_ratio = (
            sum(1 for segment in sentence_segments if len(TOKEN_PATTERN.findall(segment.text)) >= 18) / sentence_count
            if sentence_count
            else 0.0
        )
        urgency_term_count = sum(counter[term] for term in URGENCY_TERMS)
        trust_term_count = sum(counter[term] for term in TRUST_TERMS)
        sensory_term_count = sum(counter[term] for term in SENSORY_TERMS)

        return TextFeatureBundle(
            feature_bundle_id=self._stable_id("features", asset.asset_id),
            asset_id=asset.asset_id,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            question_count=question_count,
            exclamation_count=exclamation_count,
            uppercase_ratio=uppercase_ratio,
            unique_token_ratio=unique_token_ratio,
            repeated_token_ratio=repeated_token_ratio,
            long_sentence_ratio=long_sentence_ratio,
            urgency_term_count=urgency_term_count,
            trust_term_count=trust_term_count,
            sensory_term_count=sensory_term_count,
            feature_notes=["baseline_text_features_v1"],
            lineage=ArtifactLineage(source_asset_id=asset.asset_id, source_project_id=asset.project_id),
        )

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

