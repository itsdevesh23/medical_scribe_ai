MEDICAL SCRIBE AI - SETUP INSTRUCTIONS
======================================

PREREQUISITES:
1. Install Python 3.11 from https://www.python.org/downloads/release/python-3119/
2. Install Ollama from https://ollama.com
3. Run in terminal: ollama pull llama3.1
4. Install FFmpeg from https://www.gyan.dev/ffmpeg/builds/ (full-shared version)
5. Create Hugging Face account at https://huggingface.co
6. Accept these model licenses:
   - https://huggingface.co/pyannote/segmentation-3.0
   - https://huggingface.co/pyannote/speaker-diarization-community-1
7. Generate token at https://huggingface.co/settings/tokens

SETUP:
1. Extract the ZIP file
2. Open folder in terminal
3. Create virtual environment: python -m venv venv
4. Activate: venv\Scripts\activate
5. Install packages: pip install -r requirements.txt
6. Edit config.py: Add your Hugging Face token
7. Place .wav audio file in sample_audio/ folder
8. Run: python main.py

OUTPUT:
- Transcript displayed in console
- report.json saved with structured medical report