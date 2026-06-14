# Offline AI Medical Scribe & Meeting Minutes Generator

A completely local, offline AI application that automatically transcribes, diarizes (identifies speakers), and generates structured medical SOAP notes or professional meeting minutes from audio recordings or live microphone input.

This application uses state-of-the-art AI models (OpenAI Whisper, Pyannote, and Ollama/Phi3) running **100% locally** on your machine for maximum privacy. No data is sent to the cloud.

## 🎯 Usage Modes
- **Medical Mode:** The LLM extracts: patient complaint, symptoms, possible diagnoses, medications, follow‑up.
- **Meeting Mode:** The LLM extracts: meeting title, date, attendees, key discussion points, decisions, action items (with assigned persons), next meeting.

---

## 🚀 Deployment Options

There are two ways to deploy this application:
1. **Docker Deployment (Recommended)** - Simplest method, no dependencies required.
2. **Manual Offline Deployment** - For completely air-gapped computers where Docker is not an option.

---

## 🐳 Docker Deployment (Recommended for Office Testing)

If you want to run the application in an office environment or don't want to install dependencies locally, you can use **Docker**. This bundles the frontend, backend, database, and AI models into isolated containers.

### Docker Prerequisites
1. **Docker Desktop**: Install from [docker.com](https://www.docker.com/products/docker-desktop/).
2. **AI Models**: You still need to download the AI models locally first so Docker can mount them.
   - Open `download_models.py` and paste your Hugging Face token where it says `YOUR_HUGGING_FACE_TOKEN_HERE`.
   - Run `docker-compose run --rm backend python download_models.py` (This uses Docker to safely download the models so you don't even need Python installed on your PC!).
   - *Note: Docker will automatically pull the Ollama `phi3:mini` model for you on startup!*

### Running with Docker

1. Open a terminal in the `medical_scribe_ai` folder.
2. Run this single command:
   ```bash
   docker-compose up --build
   ```
3. Wait for the containers to build and start. The first time will take a few minutes as it downloads the environments.
4. Once running, open your web browser and go to:
   **`http://localhost:5173`**

To stop the application, simply press `Ctrl + C` in the terminal, or run:
```bash
docker-compose down
```

---

## 🏢 Offline Deployment (Hospital / Office Without Docker)
This system is designed to be fully transferred to an air-gapped or offline computer:
1. Run `download_models.py` and `ollama pull phi3:mini` on an internet-connected machine.
2. Copy the entire `medical_scribe_ai` folder (including the downloaded `models/` folder) via USB to the target machine.
3. Install Python, FFmpeg, and Ollama on the target machine from offline installers.
4. Run the three startup commands (FastAPI, Celery, React). Everything will function 100% offline.

---

## ❓ Troubleshooting
| Problem | Solution |
|---------|----------|
| **Frontend stuck on "Generating Report"** | Make sure the Ollama application is running in the background and you have pulled the `phi3:mini` model. |
| **Audio format error** | Ensure `ffmpeg` is correctly installed and accessible in your system's PATH variable. |
| **LLM output is poor** | You can switch models in `config.py` (e.g., to `llama3` for better multilingual support). |
| **TimeoutError / Websocket crash** | This happens if Redis gets stuck. Just restart the Celery and FastAPI terminals. |
