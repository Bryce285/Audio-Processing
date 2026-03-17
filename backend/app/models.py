from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    processed_filename = Column(String, unique=True, index=True)
    duration = Column(Float)
    rms = Column(Float)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))
    jobs = relationship("Job", back_populates="recording")

# TODO - add a pipelines table so the user can store pipeline presets

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False)
    pipeline_json = Column(JSON)
    status = Column(String, default="queued")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    recording = relationship("Recording", back_populates="jobs")
