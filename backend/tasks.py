import torch
import os
import sys
from celery import Celery
from dotenv import load_dotenv

# Add project root to sys.path so we can import from medical_scribe_ai root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.models import Session
from backend.pdf_generator import generate_pdf
from main import run_pipeline

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REPORT_DIR = os.getenv("REPORT_DIR", "./storage/reports")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

import redis
redis_client = redis.Redis.from_url(REDIS_URL)

@celery_app.task(bind=True, name="process_session")
def process_session(self, session_id_str):
    db = SessionLocal()
    session = db.query(Session).filter(Session.id == session_id_str).first()
    if not session:
        db.close()
        return {"status": "error", "message": "Session not found"}

    try:
        session.status = "processing"
        db.commit()
        
        redis_key = f"session:{session_id_str}:status"
        redis_client.set(redis_key, "processing")

        def update_progress(phase):
            self.update_state(state='PROGRESS', meta={'phase': phase})
            redis_client.set(redis_key, phase)

        audio_path = session.audio_file_path
        mode = session.mode

        # Run pipeline
        labeled, report = run_pipeline(audio_path, mode, update_progress)
        
        update_progress("generating_pdf")
        
        # Save results to DB
        session.transcript = labeled
        session.report = report
        
        # Generate PDF
        pdf_filename = f"{session_id_str}.pdf"
        pdf_path = os.path.join(REPORT_DIR, pdf_filename)
        generate_pdf(report, mode, pdf_path)
        
        session.pdf_path = pdf_path
        session.status = "completed"
        db.commit()
        
        redis_client.set(redis_key, "completed")
        
        return {"status": "completed"}
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        db.commit()
        redis_client.set(f"session:{session_id_str}:status", "failed")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
