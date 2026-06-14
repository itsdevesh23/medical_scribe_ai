# Offline AI Medical Scribe & Meeting Minutes Generator

A completely local, offline AI application that automatically transcribes, diarizes (identifies speakers), and generates structured medical SOAP notes or professional meeting minutes from audio recordings or live microphone input.

This application uses state-of-the-art AI models (OpenAI Whisper, Pyannote, and Ollama/Phi3) running **100% locally** on your machine for maximum privacy. No data is sent to the cloud.

## 🎯 Usage Modes
- **Medical Mode:** The LLM extracts: patient complaint, symptoms, possible diagnoses, medications, follow‑up.
- **Meeting Mode:** The LLM extracts: meeting title, date, attendees, key discussion points, decisions, action items (with assigned persons), next meeting.

---

## 📋 Prerequisites

Because this runs heavy AI models locally, you will need to install a few dependencies on your machine before running the app.

### Hardware
- CPU with at least 4 cores (8 recommended for faster processing)
- 16 GB RAM (minimum 8 GB)
- ~10 GB free disk space for models and audio files

### Software

1. **Python 3.10 or 3.11**: Make sure Python is installed and added to your system PATH.
2. **FFmpeg**: Required for audio format conversion.
   - **Windows:** Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via winget: `winget install ffmpeg`. Must be in system `PATH`.
   - **Mac:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`
3. **Redis**: Used as a message broker for background tasks.
   - **Windows:** Download [Memurai](https://www.memurai.com/) (Redis for Windows) or run it via WSL.
   - **Mac:** `brew install redis` and run `brew services start redis`
   - **Linux:** `sudo apt install redis-server`
4. **Hugging Face Account & Token**: Required to download the PyAnnote Diarization model.
   - Create a free account at [huggingface.co](https://huggingface.co/).
   - Go to the [PyAnnote Speaker Diarization page](https://huggingface.co/pyannote/speaker-diarization-community-1) and agree to their terms of use.
   - Create an Access Token in your HF settings and paste it into `download_models.py` where it says `YOUR_HUGGING_FACE_TOKEN_HERE`.
5. **Ollama**: Used for the local Large Language Model generation.
   - Download and install from [Ollama's website](https://ollama.com/).
   - Once installed, open a terminal and run this command to download the AI model we use:
     ```bash
     ollama pull phi3:mini
     ```
6. **Node.js (v18+)**: Required for running the React/Vite frontend.

---

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <YOUR-GITHUB-REPO-URL>
   cd medical_scribe_ai
   ```

2. **Install Python Dependencies (Backend):**
   It is highly recommended to use a virtual environment or Anaconda.
   ```bash
   pip install -r requirements.txt
   ```

3. **Download AI Models:**
   Edit `download_models.py` and insert your Hugging Face token (`HF_TOKEN`). Then run:
   ```bash
   python download_models.py
   ```
   *This will download Whisper, PyAnnote, and Phi3 to your local `models/` directory.*

4. **Install Node Dependencies (Frontend):**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 💻 How to Run the Application

To run the application, you need to open **3 separate terminals** (command prompts) from the root folder of this project.

### Terminal 1: Start the FastAPI Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*This handles file uploads, the database, and the live status connection to the frontend.*

### Terminal 2: Start the Celery Worker (AI Pipeline)
**Windows:**
```bash
python -m celery -A backend.tasks worker --loglevel=info -P gevent
```
**Mac/Linux:**
```bash
celery -A backend.tasks worker --loglevel=info
```
*This runs the heavy lifting: Whisper transcription, Pyannote diarization, and Ollama summarization in the background.*

### Terminal 3: Start the React Frontend
```bash
cd frontend
npm run dev
```
*This starts the User Interface. Once it is running, open your web browser and go to `http://localhost:5173` to use the application!*

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
