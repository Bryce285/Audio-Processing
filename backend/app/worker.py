# TODO - finish implementing worker, schedule it from somewhere
while True:
    job = db.query(Job).filter(
        Job.status == "queued"
    ).first()

    if job:
        job.status = "processing"
        db.commit()

        try:
            AudioProcessor.apply_pipeline(...)
            job.status = "done"
            db.commit()

        except Exception as e:
            job.status = "failed"
            db.commit()
            print(e)
