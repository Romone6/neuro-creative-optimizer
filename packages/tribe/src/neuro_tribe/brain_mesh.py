from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from neuro_tribe.schemas import (
    BrainFace,
    BrainMeshData,
    BrainMeshResponse,
    BrainVertex,
    ROIData,
)


class BrainMeshService:
    def __init__(self, cache_dir: Path | None = None) -> None:
        self._cache_dir = cache_dir or Path("./cache")
        self._mesh_cache: dict[str, BrainMeshResponse | None] = {}

    def load_fsaverage5_mesh(self, hemisphere: str = "both") -> BrainMeshResponse:
        cache_key = f"fsaverage5_{hemisphere}"
        if cache_key in self._mesh_cache and self._mesh_cache[cache_key] is not None:
            return self._mesh_cache[cache_key]

        try:
            from nilearn.datasets import fetch_surf_fsaverage
            from nilearn.surface import load_surf_mesh
        except ImportError as exc:
            raise RuntimeError("nilearn not installed") from exc

        fsaverage = fetch_surf_fsaverage(mesh="fsaverage5")

        left_mesh = load_surf_mesh(fsaverage["pial_left"])
        right_mesh = load_surf_mesh(fsaverage["pial_right"])

        left_coords, left_faces_data = left_mesh
        right_coords, right_faces_data = right_mesh

        left_vertices = self._serialize_vertices(left_coords)
        left_faces = self._serialize_faces(left_faces_data)

        right_vertices = self._serialize_vertices(right_coords)
        right_faces = self._serialize_faces(right_faces_data)

        roi_labels = self._get_roi_labels()

        left_rois = self._build_default_rois("left", len(left_vertices))
        right_rois = self._build_default_rois("right", len(right_vertices))

        both_vertices = left_vertices + right_vertices
        both_faces = left_faces + [
            BrainFace(
                a=f.a + len(left_vertices),
                b=f.b + len(left_vertices),
                c=f.c + len(left_vertices),
            )
            for f in right_faces
        ]
        both_rois = left_rois + right_rois

        result = BrainMeshResponse(
            mesh=BrainMeshData(
                vertices=both_vertices,
                faces=both_faces,
                rois=both_rois,
                hemisphere="both",
            ),
            left_hemisphere=BrainMeshData(
                vertices=left_vertices,
                faces=left_faces,
                rois=left_rois,
                hemisphere="left",
            ),
            right_hemisphere=BrainMeshData(
                vertices=right_vertices,
                faces=right_faces,
                rois=right_rois,
                hemisphere="right",
            ),
            roi_labels=roi_labels,
        )

        self._mesh_cache[cache_key] = result
        return result

    def load_fsaverage6_mesh(self, hemisphere: str = "both") -> BrainMeshResponse:
        cache_key = f"fsaverage6_{hemisphere}"
        if cache_key in self._mesh_cache and self._mesh_cache[cache_key] is not None:
            return self._mesh_cache[cache_key]

        try:
            from nilearn.datasets import fetch_surf_fsaverage
            from nilearn.surface import load_surf_mesh
        except ImportError as exc:
            raise RuntimeError("nilearn not installed") from exc

        fsaverage = fetch_surf_fsaverage(mesh="fsaverage6")

        left_mesh = load_surf_mesh(fsaverage["pial_left"])
        right_mesh = load_surf_mesh(fsaverage["pial_right"])

        left_coords, left_faces_data = left_mesh
        right_coords, right_faces_data = right_mesh

        left_vertices = self._serialize_vertices(left_coords)
        left_faces = self._serialize_faces(left_faces_data)

        right_vertices = self._serialize_vertices(right_coords)
        right_faces = self._serialize_faces(right_faces_data)

        roi_labels = self._get_roi_labels()

        left_rois = self._build_default_rois("left", len(left_vertices))
        right_rois = self._build_default_rois("right", len(right_vertices))

        both_vertices = left_vertices + right_vertices
        both_faces = left_faces + [
            BrainFace(
                a=f.a + len(left_vertices),
                b=f.b + len(left_vertices),
                c=f.c + len(left_vertices),
            )
            for f in right_faces
        ]
        both_rois = left_rois + right_rois

        return BrainMeshResponse(
            mesh=BrainMeshData(
                vertices=both_vertices,
                faces=both_faces,
                rois=both_rois,
                hemisphere="both",
            ),
            left_hemisphere=BrainMeshData(
                vertices=left_vertices,
                faces=left_faces,
                rois=left_rois,
                hemisphere="left",
            ),
            right_hemisphere=BrainMeshData(
                vertices=right_vertices,
                faces=right_faces,
                rois=right_rois,
                hemisphere="right",
            ),
            roi_labels=roi_labels,
        )

        self._mesh_cache[cache_key] = result
        return result

    def _serialize_vertices(self, coordinates) -> list[BrainVertex]:
        return [
            BrainVertex(x=float(x), y=float(y), z=float(z)) for x, y, z in coordinates
        ]

    def _serialize_faces(self, faces) -> list[BrainFace]:
        return [BrainFace(a=int(a), b=int(b), c=int(c)) for a, b, c in faces]

    def _get_roi_labels(self) -> list[str]:
        return [
            "frontal",
            "parietal",
            "temporal",
            "occipital",
            "cingulate",
            "insula",
            "amygdala",
            "hippocampus",
            "putamen",
            "caudate",
        ]

    def _build_default_rois(self, hemisphere: str, vertex_count: int) -> list[ROIData]:
        roi_definitions = {
            "frontal": {
                "center": (-30, 20, 10) if hemisphere == "left" else (30, 20, 10),
                "label": "Frontal Cortex",
            },
            "parietal": {"center": (-25, -60, 45), "label": "Parietal Cortex"},
            "temporal": {
                "center": (-45, -30, -15) if hemisphere == "left" else (45, -30, -15),
                "label": "Temporal Cortex",
            },
            "occipital": {"center": (0, -90, 0), "label": "Occipital Cortex"},
            "cingulate": {"center": (0, 20, 30), "label": "Cingulate Cortex"},
            "insula": {
                "center": (-35, 5, 5) if hemisphere == "left" else (35, 5, 5),
                "label": "Insula",
            },
            "amygdala": {
                "center": (-22, -5, -18) if hemisphere == "left" else (22, -5, -18),
                "label": "Amygdala",
            },
            "hippocampus": {
                "center": (-25, -25, -12) if hemisphere == "left" else (25, -25, -12),
                "label": "Hippocampus",
            },
            "putamen": {
                "center": (-24, 3, 6) if hemisphere == "left" else (24, 3, 6),
                "label": "Putamen",
            },
            "caudate": {
                "center": (-10, 15, 5) if hemisphere == "left" else (10, 15, 5),
                "label": "Caudate",
            },
        }

        rois = []
        for roi_name, definition in roi_definitions.items():
            cx, cy, cz = definition["center"]
            vertex_indices = self._find_vertices_in_radius(
                np.array([cx, cy, cz]), vertex_count, radius=15.0
            )
            rois.append(
                ROIData(
                    name=roi_name,
                    label=definition["label"],
                    activation=0.0,
                    vertex_indices=vertex_indices,
                    center={"x": cx, "y": cy, "z": cz},
                )
            )
        return rois

    def _find_vertices_in_radius(
        self, center: np.ndarray, vertex_count: int, radius: float = 15.0
    ) -> list[int]:
        mock_vertices = np.random.randn(vertex_count, 3) * 30
        distances = np.linalg.norm(mock_vertices - center, axis=1)
        return sorted(np.where(distances < radius)[0].tolist()[:500])

    def get_mesh_for_frontend(self) -> dict:
        mesh_data = self.load_fsaverage6_mesh("both")
        return {
            "vertices": [v.model_dump() for v in mesh_data.mesh.vertices],
            "faces": [f.model_dump() for f in mesh_data.mesh.faces],
            "roiLabels": mesh_data.roi_labels,
            "rois": [r.model_dump() for r in mesh_data.mesh.rois],
            "hemisphere": "both",
        }
