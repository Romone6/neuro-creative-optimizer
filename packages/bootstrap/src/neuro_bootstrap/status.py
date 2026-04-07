from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class SetupStatus(BaseModel):
    python_version_ok: bool
    python_version: str
    tribe_repo_present: bool
    tribe_commit: str | None
    tribe_install_ok: bool
    pretrained_load_ok: bool
    smoke_test_ok: bool
    mode: str


def build_setup_status(
    repo_root: Path,
    python_version: str,
    tribe_install_ok: bool,
    pretrained_load_ok: bool,
    smoke_test_ok: bool,
) -> SetupStatus:
    tribe_git_dir = repo_root / "third_party" / "tribev2" / ".git"
    tribe_repo_present = tribe_git_dir.exists()
    tribe_commit = _read_tribe_commit(tribe_git_dir) if tribe_repo_present else None
    python_version_ok = _python_version_ok(python_version)

    if tribe_repo_present and tribe_install_ok and pretrained_load_ok and smoke_test_ok:
        mode = "tribe_enabled"
    elif tribe_repo_present or tribe_install_ok or pretrained_load_ok or smoke_test_ok:
        mode = "tribe_degraded"
    else:
        mode = "baseline_only"

    return SetupStatus(
        python_version_ok=python_version_ok,
        python_version=python_version,
        tribe_repo_present=tribe_repo_present,
        tribe_commit=tribe_commit,
        tribe_install_ok=tribe_install_ok,
        pretrained_load_ok=pretrained_load_ok,
        smoke_test_ok=smoke_test_ok,
        mode=mode,
    )


def write_setup_status_artifact(repo_root: Path, status: SetupStatus) -> Path:
    artifact_path = repo_root / "artifacts" / "setup" / "latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(status.model_dump(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path


def _python_version_ok(python_version: str) -> bool:
    parts = python_version.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    return (major, minor) >= (3, 11)


def _read_tribe_commit(git_dir: Path) -> str | None:
    head_path = git_dir / "HEAD"
    if not head_path.exists():
        return None

    head_text = head_path.read_text(encoding="utf-8").strip()
    if head_text.startswith("ref:"):
        ref_path = git_dir / head_text.split(":", maxsplit=1)[1].strip()
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        return None

    return head_text or None
