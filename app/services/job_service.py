import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.transaction import Transaction
from app.models.job_summary import JobSummary
from app.tasks.processing_tasks import process_transaction_job
import shutil
import os
from typing import List, Optional

UPLOAD_DIR = "downloads/"

def create_job_from_upload(file: UploadFile, db: Session) -> Job:
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    row_count_raw = 0
    with open(file_path, "r", encoding="utf-8") as f:
        row_count_raw = sum(1 for line in f) - 1
    
    if row_count_raw < 0:
        row_count_raw = 0

    job = Job(
        id=job_id,
        filename=file.filename,
        status="pending",
        row_count_raw=row_count_raw
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)

    process_transaction_job.delay(job_id, file_path)

    return job

def get_all_jobs(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[Job]:
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    return query.offset(skip).limit(limit).all()

def get_job_status(db: Session, job_id: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "row_count_raw": job.row_count_raw,
        "row_count_clean": job.row_count_clean,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }

def get_job_results(db: Session, job_id: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    transactions = db.query(Transaction).filter(Transaction.job_id == job_id).all()
    summary = db.query(JobSummary).filter(JobSummary.job_id == job_id).first()

    anomalies = [t for t in transactions if t.is_anomaly]
    
    cat_breakdown = {}
    for t in transactions:
        c = t.category or "Uncategorised"
        cat_breakdown[c] = cat_breakdown.get(c, 0) + 1

    return {
        "job": job,
        "summary": summary,
        "cleaned_transactions": transactions,
        "anomalies": anomalies,
        "category_breakdown": cat_breakdown
    }
