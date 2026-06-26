# Medical Scribe AI - Offline Air-Gapped Deployment Guide

This guide explains how to take this entire AI suite from an internet-connected laptop (where you downloaded everything) and transfer it to a completely disconnected, "air-gapped" offline computer using a USB cable or drive.

## What You Need to Transfer
Because this AI system relies on large models and Docker environments, you must transfer exactly 3 things to the offline computer:
1. **The Project Folder** (containing your models, Ollama storage, and code)
2. **The Docker Images** (bundled into a single `.tar` file)
3. **The Hugging Face Cache** (containing the PyAnnote models)

---

## Step 1: Prepare the Files on the Internet Laptop (Tomorrow's Tasks)

### 1. Download the Ollama Model Locally
Ensure that your `docker-compose.yml` has the `ollama` volume mapped to `./ollama_storage:/root/.ollama`. (This is already the default on GitHub).
Run the following command once while connected to the internet to download the AI text model directly into your project folder:
```bash
docker-compose up
```
*(Wait until you see "Application startup complete", then press `Ctrl + C` to stop it).*

### 2. Bundle the Docker Images
Open PowerShell in your project folder and run this exact command to bundle all the massive Docker images (Python, Postgres, Redis, etc.) into one giant `.tar` file. **This will take a few minutes.**
```bash
docker save -o medical_scribe_images.tar postgres:15 redis:7 ollama/ollama curlimages/curl:latest medical_scribe_ai-master-frontend medical_scribe_ai-master-backend medical_scribe_ai-master-worker
```

### 3. Copy Everything to your USB Drive / Cable
Copy these three critical items onto your USB drive:
1. **The entire `medical_scribe_ai-master` project folder**. (This now contains your `models/`, `ollama_storage/`, and `.env` files).
2. **The `medical_scribe_images.tar` file** you just created.
3. **Your Hugging Face cache folder**. Navigate to `C:\Users\YOUR_USERNAME\.cache\` and copy the entire `huggingface` folder.

---

## Step 2: Deploy on the Offline Computer

Once you plug your USB drive / cable into the offline computer, follow these steps:

### 1. Restore the Hugging Face Cache
Paste the `huggingface` folder from your USB drive directly into `C:\Users\THEIR_USERNAME\.cache\huggingface` on the new offline computer.

### 2. Move the Project Folder
Paste the `medical_scribe_ai-master` folder from your USB drive onto their Desktop or Documents folder.

### 3. Load the Docker Images
Open a terminal (PowerShell) inside the `medical_scribe_ai-master` folder on the offline computer and run this command to install the Docker images into their system:
```bash
docker load -i D:\path\to\USB\medical_scribe_images.tar
```
*(Replace the path with wherever you placed the `.tar` file).*

### 4. Start the Application!
Because the computer has absolutely no internet, **DO NOT** use the `--build` flag. (The `--build` flag attempts to download Python libraries from the internet).

Simply run:
```bash
docker-compose up
```

You are completely done. That offline laptop will now run the full AI suite entirely locally with no internet access required, forever!
