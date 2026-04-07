from fastapi.testclient import TestClient

from neuro_api.main import app


def test_tribe_analysis_endpoint_returns_response() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/analyze/text/tribe",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": {
                "label": "General audience",
                "platform_context": "general",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "mode" in payload
    assert "source_type" in payload
