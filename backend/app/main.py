import os

from fastapi import FastAPI
from database import Base, engine
from backend.app.routers import Processing, Recordings
from paths import UPLOAD_DIR, PROCESSED_DIR

app = FastAPI()
recordings_router = Recordings()
processing_router = Processing()
app.include_router(recordings_router.router, prefix="/recordings", tags=["recordings"])
app.include_router(processing_router.router, prefix="/processing", tags=["processing"])

# TODO - fix usage of deprecated decorator
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
