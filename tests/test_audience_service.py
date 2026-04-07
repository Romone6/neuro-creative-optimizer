from neuro_analysis.audience import AudienceProfileInput, AudienceService


def test_audience_service_normalizes_profile_and_builds_modifier_context() -> None:
    service = AudienceService()

    result = service.validate_profile(
        AudienceProfileInput(
            label="  Cold traffic founders  ",
            age_band=" 25-40 ",
            platform_context=" linkedin ",
            tone_preference=" direct ",
            target_goals=[
                {"dimension": "trust", "target_value": 0.82, "priority": 2},
                {"dimension": "clarity", "target_value": 0.91, "priority": 1},
            ],
        )
    )

    assert result.profile.label == "Cold traffic founders"
    assert result.profile.target_goals[0].dimension == "clarity"
    assert result.modifier_context["traits"]["platform_context"] == "linkedin"
    assert result.modifier_context["target_dimensions"]["trust"]["target_value"] == 0.82

