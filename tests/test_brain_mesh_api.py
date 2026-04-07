import pytest
from fastapi.testclient import TestClient

from neuro_api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_brain_mesh_endpoint_returns_valid_response(client):
    response = client.get("/v1/brain/mesh?hemisphere=both")
    assert response.status_code == 200

    data = response.json()
    assert "vertices" in data
    assert "faces" in data
    assert "roiLabels" in data
    assert "rois" in data
    assert "hemisphere" in data


def test_brain_mesh_endpoint_returns_mesh_data(client):
    response = client.get("/v1/brain/mesh?hemisphere=both")
    assert response.status_code == 200

    data = response.json()
    assert len(data["vertices"]) > 0
    assert len(data["faces"]) > 0
    assert len(data["roiLabels"]) == 10
    assert len(data["rois"]) == 20  # 10 per hemisphere when both


def test_brain_mesh_endpoint_left_hemisphere(client):
    response = client.get("/v1/brain/mesh?hemisphere=left")
    assert response.status_code == 200

    data = response.json()
    assert data["hemisphere"] == "left"


def test_brain_mesh_endpoint_right_hemisphere(client):
    response = client.get("/v1/brain/mesh?hemisphere=right")
    assert response.status_code == 200

    data = response.json()
    assert data["hemisphere"] == "right"


def test_brain_mesh_vertex_structure(client):
    response = client.get("/v1/brain/mesh?hemisphere=both")
    assert response.status_code == 200

    data = response.json()
    vertex = data["vertices"][0]
    assert "x" in vertex
    assert "y" in vertex
    assert "z" in vertex
    assert isinstance(vertex["x"], (int, float))
    assert isinstance(vertex["y"], (int, float))
    assert isinstance(vertex["z"], (int, float))


def test_brain_mesh_face_structure(client):
    response = client.get("/v1/brain/mesh?hemisphere=both")
    assert response.status_code == 200

    data = response.json()
    face = data["faces"][0]
    assert "a" in face
    assert "b" in face
    assert "c" in face
    assert isinstance(face["a"], int)
    assert isinstance(face["b"], int)
    assert isinstance(face["c"], int)


def test_brain_mesh_roi_structure(client):
    response = client.get("/v1/brain/mesh?hemisphere=both")
    assert response.status_code == 200

    data = response.json()
    roi = data["rois"][0]
    assert "name" in roi
    assert "label" in roi
    assert "activation" in roi
    assert "vertex_indices" in roi
    assert "center" in roi
    assert 0.0 <= roi["activation"] <= 1.0
