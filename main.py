import torch
import json
from transcriber import transcribe_audio
from diarization import diarize_audio
from align import assign_speakers
from nlp import generate_report

def build_transcript_text(labeled_segments):
    """Convert labeled segments into readable dialogue format."""
    lines = []
    for seg in labeled_segments:
        speaker_name = seg["speaker"]
        lines.append(f"{speaker_name}: {seg['text']}")
    return "\n".join(lines)

def run_pipeline(audio_file_path, mode, update_progress=None):
    """
    Run the end-to-end pipeline.
    update_progress is an optional callback: update_progress(phase_name)
    Returns: (transcript_json, report_json)
    """
    if update_progress:
        update_progress("transcribing")
    transcription = transcribe_audio(audio_file_path)

    if update_progress:
        update_progress("diarizing")
    diarization = diarize_audio(audio_file_path)

    if update_progress:
        update_progress("aligning")
    labeled = assign_speakers(transcription, diarization)

    if mode == "medical":
        # ----- Medical mode: find doctor, label as Doctor/Patient -----
        speaker_total_time = {}
        speaker_medical_score = {}
        speaker_question_score = {}

        medical_keywords = [
            "diagnos", "prescrib", "medication", "treatment", "test", "ecg",
            "electrocardiogram", "pulmonary", "stress test", "blood pressure",
            "prescribe", "recommend", "suggest", "examine", "assessment",
            "lifestyle", "diet", "exercise", "follow-up", "appointment",
            "refer", "specialist", "surgery", "therapy", "injection",
            "symptom", "history", "family history", "allergy", "dosage",
            "bowel", "constipation", "laxative", "paracetamol", "fiber",
            "abdomen", "abdominal", "stomach", "prescription"
        ]

        for seg in labeled:
            speaker = seg["speaker"]
            speaker_total_time[speaker] = speaker_total_time.get(speaker, 0) + (seg["end"] - seg["start"])

            text_lower = seg["text"].lower()
            score = sum(1 for keyword in medical_keywords if keyword in text_lower)
            speaker_medical_score[speaker] = speaker_medical_score.get(speaker, 0) + score

            if "?" in seg["text"]:
                speaker_question_score[speaker] = speaker_question_score.get(speaker, 0) + 1

        combined_score = {}
        all_speakers = set(list(speaker_medical_score.keys()) + list(speaker_question_score.keys()))
        for speaker in all_speakers:
            combined_score[speaker] = (
                    speaker_medical_score.get(speaker, 0) * 3 +
                    speaker_question_score.get(speaker, 0) * 2
            )

        if combined_score:
            doctor_speaker = max(combined_score, key=combined_score.get)
        else:
            doctor_speaker = max(speaker_total_time, key=speaker_total_time.get) if speaker_total_time else "SPEAKER_00"

        # Map to Doctor / Patient
        for seg in labeled:
            if seg["speaker"] == doctor_speaker:
                seg["speaker"] = "Doctor"
            else:
                seg["speaker"] = "Patient"

    else:
        # ----- Meeting / generic mode: label as Speaker 1, Speaker 2, … -----
        unique_speakers = sorted(set(seg["speaker"] for seg in labeled))
        speaker_name_map = {spk: f"Speaker {i + 1}" for i, spk in enumerate(unique_speakers)}

        for seg in labeled:
            seg["speaker"] = speaker_name_map[seg["speaker"]]

    # Build full dialogue text
    full_transcript = build_transcript_text(labeled)

    if update_progress:
        update_progress("generating_report")
        
    report = generate_report(full_transcript, mode=mode)

    return labeled, report

if __name__ == "__main__":
    from config import AUDIO_FILE, MODE
    labeled, report = run_pipeline(AUDIO_FILE, MODE, lambda phase: print(f"Phase: {phase}"))
    print(json.dumps(report, indent=2))