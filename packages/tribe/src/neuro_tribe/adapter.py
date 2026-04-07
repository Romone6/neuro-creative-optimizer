from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from neuro_tribe.schemas import TribeRuntimeStatus


@dataclass(slots=True)
class TribeAdapterSettings:
    repo_root: Path
    status_artifact_relative_path: str = "artifacts/setup/latest.json"
    smoke_artifact_relative_path: str = "artifacts/setup/smoke-test.json"
    fusion_requires_smoke_ok: bool = True


class TribeAdapter:
    def __init__(self, settings: TribeAdapterSettings) -> None:
        self.settings = settings

    def get_runtime_status(self) -> TribeRuntimeStatus:
        artifact = self._read_json(self.settings.repo_root / self.settings.status_artifact_relative_path)
        diagnostics = self._read_json(self.settings.repo_root / self.settings.smoke_artifact_relative_path)

        mode = str(artifact.get("mode", "baseline_only"))
        smoke_test_ok = bool(artifact.get("smoke_test_ok", False))
        pretrained_load_ok = bool(artifact.get("pretrained_load_ok", False))

        available_for_fusion = pretrained_load_ok and (
            smoke_test_ok if self.settings.fusion_requires_smoke_ok else mode == "tribe_enabled"
        )

        notes: list[str] = []
        if artifact:
            notes.append(f"setup_mode={mode}")
        if diagnostics.get("smoke_test_skipped"):
            notes.append(str(diagnostics.get("smoke_test_skip_reason", "smoke_test_skipped")))
        if not pretrained_load_ok:
            notes.append("TRIBE pretrained weights are not available.")
        if pretrained_load_ok and not available_for_fusion:
            notes.append("TRIBE runtime is installed but fusion is running in degraded mode.")

        return TribeRuntimeStatus(
            mode=mode if mode in {"baseline_only", "tribe_degraded", "tribe_enabled"} else "baseline_only",
            tribe_commit=artifact.get("tribe_commit"),
            pretrained_load_ok=pretrained_load_ok,
            available_for_fusion=available_for_fusion,
            notes=notes,
        )

    def _read_json(self, path: Path) -> dict[str, object]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
