from neuro_audio.alignment import AudioAlignmentService
from neuro_audio.features import AcousticFeatureService
from neuro_audio.schemas import AudioAnalysisRequest, AudioSectionInput


def test_acoustic_feature_service_extracts_timeline_and_hook_section() -> None:
    alignment = AudioAlignmentService().align(
        AudioAnalysisRequest(
            project_id="project_song",
            content_type="song_clip",
            transcript=(
                "Soft verses fall into the night.\n\n"
                "Then the chorus lifts the signal bright."
            ),
            sections=[
                AudioSectionInput(
                    label="verse",
                    start_ms=0,
                    end_ms=16000,
                    lyrics="Soft verses fall into the night.",
                    energy=0.35,
                    loudness=0.33,
                    spectral_contrast=0.41,
                ),
                AudioSectionInput(
                    label="chorus",
                    start_ms=16000,
                    end_ms=32000,
                    lyrics="Then the chorus lifts the signal bright.",
                    energy=0.82,
                    loudness=0.76,
                    spectral_contrast=0.72,
                ),
            ],
            audience={
                "label": "Indie pop listeners",
                "platform_context": "streaming",
                "target_goals": [{"dimension": "emotional_pacing", "target_value": 0.8, "priority": 1}],
            },
            bpm=122,
        )
    )

    features = AcousticFeatureService().extract(alignment)

    assert features.section_count == 2
    assert features.avg_energy > 0.0
    assert features.hook_section_label == "chorus"
    assert len(features.tension_timeline) == 2

