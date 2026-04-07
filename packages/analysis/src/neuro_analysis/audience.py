from __future__ import annotations

from hashlib import sha1

from pydantic import BaseModel, Field

from neuro_core import ArtifactLineage, AudienceProfile, TargetResponseGoal


class AudienceProfileInput(BaseModel):
    label: str
    age_band: str | None = None
    cultural_context: str | None = None
    topic_familiarity: str | None = None
    literacy_assumption: str | None = None
    platform_context: str | None = None
    tone_preference: str | None = None
    genre_preference: str | None = None
    brand_affinity: str | None = None
    target_goals: list[TargetResponseGoal] = Field(default_factory=list)


class AudienceValidationResult(BaseModel):
    profile: AudienceProfile
    modifier_context: dict[str, object]


class AudienceService:
    def validate_profile(self, profile_input: AudienceProfileInput) -> AudienceValidationResult:
        normalized_traits = {
            "label": self._clean(profile_input.label),
            "age_band": self._clean(profile_input.age_band),
            "cultural_context": self._clean(profile_input.cultural_context),
            "topic_familiarity": self._clean(profile_input.topic_familiarity),
            "literacy_assumption": self._clean(profile_input.literacy_assumption),
            "platform_context": self._clean(profile_input.platform_context),
            "tone_preference": self._clean(profile_input.tone_preference),
            "genre_preference": self._clean(profile_input.genre_preference),
            "brand_affinity": self._clean(profile_input.brand_affinity),
        }
        goals = sorted(profile_input.target_goals, key=lambda goal: goal.priority)
        audience_profile_id = self._stable_id("aud", normalized_traits["label"], *(goal.dimension for goal in goals))

        profile = AudienceProfile(
            audience_profile_id=audience_profile_id,
            label=normalized_traits["label"] or "Unnamed Audience",
            age_band=normalized_traits["age_band"],
            cultural_context=normalized_traits["cultural_context"],
            topic_familiarity=normalized_traits["topic_familiarity"],
            literacy_assumption=normalized_traits["literacy_assumption"],
            platform_context=normalized_traits["platform_context"],
            tone_preference=normalized_traits["tone_preference"],
            genre_preference=normalized_traits["genre_preference"],
            brand_affinity=normalized_traits["brand_affinity"],
            target_goals=goals,
            lineage=ArtifactLineage(),
        )

        modifier_context = {
            "traits": {key: value for key, value in normalized_traits.items() if key != "label" and value},
            "target_dimensions": {
                goal.dimension: {
                    "target_value": goal.target_value,
                    "priority": goal.priority,
                    "min_delta": goal.min_delta,
                }
                for goal in goals
            },
        }
        return AudienceValidationResult(profile=profile, modifier_context=modifier_context)

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split()).strip()
        return cleaned or None

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

