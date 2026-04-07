from pathlib import Path

from neuro_tribe.adapter import TribeAdapter, TribeAdapterSettings


def test_tribe_adapter_reads_runtime_status_from_setup_artifacts(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "setup"
    artifacts.mkdir(parents=True)
    (artifacts / "latest.json").write_text(
        """
        {
          "mode": "tribe_degraded",
          "python_version_ok": true,
          "tribe_repo_present": true,
          "tribe_commit": "abc123",
          "tribe_install_ok": true,
          "pretrained_load_ok": true,
          "smoke_test_ok": false
        }
        """,
        encoding="utf-8",
    )

    adapter = TribeAdapter(TribeAdapterSettings(repo_root=tmp_path))
    status = adapter.get_runtime_status()

    assert status.mode == "tribe_degraded"
    assert status.tribe_commit == "abc123"
    assert status.available_for_fusion is False

