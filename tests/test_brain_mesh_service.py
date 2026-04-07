import pytest
from neuro_tribe.brain_mesh import BrainMeshService


class TestBrainMeshService:
    def test_brain_mesh_service_initializes(self):
        service = BrainMeshService()
        assert service is not None

    def test_load_fsaverage6_mesh_returns_valid_structure(self):
        service = BrainMeshService()
        result = service.load_fsaverage6_mesh("both")

        assert result.mesh is not None
        assert result.left_hemisphere is not None
        assert result.right_hemisphere is not None

        assert len(result.mesh.vertices) > 0
        assert len(result.mesh.faces) > 0
        assert len(result.mesh.rois) > 0

    def test_roi_labels_are_valid(self):
        service = BrainMeshService()
        result = service.load_fsaverage6_mesh("both")

        expected_labels = [
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
        assert result.roi_labels == expected_labels

    def test_rois_have_required_fields(self):
        service = BrainMeshService()
        result = service.load_fsaverage6_mesh("both")

        for roi in result.mesh.rois:
            assert roi.name is not None
            assert roi.label is not None
            assert 0.0 <= roi.activation <= 1.0
            assert len(roi.vertex_indices) > 0
            assert roi.center is not None

    def test_get_mesh_for_frontend_returns_serializable_dict(self):
        service = BrainMeshService()
        result = service.get_mesh_for_frontend()

        assert "vertices" in result
        assert "faces" in result
        assert "roiLabels" in result
        assert "hemisphere" in result
        assert result["hemisphere"] == "both"

        assert isinstance(result["vertices"], list)
        assert isinstance(result["faces"], list)
        assert isinstance(result["roiLabels"], list)

    def test_left_hemisphere_has_fewer_vertices_than_both(self):
        service = BrainMeshService()
        result = service.load_fsaverage6_mesh("both")

        left_count = len(result.left_hemisphere.vertices)
        both_count = len(result.mesh.vertices)

        assert left_count < both_count
        assert left_count > 0
