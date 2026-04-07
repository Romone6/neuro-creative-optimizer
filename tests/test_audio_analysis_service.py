from neuro_audio.analysis import AudioAnalysisService
from neuro_audio.schemas import AudioAnalysisRequest, AudioSectionInput


def test_audio_analysis_service_returns_timeline_comparisons_and_report() -> None:
    service = AudioAnalysisService()

    result = service.analyze(
        AudioAnalysisRequest(
            project_id="project_song",
            content_type="song_clip",
            title="Night Drive",
            transcript=(
                "City lights are bending in the rain.\n"
                "I keep driving through the same refrain.\n\n"
                "Hold on now, we are rising higher.\n"
                "This is the part that starts the fire."
            ),
            sections=[
                AudioSectionInput(
                    label="verse",
                    start_ms=0,
                    end_ms=18000,
                    lyrics="City lights are bending in the rain. I keep driving through the same refrain.",
                    energy=0.42,
                    loudness=0.38,
                    spectral_contrast=0.45,
                ),
                AudioSectionInput(
                    label="pre_chorus",
                    start_ms=18000,
                    end_ms=27000,
                    lyrics="Every mile is winding toward the wire.",
                    energy=0.58,
                    loudness=0.54,
                    spectral_contrast=0.56,
                ),
                AudioSectionInput(
                    label="chorus",
                    start_ms=27000,
                    end_ms=45000,
                    lyrics="Hold on now, we are rising higher. This is the part that starts the fire.",
                    energy=0.82,
                    loudness=0.74,
                    spectral_contrast=0.72,
                ),
            ],
            audience={
                "label": "Indie pop listeners",
                "platform_context": "streaming",
                "target_goals": [{"dimension": "memorability", "target_value": 0.8, "priority": 1}],
            },
            bpm=118,
        )
    )

    assert result.text_analysis.analysis_run.status == "completed"
    assert result.audio_scorecard.dimension_scores
    assert result.timeline.points
    assert result.section_comparison.strongest_section_label
    assert result.report.summary

