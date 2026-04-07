from neuro_analysis.audience import AudienceProfileInput, AudienceService
from neuro_analysis.features import FeatureService
from neuro_analysis.ingestion import IngestionService, TextIngestionRequest
from neuro_analysis.scoring import ScoringService


def test_scoring_service_produces_explainable_scores() -> None:
    ingestion = IngestionService()
    audience_service = AudienceService()
    feature_service = FeatureService()
    scoring_service = ScoringService()

    ingestion_result = ingestion.ingest_text(
        TextIngestionRequest(
            project_id="project_1",
            content_type="ad_copy",
            body="Act now. This offer is specific and credible.\n\nWhy wait?",
        )
    )
    audience_result = audience_service.validate_profile(
        AudienceProfileInput(
            label="Cold traffic founders",
            platform_context="linkedin",
            target_goals=[{"dimension": "trust", "target_value": 0.82, "priority": 1}],
        )
    )
    features = feature_service.extract_text_features(
        asset=ingestion_result.asset,
        segments=ingestion_result.segments,
    )

    result = scoring_service.score_text(
        asset=ingestion_result.asset,
        segments=ingestion_result.segments,
        audience_profile=audience_result.profile,
        modifier_context=audience_result.modifier_context,
        features=features,
    )

    dimensions = {score.dimension for score in result.score_vector.scores}
    assert {"clarity", "trust", "urgency", "novelty", "cognitive_load", "narrative_momentum"} <= dimensions
    assert result.score_vector.confidence_summary.overall_confidence > 0
    assert result.score_vector.scores[0].evidence
    assert result.segment_score_vectors

