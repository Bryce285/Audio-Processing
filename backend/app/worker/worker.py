from models import Job, Recording
from dsp import AudioProcessor
from database import get_db
from sqlalchemy.orm import Session
from paths import UPLOAD_DIR, PROCESSED_DIR
import os
import time

class Worker:
    def __init__(self):
        self.db = get_db()

    def run_pipeline(self):
        while True:
            job = self.db.query(Job).filter(
                Job.status == "queued"
            ).first()

            if job:
                job.status = "processing"
                self.db.commit()

                recording = self.db.query(Recording).filter(
                    Recording.id == job.recording_id
                ).first()

                if not recording:
                    raise ValueError("Associated recording not found")

                infile = os.path.join(UPLOAD_DIR, recording.filename)
                outfile_name = f"processed_{recording.filename}"
                outfile = os.path.join(PROCESSED_DIR, outfile_name)

                try:
                    AudioProcessor.apply_pipeline(infile, outfile, job.pipeline_json)

                    recording.processed_filename = outfile_name
                    job.status = "done"
                    self.db.commit()

                except Exception as e:
                    job.status = "failed"
                    self.db.commit()
                    print(e)

            # using sleep here to avoid making thousands of unnessary db requests
            # a future implementation should use a system to alert the worker of new
            # jobs instead of just having the worker sleep
            time.sleep(2)

def main():
    worker = Worker()
    worker.run_pipeline()

if __name__ == "__main__":
    main()