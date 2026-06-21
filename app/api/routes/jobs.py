from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.schemas import JobResponse, JobStatusResponse
from app.services import job_service

router = APIRouter()

@router.post("/upload", response_model=JobResponse)
def upload_job(file: UploadFile = File(...), db: Session = Depends(get_db)):
    job = job_service.create_job_from_upload(file, db)
    return job

@router.get("", response_model=List[JobResponse])
def get_jobs(
    status: Optional[str] = None, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, le=100), 
    db: Session = Depends(get_db)
):
    return job_service.get_all_jobs(db, status=status, skip=skip, limit=limit)

@router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    return job_service.get_job_status(db, job_id)
