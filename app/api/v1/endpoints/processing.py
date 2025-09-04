"""
Document processing endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.document import ProcessingJob
from app.schemas.document import (
    ProcessingJobCreate, ProcessingJobResponse
)
from app.services.processing_service import ProcessingService

router = APIRouter()

@router.post("/jobs", response_model=ProcessingJobResponse)
async def create_processing_job(
    job_data: ProcessingJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new processing job
    """
    try:
        processing_service = ProcessingService(db)
        job = await processing_service.create_job(job_data, background_tasks)
        return job
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating processing job: {str(e)}")

@router.get("/jobs", response_model=List[ProcessingJobResponse])
async def list_processing_jobs(
    db: Session = Depends(get_db)
):
    """
    List all processing jobs
    """
    try:
        processing_service = ProcessingService(db)
        jobs = await processing_service.list_jobs()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing processing jobs: {str(e)}")

@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_processing_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific processing job
    """
    try:
        processing_service = ProcessingService(db)
        job = await processing_service.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Processing job not found")
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving processing job: {str(e)}")

@router.get("/jobs/celery/{celery_job_id}", response_model=ProcessingJobResponse)
async def get_processing_job_by_celery_id(
    celery_job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a processing job by Celery job ID
    """
    try:
        processing_service = ProcessingService(db)
        job = await processing_service.get_job_by_celery_id(celery_job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Processing job not found")
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving processing job: {str(e)}")

@router.post("/jobs/{job_id}/cancel")
async def cancel_processing_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a processing job
    """
    try:
        processing_service = ProcessingService(db)
        success = await processing_service.cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Processing job not found")
        
        return {"message": "Processing job cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling processing job: {str(e)}")

@router.get("/status")
async def get_processing_status(
    db: Session = Depends(get_db)
):
    """
    Get overall processing system status
    """
    try:
        processing_service = ProcessingService(db)
        status = await processing_service.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting processing status: {str(e)}")
