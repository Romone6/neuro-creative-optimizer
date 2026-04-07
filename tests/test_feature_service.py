from neuro_analysis.features import FeatureService
from neuro_analysis.ingestion import IngestionService, TextIngestionRequest


def test_feature_service_extracts_stable_text_metrics() -> None:
    ingestion = IngestionService()
    feature_service = FeatureService()
    ingestion_result = ingestion.ingest_text(
        TextIngestionRequest(
            project_id="project_1",
            content_type="speech",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
        )
    )

    bundle = feature_service.extract_text_features(
        asset=ingestion_result.asset,
        segments=ingestion_result.segments,
    )

    assert bundle.word_count == 10
    assert bundle.paragraph_count == 2
    assert bundle.sentence_count == 3
    assert bundle.question_count == 1
    assert bundle.exclamation_count == 0
    assert bundle.urgency_term_count >= 1

