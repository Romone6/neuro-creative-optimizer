import pytest

from neuro_analysis.ingestion import IngestionError, IngestionService, TextIngestionRequest


def test_ingestion_service_builds_asset_and_segments_from_text() -> None:
    service = IngestionService()

    result = service.ingest_text(
        TextIngestionRequest(
            project_id="project_1",
            content_type="speech",
            title="Draft",
            body="Hello audience.\n\nThis is the second paragraph. It has two sentences.",
        )
    )

    assert result.asset.project_id == "project_1"
    assert result.asset.body == "Hello audience.\n\nThis is the second paragraph. It has two sentences."
    assert [segment.kind for segment in result.segments] == [
        "paragraph",
        "sentence",
        "paragraph",
        "sentence",
        "sentence",
    ]
    assert result.segments[0].text == "Hello audience."
    assert result.segments[-1].text == "It has two sentences."


def test_ingestion_service_rejects_empty_text() -> None:
    service = IngestionService()

    with pytest.raises(IngestionError) as exc:
        service.ingest_text(
            TextIngestionRequest(
                project_id="project_1",
                content_type="speech",
                body="   \n\n  ",
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.code == "content_empty"

