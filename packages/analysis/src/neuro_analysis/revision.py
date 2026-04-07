from __future__ import annotations

from hashlib import sha1

from neuro_core import (
    AnalysisRun,
    ArtifactLineage,
    AudienceProfile,
    RevisionInstruction,
    RevisionPlan,
)


class RevisionService:
    def build_plan(
        self,
        asset,
        analysis_run: AnalysisRun,
        audience_profile: AudienceProfile,
    ) -> RevisionPlan:
        sorted_target_goals = sorted(audience_profile.target_goals, key=lambda goal: goal.priority)
        score_by_dimension = {score.dimension: score for score in analysis_run.score_vector.scores}
        weakest_scores = sorted(analysis_run.score_vector.scores, key=lambda score: score.value)[:2]
        dimensions_to_address = []

        for goal in sorted_target_goals:
            if goal.dimension in score_by_dimension:
                dimensions_to_address.append(goal.dimension)
        for score in weakest_scores:
            if score.dimension not in dimensions_to_address:
                dimensions_to_address.append(score.dimension)

        instructions: list[RevisionInstruction] = []
        for priority, dimension in enumerate(dimensions_to_address, start=1):
            score = score_by_dimension.get(dimension)
            evidence_segment_ids = [
                evidence.segment_id
                for evidence in (score.evidence if score else [])
                if evidence.segment_id is not None
            ]
            rationale = (
                score.explanation
                if score is not None
                else f"Improve {dimension} for the intended audience."
            )
            prompt = self._build_instruction_prompt(dimension)
            instructions.append(
                RevisionInstruction(
                    instruction_id=self._stable_id("instruction", analysis_run.analysis_run_id, dimension),
                    dimension=dimension,
                    priority=priority,
                    prompt=prompt,
                    rationale=rationale,
                    segment_ids=evidence_segment_ids,
                )
            )

        return RevisionPlan(
            revision_plan_id=self._stable_id("revision_plan", analysis_run.analysis_run_id),
            asset_id=asset.asset_id,
            analysis_run_id=analysis_run.analysis_run_id,
            target_goals=sorted_target_goals,
            instructions=instructions,
            constraints={"preserve_core_claim": True, "variant_count": 3},
            lineage=ArtifactLineage(
                source_project_id=asset.project_id,
                source_asset_id=asset.asset_id,
                source_analysis_run_id=analysis_run.analysis_run_id,
            ),
        )

    def _build_instruction_prompt(self, dimension: str) -> str:
        prompts = {
            "trust": "Increase concrete proof, reduce overclaiming, and make the value proposition feel credible.",
            "clarity": "Reduce abstraction, simplify phrasing, and make the core claim easier to parse.",
            "urgency": "Sharpen the call to action and compress the path to action without sounding desperate.",
            "novelty": "Introduce fresher phrasing or a more distinctive angle while preserving the message.",
            "cognitive_load": "Reduce processing effort by shortening dense phrasing and clarifying the sequence.",
            "narrative_momentum": "Improve pacing so the message advances cleanly toward a stronger payoff.",
        }
        return prompts.get(dimension, f"Improve the content along the {dimension} dimension.")

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

