# TODO - move database operations into the crud files

import shutil
import os

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dsp import AudioProcessor
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import Recording
from schemas import PipelineRequest

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

class Recordings:
    router = APIRouter()
    
    @router.post("/recordings/upload")
    async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
        """
        User uploads a file, server saves the file to uploads/ and creates
        a database entry for it. API returns a response containing the 
        entry's id, name, and status
        """
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        recording = Recording(
            filename=file.filename,
            processed_filename=None,
            duration=None,
            rms=None,
            status="queued"
        )

        db.add(recording)
        db.commit()
        db.refresh(recording)

        return {
            "id": recording.id,
            "filename": recording.filename,
            "status": recording.status
        }

    @router.get("/recordings")
    def get_all_recordings(db: Session = Depends(get_db)):
        """
        Return a list of all uploaded recordings
        """
        recordings = db.query(Recording).order_by(
            Recording.uploaded_at.desc()
        ).all()

        return recordings

    @router.get("/recordings/{id}")
    def get_recording(recording_id: int, db: Session = Depends(get_db)):
        """
        Return the recording with the given id
        """
        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return recording

    @router.delete("/recordings/{id}")
    def delete_recording(recording_id: int, db: Session = Depends(get_db)):
        """
        Delete the recording with the given id
        """
        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        upload_path = f"{UPLOAD_DIR}/{recording.filename}"
        processed_path = f"{PROCESSED_DIR}/{recording.processed_filename}"

        if os.path.exists(upload_path):
            os.remove(upload_path)

        if recording.processed_filename and os.path.exists(processed_path):
            os.remove(processed_path)

        db.delete(recording)
        db.commit()

        return {"message": "Recording deleted"}

class Processing:
    router = APIRouter()

    # TODO - implement a database job queue instead of just started every request as a background task
    def run_pipeline(recording: Recording, pipeline, db: Session):
        infile = os.path.join(UPLOAD_DIR, recording.filename)
        outfile_name = f"processed_{recording.filename}"
        outfile = os.path.join(PROCESSED_DIR, outfile_name)

        try:
            recording.status = "processing"
            db.commit()

            AudioProcessor.apply_pipeline(infile, outfile, pipeline)

            recording.processed_filename = outfile_name
            recording.status = "done"

            db.commit()

        except Exception as e:
            recording.status = "failed"
            db.commit()
            print(e)

    @router.post("/processing/{id}")
    def process_recording(recording_id: int, request: PipelineRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
        """
        Run an audio pipeline on a recording
        """
        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        pipeline = []

        for step in request.pipeline:
            effect_step = {"effect": step.effect}
            effect_step.update(step.params)
            pipeline.append(effect_step)
        
        background_tasks.add_task(Processing.run_pipeline, recording, pipeline, db)

        return {
            "recording_id": recording.id,
            "status": "processing_started",
            "pipeline_steps": len(pipeline)
        }

    @router.get("/processing/status/{id}")
    def check_status(recording_id: int, db: Session = Depends(get_db)):
        """
        Check the processing status of a job
        """
        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return {
            "recording_id": recording.id,
            "status": recording.status,
            "processed_file": recording.processed_filename
        }

    @router.get("/processing/download/{filename}")
    def download_file(recording_id: int, db: Session = Depends(get_db)):
        """
        Download the processed audio file
        """
        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        if not recording.processed_filename:
            raise HTTPException(status_code=400, detail="File not processed yet")
        
        file_path = os.path.join(PROCESSED_DIR, recording.processed_filename)

        return FileResponse(
            file_path,
            media_type="audio/wav",
            filename=recording.processed_filename
        )
