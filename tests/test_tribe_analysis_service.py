import pytest

from neuro_tribe.analysis import (
    TribeAnalysisRequest,
    TribeAnalysisService,
    TribeUnavailableError,
)
from neuro_tribe.schemas import TribeRuntimeStatus


def test_tribe_analysis_service_returns_roi_activations() -> None:
    class FakeAdapter:
        def get_runtime_status(self):
            return TribeRuntimeStatus(
                mode="tribe_enabled",
                tribe_commit="abc123",
                pretrained_load_ok=True,
                available_for_fusion=True,
                notes=["test adapter"],
            )

    service = TribeAnalysisService(adapter=FakeAdapter())

    result = service.analyze_text(
        TribeAnalysisRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
            audience={
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
        ),
    )

    assert result.mode == "tribe_enabled"
    assert result.source_type == "text"
    assert len(result.notes) > 0


def test_tribe_analysis_service_maps_scores_to_rois() -> None:
    class FakeAdapter:
        def get_runtime_status(self):
            return TribeRuntimeStatus(
                mode="baseline_only",
                tribe_commit=None,
                pretrained_load_ok=False,
                available_for_fusion=False,
                notes=["baseline mode"],
            )

    service = TribeAnalysisService(adapter=FakeAdapter())

    scores = [
        {"dimension": "trust", "value": 0.8},
        {"dimension": "clarity", "value": 0.6},
        {"dimension": "urgency", "value": 0.7},
    ]

    roi_activations = service.map_scores_to_rois(scores)

    assert len(roi_activations) > 0
    for roi in roi_activations:
        assert roi.name is not None
        assert roi.label is not None
        assert 0.0 <= roi.activation <= 1.0
        assert roi.center is not None
