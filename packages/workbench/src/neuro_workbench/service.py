from __future__ import annotations

from hashlib import sha1
from pathlib import Path

from neuro_analysis.optimization import OptimizationService, TextOptimizationRequest
from neuro_evaluation import EvaluationService, TextEvaluationRequest
from neuro_workbench.schemas import (
    AudiencePreset,
    DiffRecord,
    ExperimentNotebookEntry,
    ProjectDashboard,
    ProjectHistoryEntry,
    SavedScoreProfile,
    WorkbenchEvaluationRecordResult,
    WorkbenchOptimizationRecordResult,
)
from neuro_workbench.store import WorkbenchStore


class WorkbenchService:
    def __init__(
        self,
        repo_root: Path,
        optimization_service: OptimizationService | None = None,
        evaluation_service: EvaluationService | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.optimization_service = optimization_service or OptimizationService()
        self.evaluation_service = evaluation_service or EvaluationService()
        self.store = WorkbenchStore(repo_root)

    def save_audience_preset(self, project_id: str, preset_name: str, audience: dict) -> AudiencePreset:
        preset = AudiencePreset(
            preset_id=self._stable_id("audience_preset", project_id, preset_name),
            project_id=project_id,
            preset_name=preset_name,
            audience=audience,
        )
        payload = self.store.load_project(project_id)
        payload["audience_presets"].append(preset.model_dump(mode="json"))
        self.store.save_project(project_id, payload)
        return preset

    def record_optimization(self, request: TextOptimizationRequest) -> WorkbenchOptimizationRecordResult:
        result = self.optimization_service.optimize_text(request)
        payload = self.store.load_project(request.project_id)

        history_entry = ProjectHistoryEntry(
            entry_id=self._stable_id("history", request.project_id, result.optimization_result.optimization_run_id if hasattr(result, "optimization_result") else result.optimization_run.optimization_run_id),
            project_id=request.project_id,
            run_type="optimization",
            run_id=result.optimization_run.optimization_run_id,
            summary=result.optimization_report.summary,
            recommended_target_id=result.optimization_report.recommended_variant_id,
        )
        score_profiles = self._build_score_profiles(request.project_id, result)
        diff_records = self._build_diff_records(request.project_id, result)
        notebook_entry = ExperimentNotebookEntry(
            notebook_id=self._stable_id("notebook", request.project_id, result.optimization_run.optimization_run_id),
            project_id=request.project_id,
            source_run_id=result.optimization_run.optimization_run_id,
            notebook_type="optimization",
            summary=result.optimization_report.summary,
            highlights=[comparison.summary for comparison in result.optimization_report.comparisons[:3]],
        )

        payload["history_entries"].append(history_entry.model_dump(mode="json"))
        payload["score_profiles"].extend(profile.model_dump(mode="json") for profile in score_profiles)
        payload["diff_records"].extend(diff_record.model_dump(mode="json") for diff_record in diff_records)
        payload["experiment_notebooks"].append(notebook_entry.model_dump(mode="json"))
        self.store.save_project(request.project_id, payload)

        return WorkbenchOptimizationRecordResult(
            optimization_result=result,
            history_entry=history_entry,
            score_profiles=score_profiles,
            diff_records=diff_records,
            notebook_entry=notebook_entry,
        )

    def record_evaluation(self, request: TextEvaluationRequest) -> WorkbenchEvaluationRecordResult:
        result = self.evaluation_service.evaluate_text(request)
        payload = self.store.load_project(request.project_id)
        history_entry = ProjectHistoryEntry(
            entry_id=self._stable_id("history", request.project_id, result.evaluation_run.evaluation_run_id),
            project_id=request.project_id,
            run_type="evaluation",
            run_id=result.evaluation_run.evaluation_run_id,
            summary=result.evaluation_report.summary,
            recommended_target_id=result.experiment_run.recommended_target_id,
        )
        notebook_entry = ExperimentNotebookEntry(
            notebook_id=self._stable_id("notebook", request.project_id, result.experiment_run.experiment_run_id),
            project_id=request.project_id,
            source_run_id=result.experiment_run.experiment_run_id,
            notebook_type="evaluation",
            summary=result.evaluation_report.summary,
            highlights=[
                result.evaluation_report.preference_summary,
                result.evaluation_report.calibration_summary,
            ],
        )
        payload["history_entries"].append(history_entry.model_dump(mode="json"))
        payload["experiment_notebooks"].append(notebook_entry.model_dump(mode="json"))
        self.store.save_project(request.project_id, payload)
        return WorkbenchEvaluationRecordResult(
            evaluation_result=result,
            history_entry=history_entry,
            notebook_entry=notebook_entry,
        )

    def get_project_dashboard(self, project_id: str) -> ProjectDashboard:
        payload = self.store.load_project(project_id)
        history_entries = [ProjectHistoryEntry(**entry) for entry in payload["history_entries"]]
        audience_presets = [AudiencePreset(**preset) for preset in payload["audience_presets"]]
        last_recommended_target_id = next(
            (entry.recommended_target_id for entry in reversed(history_entries) if entry.recommended_target_id),
            None,
        )
        return ProjectDashboard(
            project_id=project_id,
            total_history_entries=len(history_entries),
            audience_preset_count=len(audience_presets),
            saved_score_profile_count=len(payload["score_profiles"]),
            diff_record_count=len(payload["diff_records"]),
            experiment_notebook_count=len(payload["experiment_notebooks"]),
            optimization_run_count=sum(1 for entry in history_entries if entry.run_type == "optimization"),
            evaluation_run_count=sum(1 for entry in history_entries if entry.run_type == "evaluation"),
            recent_history=history_entries[-5:],
            audience_presets=audience_presets[-5:],
            last_recommended_target_id=last_recommended_target_id,
            notes=["workbench_dashboard_v1"],
        )

    def _build_score_profiles(self, project_id: str, result) -> list[SavedScoreProfile]:
        profiles = [
            SavedScoreProfile(
                profile_id=self._stable_id("score_profile", project_id, result.original_analysis.analysis_run.analysis_run_id),
                project_id=project_id,
                target_id=result.original_analysis.asset.asset_id,
                label="original",
                scores={score.dimension: score.value for score in result.original_analysis.analysis_run.score_vector.scores},
            )
        ]
        for variant, analysis in zip(result.variants, result.variant_analyses, strict=True):
            profiles.append(
                SavedScoreProfile(
                    profile_id=self._stable_id("score_profile", project_id, variant.variant_id),
                    project_id=project_id,
                    target_id=variant.variant_id,
                    label=variant.variant_id,
                    scores={score.dimension: score.value for score in analysis.analysis_run.score_vector.scores},
                )
            )
        return profiles

    def _build_diff_records(self, project_id: str, result) -> list[DiffRecord]:
        source_words = result.original_analysis.asset.body.split()
        source_word_set = set(source_words)
        diff_records: list[DiffRecord] = []
        for variant in result.variants:
            target_words = variant.body.split()
            target_word_set = set(target_words)
            added = len(target_word_set - source_word_set)
            removed = len(source_word_set - target_word_set)
            diff_records.append(
                DiffRecord(
                    diff_id=self._stable_id("diff", project_id, variant.variant_id),
                    project_id=project_id,
                    source_target_id=result.original_analysis.asset.asset_id,
                    target_id=variant.variant_id,
                    added_word_count=added,
                    removed_word_count=removed,
                    summary=variant.diff_summary,
                )
            )
        return diff_records

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"
