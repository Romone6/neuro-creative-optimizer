from __future__ import annotations

import json
from pathlib import Path

from neuro_decision.schemas import CommercialCriterion, CommercialDecisionReport
from neuro_workbench import WorkbenchService


class CommercialDecisionService:
    def __init__(self, repo_root: Path, workbench_service: WorkbenchService) -> None:
        self.repo_root = repo_root
        self.workbench_service = workbench_service

    def assess_project(self, project_id: str) -> CommercialDecisionReport:
        dashboard = self.workbench_service.get_project_dashboard(project_id)
        setup = self._read_setup_status()

        criteria = [
            CommercialCriterion(
                name="workflow_usage",
                status="strong" if dashboard.total_history_entries >= 2 else "weak",
                note=f"{dashboard.total_history_entries} recorded workstation runs.",
            ),
            CommercialCriterion(
                name="evaluation_signal",
                status="strong" if dashboard.evaluation_run_count >= 1 else "weak",
                note=f"{dashboard.evaluation_run_count} evaluation run(s) recorded.",
            ),
            CommercialCriterion(
                name="licensing_path",
                status="blocked" if setup.get("tribe_commit") else "clear",
                note="TRIBE-backed path likely needs replacement or relicensing for commercial deployment." if setup.get("tribe_commit") else "No TRIBE artifact detected.",
            ),
        ]

        blockers: list[str] = []
        if dashboard.total_history_entries < 2:
            blockers.append("Not enough repeated usage evidence to claim workstation fit.")
        if dashboard.evaluation_run_count < 1:
            blockers.append("No evaluation evidence is recorded for human trust/alignment.")
        if setup.get("tribe_commit"):
            blockers.append("TRIBE is present and its public stack is non-commercial, so replacement/relicensing is required.")

        if setup.get("tribe_commit") and dashboard.optimization_run_count >= 1 and dashboard.evaluation_run_count >= 1:
            recommendation = "replace_licensed_components_first"
        elif blockers:
            recommendation = "keep_as_research_system"
        else:
            recommendation = "proceed_with_product_hardening"

        next_steps = [
            "Increase evaluation coverage with more human ratings and preference votes.",
            "Track repeat operator usage through the workstation layer.",
        ]
        if setup.get("tribe_commit"):
            next_steps.append("Replace or relicense TRIBE-dependent components before commercial deployment.")

        return CommercialDecisionReport(
            project_id=project_id,
            recommendation=recommendation,
            summary=(
                f"Commercial readiness assessment for {project_id} recommends {recommendation} "
                f"based on usage evidence, evaluation coverage, and licensing constraints."
            ),
            blockers=blockers,
            next_steps=next_steps,
            criteria=criteria,
        )

    def _read_setup_status(self) -> dict[str, object]:
        path = self.repo_root / "artifacts" / "setup" / "latest.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
