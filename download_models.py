import os
from huggingface_hub import snapshot_download, hf_hub_download

# --------- CONFIG ---------
MODELS_DIR = "models"
WHISPER_MODEL = "Systran/faster-whisper-small"
PYANNOTE_MODEL = "pyannote/speaker-diarization-3.1"
PHI3_REPO = "microsoft/Phi-3-mini-4k-instruct-gguf"
PHI3_FILENAME = "Phi-3-mini-4k-instruct-q4.gguf"
HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN_HERE"
# --------------------------

def download_whisper():
    target = os.path.join(MODELS_DIR, "whisper", "small")
    print(f"Downloading Whisper ({WHISPER_MODEL}) to {target} ...")
    snapshot_download(repo_id=WHISPER_MODEL, local_dir=target,
                      token=HF_TOKEN, ignore_patterns=["*.msgpack", "*.h5"])
    print("Whisper done.")

def download_pyannote():
    print(f"Downloading PyAnnote ({PYANNOTE_MODEL}) to HuggingFace cache...")
    from pyannote.audio import Pipeline
    Pipeline.from_pretrained(PYANNOTE_MODEL, use_auth_token=HF_TOKEN)
    print("PyAnnote done.")

def download_phi3_gguf():
    target_dir = os.path.join(MODELS_DIR, "phi3")
    os.makedirs(target_dir, exist_ok=True)
    print(f"Downloading Phi-3 GGUF ({PHI3_FILENAME}) ...")
    hf_hub_download(
        repo_id=PHI3_REPO,
        filename=PHI3_FILENAME,
        local_dir=target_dir,
        local_dir_use_symlinks=False,
        token=HF_TOKEN,
    )
    print("Phi-3 GGUF downloaded.")


def download_whisper_medium():
    target = os.path.join(MODELS_DIR, "whisper", "medium")
    print(f"Downloading Whisper medium (Systran/faster-whisper-medium) to {target} ...")
    snapshot_download(
        repo_id="Systran/faster-whisper-medium",
        local_dir=target,
        token=HF_TOKEN,
        ignore_patterns=["*.msgpack", "*.h5"]
    )
    print("Whisper medium done.")


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    download_whisper_medium()
    download_phi3_gguf()    # This now works because the function is defined above
    download_whisper()
    download_pyannote()
    print("All models downloaded.")
    print(f"Whisper, PyAnnote, and Phi-3 are in the '{MODELS_DIR}' folder.")
    print("No Ollama needed. You can now copy the whole project to the offline PC.")



