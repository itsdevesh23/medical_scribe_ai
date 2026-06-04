import torch
import os
import shutil
import asyncio
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession

from backend.database import engine, Base, get_db
from backend.models import Session
from backend.tasks import celery_app, process_session, redis_client

app = FastAPI(title="Offline Medical Scribe & Meeting Minutes API")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./storage/audio")
REPORT_DIR = os.getenv("REPORT_DIR", "./storage/reports")

# Initialize DB and directories
Base.metadata.create_all(bind=engine)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

@app.post("/api/sessions")
async def create_session(mode: str = Form(...), file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    if mode not in ["medical", "meeting"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    # Create DB record
    new_session = Session(mode=mode)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    session_id_str = str(new_session.id)
    
    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    raw_audio_path = os.path.join(UPLOAD_DIR, f"{session_id_str}_raw{file_ext}")
    final_audio_path = os.path.join(UPLOAD_DIR, f"{session_id_str}.wav")
    
    with open(raw_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Standardize audio: convert any format (webm, mp3, etc) to 16kHz mono WAV
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-y", "-i", raw_audio_path, "-ar", "16000", "-ac", "1", final_audio_path], 
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(raw_audio_path):
            os.remove(raw_audio_path)
        new_session.audio_file_path = final_audio_path
    except subprocess.CalledProcessError:
        # If ffmpeg fails, fallback to the raw file
        new_session.audio_file_path = raw_audio_path
    db.commit()
    
    # Init redis status
    redis_client.set(f"session:{session_id_str}:status", "pending")
    
    # Dispatch Celery task
    process_session.delay(session_id_str)
    
    return {"session_id": session_id_str, "status": "pending"}

@app.get("/api/sessions")
def list_sessions(db: DBSession = Depends(get_db)):
    sessions = db.query(Session).order_by(Session.created_at.desc()).all()
    return [{"id": str(s.id), "date": s.created_at, "mode": s.mode, "status": s.status} for s in sessions]

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": str(session.id),
        "status": session.status,
        "mode": session.mode,
        "transcript": session.transcript,
        "report": session.report,
        "error_message": session.error_message
    }

@app.get("/api/sessions/{session_id}/report.pdf")
def download_pdf(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session or not session.pdf_path or not os.path.exists(session.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(session.pdf_path, filename=f"{session.mode}_report_{session_id}.pdf")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    redis_key = f"session:{session_id}:status"
    try:
        last_status = None
        while True:
            try:
                current_status_bytes = redis_client.get(redis_key)
                if current_status_bytes:
                    current_status = current_status_bytes.decode('utf-8')
                    if current_status != last_status:
                        await websocket.send_json({"status": current_status})
                        last_status = current_status
                        if current_status in ["completed", "failed"]:
                            break
            except Exception as e:
                # Ignore transient Redis errors (like TimeoutError) during polling
                pass
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
