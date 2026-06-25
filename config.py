import os

# ---------- Paths ----------
AUDIO_FILE = "sample_audio/test_meeting.wav"

# Local model paths (relative to project root)
WHISPER_MODEL_PATH = "models/whisper/medium"
PYANNOTE_MODEL_PATH = "models/pyannote/speaker-diarization-community-1/config.yaml"

# Ollama model name
OLLAMA_MODEL = "phi3:mini"        # Changed from mistral for faster CPU inference
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ---------- Mode ----------
MODE = "meeting"                    # "medical" or "meeting"

# For meetings: allow 3 to 10 speakers; for medical: fix to 2.
MIN_SPEAKERS = 1
MAX_SPEAKERS = 5

# ---------- Prompts ----------
MEDICAL_PROMPT = """
You are a medical scribe AI. Given the following transcript of a doctor-patient conversation, extract a structured clinical report in JSON format with these exact fields:
- patient_complaint: main reason for visit
- symptoms: list of symptoms mentioned
- diagnosis_possibilities: possible conditions discussed or implied
- medications_prescribed: list of medications with dosage and frequency
- follow_up_instructions: any follow-up or lifestyle advice

Transcript:
{transcript}

Return ONLY valid JSON, no other text or explanation.
"""

MEETING_PROMPT = """
You are an AI that extracts precise meeting minutes from a transcript.
Output ONLY valid JSON, no extra text, no explanations.

Required JSON keys:
- meeting_title: short title
- date: date mentioned or "unknown"
- attendees: list of speaker labels as they appear in the transcript, e.g. "Speaker 1", "Speaker 4 (Meeting Lead)"
- speaker_mapping: a dictionary mapping speaker labels to their real names IF AND ONLY IF you are absolutely certain. If you don't know, use the speaker label itself. Never guess.
- key_discussion_points: list of detailed sentences
- decisions_made: list of decisions, each as a short sentence. Include things like "agreed to review X", "decided to book Y".
- action_items: list of objects with "task", "assigned_to", "deadline". assigned_to should be the real name if known, otherwise the speaker label.
- next_meeting: object with "date" and "details", or "not specified".

Critical rules:
- Use speaker labels exactly as in the transcript.
- Infer names ONLY from direct addressing (e.g. "Morgan, could you..."). If unsure, use the speaker label.
- Include ALL action items mentioned, even minor ones.
- Capture decisions even if implied by phrases like "can we look at getting another one booked" -> decision: book another workshop.

Transcript:
{transcript}

JSON:
"""