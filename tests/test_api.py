from fastapi.testclient import TestClient

from neuro_api.main import app


def test_api_exposes_provider_catalogue() -> None:
    client = TestClient(app)

    response = client.get("/v1/llm/providers")

    assert response.status_code == 200
    payload = response.json()
    assert [provider["provider"] for provider in payload["providers"]] == [
        "anthropic",
        "local",
        "openai",
        "openrouter",
    ]


def test_api_exposes_setup_status() -> None:
    client = TestClient(app)

    response = client.get("/v1/setup/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] in {"baseline_only", "tribe_degraded", "tribe_enabled"}


def test_provider_specific_chat_endpoint_exists(monkeypatch) -> None:
    class FakeService:
        def execute(self, request):
            return type(
                "Response",
                (),
                {
                    "provider": request.provider,
                    "model": request.model,
                    "output_text": "provider route ok",
                    "finish_reason": "stop",
                    "transport": "openai_compatible",
                    "raw_response": None,
                },
            )()

    monkeypatch.setattr("neuro_api.main.get_provider_service", lambda: FakeService())
    client = TestClient(app)

    response = client.post(
        "/v1/llm/providers/openrouter/chat",
        json={
            "model": "openrouter/auto",
            "messages": [{"role": "user", "content": "test"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "openrouter"
    assert payload["output_text"] == "provider route ok"


def test_generic_chat_endpoint_routes_provider_requests(monkeypatch) -> None:
    class FakeService:
        def execute(self, request):
            return type(
                "Response",
                (),
                {
                    "provider": request.provider,
                    "model": request.model,
                    "output_text": "generic route ok",
                    "finish_reason": "stop",
                    "transport": "openai_compatible",
                    "raw_response": None,
                },
            )()

    monkeypatch.setattr("neuro_api.main.get_provider_service", lambda: FakeService())
    client = TestClient(app)

    response = client.post(
        "/v1/llm/chat",
        json={
            "provider": "local",
            "model": "llama3.1",
            "messages": [{"role": "user", "content": "test"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "local"
    assert payload["output_text"] == "generic route ok"


def test_text_ingestion_endpoint_returns_asset_and_segments() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/assets/ingest/text",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Hello audience.\n\nThis is the second paragraph.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset"]["project_id"] == "project_1"
    assert len(payload["segments"]) >= 3


def test_audience_validation_endpoint_returns_modifier_context() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/audiences/validate",
        json={
            "label": "Cold traffic founders",
            "platform_context": "linkedin",
            "target_goals": [
                {"dimension": "trust", "target_value": 0.82, "priority": 1}
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["profile"]["label"] == "Cold traffic founders"
    assert payload["modifier_context"]["traits"]["platform_context"] == "linkedin"


def test_prompt_routing_endpoint_returns_default_analysis_route() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/policy/route",
        json={"task_type": "analysis", "quality": "balanced"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] in {"openrouter", "local", "openai", "anthropic"}


def test_text_analysis_endpoint_returns_complete_analysis_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/analyze/text",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_run"]["status"] == "completed"
    assert payload["report"]["summary"]
    assert payload["feature_bundle"]["word_count"] > 0


def test_optimize_text_endpoint_returns_variants_and_rankings() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/optimize/text",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["revision_plan"]["instructions"]
    assert len(payload["variants"]) == 3
    assert len(payload["variant_rankings"]) == 3
    assert payload["optimization_run"]["status"] == "completed"
    assert payload["optimization_report"]["recommended_variant_id"]


def test_evaluate_text_endpoint_returns_evaluation_artifacts() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/evaluate/text",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
            "variants": [
                {
                    "variant_id": "variant_a",
                    "body": "Act now. Here is the concrete promise and why it is credible.",
                }
            ],
            "human_ratings": [
                {
                    "target_id": "original",
                    "rater_id": "r1",
                    "dimension_scores": {"trust": 0.55, "clarity": 0.62},
                },
                {
                    "target_id": "variant_a",
                    "rater_id": "r1",
                    "dimension_scores": {"trust": 0.86, "clarity": 0.71},
                },
            ],
            "preference_votes": [
                {
                    "winner_target_id": "variant_a",
                    "loser_target_id": "original",
                    "rater_id": "r1",
                    "reason": "More credible",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["evaluation_run"]["status"] == "completed"
    assert payload["experiment_run"]["status"] == "completed"
    assert payload["evaluation_report"]["summary"]


def test_tribe_analysis_endpoint_returns_runtime_and_comparison_artifacts() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/analyze/text/tribe",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
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


def test_audio_analysis_endpoint_returns_timeline_and_section_comparison() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/analyze/audio",
        json={
            "project_id": "project_song",
            "content_type": "song_clip",
            "title": "Night Drive",
            "transcript": (
                "City lights are bending in the rain.\n"
                "I keep driving through the same refrain.\n\n"
                "Hold on now, we are rising higher.\n"
                "This is the part that starts the fire."
            ),
            "sections": [
                {
                    "label": "verse",
                    "start_ms": 0,
                    "end_ms": 18000,
                    "lyrics": "City lights are bending in the rain. I keep driving through the same refrain.",
                    "energy": 0.42,
                    "loudness": 0.38,
                    "spectral_contrast": 0.45,
                },
                {
                    "label": "chorus",
                    "start_ms": 18000,
                    "end_ms": 36000,
                    "lyrics": "Hold on now, we are rising higher. This is the part that starts the fire.",
                    "energy": 0.82,
                    "loudness": 0.74,
                    "spectral_contrast": 0.72,
                },
            ],
            "audience": {
                "label": "Indie pop listeners",
                "platform_context": "streaming",
                "target_goals": [
                    {"dimension": "memorability", "target_value": 0.8, "priority": 1}
                ],
            },
            "bpm": 118,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["text_analysis"]["analysis_run"]["status"] == "completed"
    assert payload["audio_scorecard"]["dimension_scores"]
    assert payload["timeline"]["points"]
    assert payload["section_comparison"]["summary"]


def test_workbench_api_records_and_returns_dashboard(tmp_path, monkeypatch) -> None:
    from neuro_workbench.service import WorkbenchService

    service = WorkbenchService(repo_root=tmp_path)
    monkeypatch.setattr("neuro_api.main.get_workbench_service", lambda: service)
    client = TestClient(app)

    preset_response = client.post(
        "/v1/workbench/audience-presets",
        json={
            "project_id": "project_1",
            "preset_name": "cold_traffic_founders",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
        },
    )
    optimize_response = client.post(
        "/v1/workbench/optimize/text",
        json={
            "project_id": "project_1",
            "content_type": "speech",
            "body": "Act now. This offer is specific and credible.\n\nWhy wait?",
            "audience": preset_response.json()["audience"],
        },
    )
    dashboard_response = client.get("/v1/workbench/projects/project_1/dashboard")

    assert preset_response.status_code == 200
    assert optimize_response.status_code == 200
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["total_history_entries"] == 1
    assert payload["audience_preset_count"] == 1
    assert payload["saved_score_profile_count"] >= 1


def test_agent_and_decision_api_endpoints_return_structured_payloads(
    tmp_path, monkeypatch
) -> None:
    from neuro_agent.service import AgentWorkflowService
    from neuro_decision.service import CommercialDecisionService
    from neuro_workbench.service import WorkbenchService

    workbench = WorkbenchService(repo_root=tmp_path)
    agent_service = AgentWorkflowService(repo_root=tmp_path)
    decision_service = CommercialDecisionService(
        repo_root=tmp_path, workbench_service=workbench
    )

    monkeypatch.setattr("neuro_api.main.get_workbench_service", lambda: workbench)
    monkeypatch.setattr(
        "neuro_api.main.get_agent_workflow_service", lambda: agent_service
    )
    monkeypatch.setattr(
        "neuro_api.main.get_commercial_decision_service", lambda: decision_service
    )

    client = TestClient(app)

    campaign_response = client.post(
        "/v1/agent/campaign/optimize",
        json={
            "project_id": "project_campaign",
            "content_type": "ad_copy",
            "audience": {
                "label": "Cold traffic founders",
                "platform_context": "linkedin",
                "target_goals": [
                    {"dimension": "trust", "target_value": 0.82, "priority": 1}
                ],
            },
            "candidates": [
                {
                    "candidate_id": "candidate_a",
                    "body": "Act now. This offer is specific and credible.",
                },
                {
                    "candidate_id": "candidate_b",
                    "body": "Build momentum fast with a concrete reason to believe this works.",
                },
            ],
            "channel_constraints": [{"platform": "linkedin", "max_chars": 140}],
        },
    )
    approval_target = campaign_response.json()["campaign_comparison"][
        "recommended_target_id"
    ]
    approval_response = client.post(
        "/v1/agent/approval",
        json={
            "project_id": "project_campaign",
            "target_id": approval_target,
            "status": "approved",
            "reviewer_id": "editor_1",
            "reason": "Best fit",
        },
    )
    decision_response = client.get("/v1/decision/commercial-readiness/project_campaign")

    assert campaign_response.status_code == 200
    assert campaign_response.json()["campaign_comparison"]["recommended_target_id"]
    assert approval_response.status_code == 200
    assert approval_response.json()["status"] == "approved"
    assert decision_response.status_code == 200
    assert decision_response.json()["summary"]
