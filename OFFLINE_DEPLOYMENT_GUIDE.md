# Medical Scribe AI - Office Manual Updates & Offline Air-Gapped Deployment Guide

This document contains everything you need to do at the office tomorrow. Part 1 covers the manual code edits to apply the latest fixes to your office computer. Part 2 explains how to bundle everything and move it to a completely disconnected, "air-gapped" offline computer.

---

## PART 1: Manual Code Updates (Do these on the Internet Laptop first)

If you don't want to re-download the ZIP, make these 6 quick edits in your existing office folder:

### 1. `docker-compose.yml`
Find the `worker:` block, scroll down to its `environment:` list, and add the token at the bottom so it looks exactly like this:
```yaml
  worker:
    # ... other stuff ...
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medicalscribe
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_HOST=http://ollama:11434
      - HF_TOKEN=${HF_TOKEN}    <-- ADD THIS LINE
```

Also, under the `ollama:` section, change the volume line so the model downloads locally into your folder:
```yaml
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_storage:/root/.ollama     <-- CHANGE TO THIS
```

### 2. `.env` (New File)
Create a new file named exactly `.env` right next to your `docker-compose.yml` file, and paste this inside:
```text
HF_TOKEN=hf_your_actual_token_here
```

### 3. `.dockerignore` (New File)
Create a new file named exactly `.dockerignore` right next to your `docker-compose.yml` file, and paste this inside (this stops the 14-minute upload):
```text
models/
storage/
.venv/
```

### 4. `requirements.txt`
Open this file and add this exact line to the very bottom:
```text
huggingface_hub==0.22.2
```

### 5. `backend/diarization.py`
Open this file and find **Line 14**. Replace `for turn, speaker in diarization.speaker_diarization:` with this exact line:
```python
    for turn, _, speaker in diarization.itertracks(yield_label=True):
```

### 6. `download_models.py`
Replace the `HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN_HERE"` line at the top with these three lines so it reads from your new `.env` file:
```python
from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR_HUGGING_FACE_TOKEN_HERE")
```

**Run a Final Build:**
Now that your edits are done, open your terminal in that folder and run:
```bash
docker-compose up --build
```
This will take a few seconds to finish, and it will force Ollama to download the text model directly into the new `ollama_storage` folder. Wait until it says "Application startup complete", then press `Ctrl + C` to stop it.

---

## PART 2: Air-Gapped Transfer to the Offline Laptop

Now that your internet laptop is fully updated and working, you are ready to transfer everything to the offline computer.

### Step 1: Bundle the Docker Images
Open PowerShell in your project folder on the internet laptop and run this exact command. It will bundle all the massive Docker images (Python, Postgres, Redis, etc.) into one giant `.tar` file:
```bash
docker save -o medical_scribe_images.tar postgres:15 redis:7 ollama/ollama curlimages/curl:latest medical_scribe_ai-master-frontend medical_scribe_ai-master-backend medical_scribe_ai-master-worker
```

### Step 2: Transfer to the USB Drive
Copy these 3 items onto your USB drive / cable:
1. The entire `medical_scribe_ai-master` project folder (which now contains your `models`, `ollama_storage`, and `.env` files).
2. The `medical_scribe_images.tar` file you just created.
3. Your Hugging Face cache folder! Go to `C:\Users\YOUR_USERNAME\.cache\` and copy the entire `huggingface` folder.

### Step 3: Load on the Offline Laptop
1. Plug in the USB drive to the offline computer.
2. Paste the `huggingface` folder into `C:\Users\THEIR_USERNAME\.cache\huggingface` on the new offline computer.
3. Paste the `medical_scribe_ai-master` folder onto their Desktop.
4. Open a terminal in that folder and run this to install the Docker images into their system:
   ```bash
   docker load -i D:\path\to\USB\medical_scribe_images.tar
   ```
5. **Start the app!** Because it has absolutely no internet, you cannot use `--build` (it will try to download things and fail). Just run:
   ```bash
   docker-compose up
   ```

You are completely done. That offline laptop will now run the full AI suite entirely locally with no internet access required, forever!
