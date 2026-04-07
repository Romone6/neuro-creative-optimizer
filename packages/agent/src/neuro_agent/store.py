from __future__ import annotations

import json
from pathlib import Path


class AgentStore:
    def __init__(self, repo_root: Path) -> None:
        self.root = repo_root / "artifacts" / "agent"
        self.root.mkdir(parents=True, exist_ok=True)

    def load_approvals(self, project_id: str) -> list[dict]:
        path = self.root / f"{project_id}-approvals.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def save_approvals(self, project_id: str, approvals: list[dict]) -> None:
        path = self.root / f"{project_id}-approvals.json"
        path.write_text(json.dumps(approvals, indent=2, sort_keys=True), encoding="utf-8")
