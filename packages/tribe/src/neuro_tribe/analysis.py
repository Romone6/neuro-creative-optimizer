from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

from neuro_tribe.adapter import TribeAdapter, TribeAdapterSettings
from neuro_tribe.inference import TribeInferenceService
from neuro_tribe.schemas import TribeAnalysisRequest, ROIData, BrainVertex

if TYPE_CHECKING:
    import numpy as np
else:
    import numpy as np

logger = logging.getLogger(__name__)


class TribeUnavailableError(RuntimeError):
    def __init__(self, mode: str, notes: list[str]) -> None:
        self.mode = mode
        self.notes = notes
        super().__init__(
            f"TRIBE v2 live inference is not available in this service. Current mode: {mode}."
        )


class ROIActivation(BaseModel):
    name: str
    label: str
    activation: float
    vertex_indices: list[int]
    center: BrainVertex


class TribeBrainResponse(BaseModel):
    mode: str
    roi_activations: list[ROIActivation]
    source_type: str
    notes: list[str]


SIGNAL_TO_ROI_MAP = {
    "trust": ["frontal"],
    "clarity": ["temporal"],
    "urgency": ["amygdala"],
    "novelty": ["frontal", "parietal"],
    "tension": ["cingulate"],
    "narrative_momentum": ["temporal"],
    "cognitive_load": ["frontal"],
    "memorability": ["hippocampus"],
    "emotional_engagement": ["amygdala"],
}


class TribeAnalysisService:
    def __init__(
        self,
        adapter: TribeAdapter | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self.adapter = adapter or TribeAdapter(
            TribeAdapterSettings(repo_root=repo_root or Path.cwd())
        )
        self._inference_service = TribeInferenceService.get_instance(
            cache_folder=repo_root / "cache" / "tribev2" if repo_root else None
        )
        self._roi_definitions = {
            "frontal": {
                "center": {"x": -30.0, "y": 20.0, "z": 10.0},
                "label": "Frontal Cortex",
            },
            "parietal": {
                "center": {"x": -25.0, "y": -60.0, "z": 45.0},
                "label": "Parietal Cortex",
            },
            "temporal": {
                "center": {"x": -45.0, "y": -30.0, "z": -15.0},
                "label": "Temporal Cortex",
            },
            "occipital": {
                "center": {"x": 0.0, "y": -90.0, "z": 0.0},
                "label": "Occipital Cortex",
            },
            "cingulate": {
                "center": {"x": 0.0, "y": 20.0, "z": 30.0},
                "label": "Cingulate Cortex",
            },
            "insula": {"center": {"x": -35.0, "y": 5.0, "z": 5.0}, "label": "Insula"},
            "amygdala": {
                "center": {"x": -22.0, "y": -5.0, "z": -18.0},
                "label": "Amygdala",
            },
            "hippocampus": {
                "center": {"x": -25.0, "y": -25.0, "z": -12.0},
                "label": "Hippocampus",
            },
            "putamen": {"center": {"x": -24.0, "y": 3.0, "z": 6.0}, "label": "Putamen"},
            "caudate": {
                "center": {"x": -10.0, "y": 15.0, "z": 5.0},
                "label": "Caudate",
            },
        }

    def load_model(self) -> bool:
        return self._inference_service.load_model()

    def analyze_text(self, request: TribeAnalysisRequest) -> TribeBrainResponse:
        runtime_status = self.adapter.get_runtime_status()
        roi_activations: list[ROIActivation] = []
        notes: list[str] = []

        if not self._inference_service.is_available():
            load_ok = self.load_model()
            if not load_ok:
                runtime_status = self.adapter.get_runtime_status()
                notes = [
                    f"Fallback: {runtime_status.mode} mode",
                    "TRIBE model unavailable - using baseline mapping",
                ]
            else:
                notes = ["TRIBE model loaded - running neural inference"]
        else:
            notes = ["TRIBE model ready - running neural inference"]

        if self._inference_service.is_available():
            try:
                text = request.body
                preds, segments = self._inference_service.predict_from_text(text)
                logger.info(
                    f"TRIBE prediction: {preds.shape} segments: {len(segments)}"
                )

                num_vertices = preds.shape[1] if len(preds.shape) > 1 else 20484
                activation_per_vertex = (
                    preds.mean(axis=0) if len(preds.shape) > 1 else preds.flatten()
                )

                roi_activations = self._map_predictions_to_rois(
                    activation_per_vertex, num_vertices
                )
                notes.append(f"TRIBE neural inference: {preds.shape[0]} predictions")
            except Exception as exc:
                logger.error(f"TRIBE inference failed: {exc}")
                notes.append(f"TRIBE inference error: {str(exc)[:50]}")
        else:
            if runtime_status.available_for_fusion:
                notes = [
                    "TRIBE fusion mode - using baseline-derived brain activation mapping"
                ]
            else:
                notes = ["Baseline mode - mapping analysis scores to brain regions"]

        return TribeBrainResponse(
            mode=runtime_status.mode,
            roi_activations=roi_activations,
            source_type="text",
            notes=notes,
        )

    def _map_predictions_to_rois(
        self, predictions: "np.ndarray", num_vertices: int
    ) -> list[ROIActivation]:
        if len(predictions.shape) > 1:
            predictions = predictions.flatten()

        roi_activations = []
        for roi_name, definition in self._roi_definitions.items():
            vertex_indices = self._inference_service.get_roi_vertex_indices(roi_name)

            if vertex_indices:
                valid_indices = [i for i in vertex_indices if i < len(predictions)]
                if valid_indices:
                    activation = float(predictions[valid_indices].mean())
                else:
                    activation = 0.5
            else:
                activation = 0.5

            roi_activations.append(
                ROIActivation(
                    name=roi_name,
                    label=definition.get("label", roi_name.title()),
                    activation=activation,
                    vertex_indices=vertex_indices,
                    center=BrainVertex(
                        **definition.get("center", {"x": 0.0, "y": 0.0, "z": 0.0})
                    ),
                )
            )

        return roi_activations

    def map_scores_to_rois(self, scores: list[dict]) -> list[ROIActivation]:
        roi_values: dict[str, list[float]] = {}

        for score in scores:
            dimension = score.get("dimension", "")
            value = score.get("value", 0.5)

            mapped_rois = SIGNAL_TO_ROI_MAP.get(dimension, [])
            for roi in mapped_rois:
                if roi not in roi_values:
                    roi_values[roi] = []
                roi_values[roi].append(float(value))

        roi_activations = []
        for roi_name, values in roi_values.items():
            definition = self._roi_definitions.get(roi_name, {})
            avg_activation = sum(values) / len(values) if values else 0.5

            vertex_indices = list(
                range(int(avg_activation * 1000), int(avg_activation * 1000) + 500)
            )

            roi_activations.append(
                ROIActivation(
                    name=roi_name,
                    label=definition.get("label", roi_name.title()),
                    activation=avg_activation,
                    vertex_indices=vertex_indices,
                    center=definition.get("center", {"x": 0.0, "y": 0.0, "z": 0.0}),
                )
            )

        return roi_activations

    def get_runtime_status(self):
        return self.adapter.get_runtime_status()
