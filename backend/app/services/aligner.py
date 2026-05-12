"""
Alinea segmentos de transcripción con segmentos de diarización
para asignar cada frase a un hablante.
"""


def align(
    transcription: list[dict],
    diarization: list[dict],
) -> list[dict]:
    """
    Combina transcripción y diarización produciendo segmentos con speaker.

    Args:
        transcription: [{"start": 0.0, "end": 2.5, "text": "..."}]
        diarization:  [{"start": 0.0, "end": 5.2, "speaker": "SPEAKER_00"}]

    Returns:
        [{"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00", "text": "..."}]
    """
    aligned = []

    for seg in transcription:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_mid = (seg_start + seg_end) / 2.0

        best_speaker = "DESCONOCIDO"
        best_overlap = 0.0

        for spk_seg in diarization:
            overlap_start = max(seg_start, spk_seg["start"])
            overlap_end = min(seg_end, spk_seg["end"])
            overlap = max(0.0, overlap_end - overlap_start)

            if spk_seg["start"] <= seg_mid <= spk_seg["end"]:
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = spk_seg["speaker"]

        aligned.append({
            "start": seg_start,
            "end": seg_end,
            "speaker": best_speaker,
            "text": seg["text"],
        })

    return aligned
