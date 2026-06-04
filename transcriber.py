import whisper
from pyannote.audio import Pipeline
import torch

# Mute speechbrain lazy import crashes caused by pytorch-lightning's inspect.stack()
import speechbrain.utils.importutils
speechbrain.utils.importutils.LazyModule.__getattr__ = lambda self, name: (_ for _ in ()).throw(AttributeError())

from config import WHISPER_MODEL_PATH, PYANNOTE_MODEL_PATH

def transcribe_audio(audio_path: str):
    # whisper.load_model handles downloading if it's just the name "small"
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    transcription = []
    for segment in result["segments"]:
        transcription.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })
    return transcription