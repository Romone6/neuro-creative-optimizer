from pathlib import Path

from neuro_bootstrap.status import build_setup_status, write_setup_status_artifact


def test_setup_status_defaults_to_baseline_only_without_tribe_assets(tmp_path: Path) -> None:
    status = build_setup_status(
        repo_root=tmp_path,
        python_version="3.11.9",
        tribe_install_ok=False,
        pretrained_load_ok=False,
        smoke_test_ok=False,
    )

    assert status.mode == "baseline_only"
    assert status.tribe_repo_present is False
    assert status.tribe_commit is None


def test_setup_status_enables_tribe_mode_when_all_checks_pass(tmp_path: Path) -> None:
    tribe_repo = tmp_path / "third_party" / "tribev2" / ".git"
    tribe_repo.mkdir(parents=True)
    head_file = tribe_repo / "HEAD"
    head_file.write_text("abcdef1234567890\n", encoding="utf-8")

    status = build_setup_status(
        repo_root=tmp_path,
        python_version="3.11.9",
        tribe_install_ok=True,
        pretrained_load_ok=True,
        smoke_test_ok=True,
    )

    assert status.mode == "tribe_enabled"
    assert status.tribe_repo_present is True
    assert status.tribe_commit == "abcdef1234567890"


def test_setup_status_can_be_persisted_as_json(tmp_path: Path) -> None:
    status = build_setup_status(
        repo_root=tmp_path,
        python_version="3.11.9",
        tribe_install_ok=False,
        pretrained_load_ok=False,
        smoke_test_ok=False,
    )

    artifact_path = write_setup_status_artifact(tmp_path, status)

    assert artifact_path == tmp_path / "artifacts" / "setup" / "latest.json"
    assert artifact_path.exists() is True
    payload = artifact_path.read_text(encoding="utf-8")
    assert '"mode": "baseline_only"' in payload
