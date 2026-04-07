from __future__ import annotations

import json
from pathlib import Path


class WorkbenchStore:
    def __init__(self, repo_root: Path) -> None:
        self.root = repo_root / "artifacts" / "workbench"
        self.root.mkdir(parents=True, exist_ok=True)

    def load_project(self, project_id: str) -> dict[str, list[dict]]:
        path = self._path(project_id)
        if not path.exists():
            return self._empty_payload()
        return json.loads(path.read_text(encoding="utf-8"))

    def save_project(self, project_id: str, payload: dict[str, list[dict]]) -> None:
        path = self._path(project_id)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _path(self, project_id: str) -> Path:
        return self.root / f"{project_id}.json"

    def _empty_payload(self) -> dict[str, list[dict]]:
        return {
            "audience_presets": [],
            "history_entries": [],
            "score_profiles": [],
            "diff_records": [],
            "experiment_notebooks": [],
        }

