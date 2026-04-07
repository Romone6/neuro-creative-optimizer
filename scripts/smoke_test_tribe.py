from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def _configure_pythonpath(repo_root: Path) -> None:
    for relative_path in (
        "apps/api/src",
        "packages/bootstrap/src",
        "packages/core/src",
        "packages/llm/src",
    ):
        path = str(repo_root / relative_path)
        if path not in sys.path:
            sys.path.insert(0, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    _configure_pythonpath(repo_root)

    from neuro_bootstrap.status import build_setup_status, write_setup_status_artifact

    tribe_dir = repo_root / "third_party" / "tribev2"
    diagnostics: dict[str, str | bool | None] = {}
    full_smoke_enabled = os.getenv("TRIBE_FULL_SMOKE", "").lower() in {"1", "true", "yes"}

    tribe_install_ok = False
    pretrained_load_ok = False
    smoke_test_ok = False

    try:
        from tribev2 import TribeModel  # type: ignore

        diagnostics["tribe_import_ok"] = True
        tribe_install_ok = True
    except Exception as exc:  # pragma: no cover - exercised via runtime diagnostics
        diagnostics["tribe_import_ok"] = False
        diagnostics["tribe_import_error"] = str(exc)
        TribeModel = None  # type: ignore

    cache_dir = repo_root / "cache" / "tribev2"
    if tribe_install_ok and TribeModel is not None:
        try:
            model = TribeModel.from_pretrained("facebook/tribev2", cache_folder=str(cache_dir))
            diagnostics["pretrained_load_ok"] = True
            pretrained_load_ok = True
            diagnostics["pretrained_model_class"] = model.__class__.__name__
        except Exception as exc:  # pragma: no cover - exercised via runtime diagnostics
            diagnostics["pretrained_load_ok"] = False
            diagnostics["pretrained_load_error"] = str(exc)

    if pretrained_load_ok and full_smoke_enabled:
        try:
            smoke_input_path = repo_root / "artifacts" / "setup" / "smoke-input.txt"
            smoke_input_path.parent.mkdir(parents=True, exist_ok=True)
            smoke_input_path.write_text(
                "This is a TRIBE smoke test for the neuro creative optimizer.",
                encoding="utf-8",
            )

            events = model.get_events_dataframe(text_path=str(smoke_input_path))
            preds, segments = model.predict(events=events, verbose=False)

            diagnostics["events_rows"] = int(len(events))
            diagnostics["predictions_shape"] = list(preds.shape)
            diagnostics["segments_count"] = int(len(segments))
            diagnostics["smoke_test_ok"] = True
            smoke_test_ok = True
        except Exception as exc:  # pragma: no cover - exercised via runtime diagnostics
            diagnostics["smoke_test_ok"] = False
            diagnostics["smoke_test_error"] = str(exc)
    elif pretrained_load_ok:
        diagnostics["smoke_test_skipped"] = True
        diagnostics["smoke_test_skip_reason"] = (
            "Full predict smoke is disabled by default because TRIBE text inference "
            "pulls in a heavy transcription path. Set TRIBE_FULL_SMOKE=1 to run it."
        )

    diagnostics["smoke_test_ok"] = smoke_test_ok
    diagnostics["tribe_repo_dir"] = str(tribe_dir)
    diagnostics["cache_dir"] = str(cache_dir)

    status = build_setup_status(
        repo_root=repo_root,
        python_version=platform.python_version(),
        tribe_install_ok=tribe_install_ok,
        pretrained_load_ok=pretrained_load_ok,
        smoke_test_ok=smoke_test_ok,
    )
    artifact_path = write_setup_status_artifact(repo_root, status)

    diagnostics_path = repo_root / "artifacts" / "setup" / "smoke-test.json"
    diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({"status_path": str(artifact_path), "diagnostics_path": str(diagnostics_path), **status.model_dump()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
