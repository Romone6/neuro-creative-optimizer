from neuro_audio.alignment import AudioAlignmentService
from neuro_audio.schemas import AudioAnalysisRequest, AudioSectionInput


def test_audio_alignment_service_builds_timed_sections_and_asset() -> None:
    service = AudioAlignmentService()

    result = service.align(
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
                    label="chorus",
                    start_ms=18000,
                    end_ms=36000,
                    lyrics="Hold on now, we are rising higher. This is the part that starts the fire.",
                    energy=0.78,
                    loudness=0.7,
                    spectral_contrast=0.69,
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

    assert result.asset.content_type == "song_clip"
    assert len(result.sections) == 2
    assert result.sections[1].label == "chorus"
    assert result.sections[1].duration_ms == 18000
    assert result.sections[1].lyric_word_count > 0

