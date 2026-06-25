# Project Overview: Architecture & Use Cases

This document outlines the core business value (Use Cases) and the technical foundation (Source Code Architecture) of the Offline AI Medical Scribe & Meeting Minutes Generator.

## 1. Primary Use Cases

This application is a highly versatile, dual-purpose AI pipeline designed for maximum data privacy. Because it runs 100% offline on local hardware, it is uniquely positioned to handle highly sensitive audio data without violating HIPAA or corporate confidentiality policies.

### Use Case A: The Medical Scribe (Healthcare)
* **The Problem:** Doctors spend hours every day typing clinical SOAP notes after seeing patients, leading to severe burnout. Using cloud-based AI solutions (like ChatGPT or Google Cloud) often violates HIPAA and patient privacy laws by sending sensitive health data over the internet.
* **Our Solution:** A doctor can record the consultation on their phone or laptop. Our completely offline system automatically transcribes the audio, analyzes the frequency to figure out who is the Doctor and who is the Patient (Diarization), and uses a local Large Language Model (Phi-3) to extract Symptoms, Diagnoses, Medications, and Follow-ups into a beautifully structured clinical PDF. **Zero patient data ever leaves the computer.**

### Use Case B: Corporate Meeting Minutes (Business)
* **The Problem:** In corporate environments, taking accurate meeting minutes is tedious and prone to human error. Furthermore, sensitive company strategies, financial discussions, or board meetings cannot be securely uploaded to public cloud AI transcription tools.
* **Our Solution:** You record the boardroom meeting. The system automatically transcribes the audio, identifies individual speakers (Speaker 1, Speaker 2, Speaker 3, etc.), and uses the AI to extract Key Decisions, Action Items, and deadlines into a structured, shareable report.

---

## 2. Source Code Architecture

The source code is designed to be highly modular, scalable, and easy to deploy. It separates the heavy AI processing from the user interface to ensure the application remains fast and responsive.

### Frontend (React + Vite + TailwindCSS)
* Located in the `frontend/` directory.
* The user interface is built using modern React. It allows users to easily switch between "Medical" and "Meeting" modes.
* It handles file uploads via a drag-and-drop interface and maintains a live WebSocket connection to the backend to display real-time progress updates (e.g., "Transcribing...", "Diarizing...").

### Backend API (FastAPI + Python)
* Located in the `backend/` directory.
* A high-performance, asynchronous Python API built with **FastAPI**.
* It securely handles file uploads and connects to a **PostgreSQL/SQLite database** (via SQLAlchemy) to track the status of all audio processing sessions.
* It exposes the WebSocket endpoint that the React frontend connects to.

### The AI Pipeline (Celery + Redis)
Because AI models take a long time to run (especially on CPUs), the heavy lifting is completely decoupled into background workers using **Celery** and **Redis**. 
* **Step 1 (Whisper):** Converts the raw audio file into text using OpenAI's open-source Whisper model (`transcriber.py`).
* **Step 2 (PyAnnote):** Analyzes the audio frequencies to separate the voices into distinct speaker segments (Diarization) (`diarization.py`).
* **Step 3 (Alignment):** Merges the text from Whisper with the timestamps from PyAnnote to create a labeled transcript (`align.py`).
* **Step 4 (Ollama/Phi-3):** Reads the final labeled transcript and acts as the "reasoning engine" to extract the structured JSON data for the PDF report (`nlp.py`).

### Deployment (Docker)
* Everything is containerized using **Docker** and **Docker Compose**.
* The `docker-compose.yml` file defines 5 completely isolated containers (Frontend, Backend API, Celery Worker, Redis, and Ollama).
* This ensures the application can be deployed on any machine in the office with a single command (`docker-compose up --build`), completely eliminating "dependency hell."
