# Mute speechbrain lazy import crashes caused by pytorch-lightning's inspect.stack()
import speechbrain.utils.importutils
speechbrain.utils.importutils.LazyModule.__getattr__ = lambda self, name: (_ for _ in ()).throw(AttributeError())

from pyannote.audio import Pipeline
from config import PYANNOTE_MODEL_PATH, MIN_SPEAKERS, MAX_SPEAKERS

def diarize_audio(audio_path: str):
    pipeline = Pipeline.from_pretrained(PYANNOTE_MODEL_PATH)
    diarization = pipeline(audio_path, min_speakers=MIN_SPEAKERS, max_speakers=MAX_SPEAKERS)
    speaker_segments = []
    for turn, speaker in diarization.speaker_diarization:
        speaker_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return speaker_segments