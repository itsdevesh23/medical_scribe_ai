def assign_speakers(transcription, diarization):
    """
    For each transcription segment, find the speaker who speaks the most during that time.
    Returns a list of labeled utterances.
    """
    labeled_transcript = []

    for seg in transcription:
        seg_start = seg["start"]
        seg_end = seg["end"]

        # Count speaker time in this interval
        speaker_time = {}
        for d in diarization:
            # Overlap calculation
            overlap_start = max(seg_start, d["start"])
            overlap_end = min(seg_end, d["end"])
            if overlap_start < overlap_end:
                duration = overlap_end - overlap_start
                speaker_time[d["speaker"]] = speaker_time.get(d["speaker"], 0) + duration

        if not speaker_time:
            dominant_speaker = "UNKNOWN"
        else:
            dominant_speaker = max(speaker_time, key=speaker_time.get)

        labeled_transcript.append({
            "start": seg_start,
            "end": seg_end,
            "speaker": dominant_speaker,
            "text": seg["text"]
        })

    return labeled_transcript