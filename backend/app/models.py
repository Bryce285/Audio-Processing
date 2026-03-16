from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from .database import Base

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    processed_filename = Column(String, unique=True, index=True)
    duration = Column(Float)
    rms = Column(Float)
    status = Column(String, default="queued")
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))

# TODO - add a pipelines table so the user can store pipeline presets

# TODO - add a table to store job queue info