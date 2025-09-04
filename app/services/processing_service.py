"""
Processing service for managing document processing jobs
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.document import ProcessingJob, Document
from app.schemas.document import ProcessingJobCreate, ProcessingJobResponse, JobStatus

class ProcessingService:
    """Service for processing job operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_job(
        self,
        job_data: ProcessingJobCreate,
        background_tasks=None
    ) -> ProcessingJobResponse:
        """Create a new processing job"""
        
        # Generate unique job ID
        job_id = str(uuid.uuid4()) 
        
        db_job = ProcessingJob(
            job_id=job_id,
            job_type=job_data.job_type,
            status=JobStatus.PENDING,
            input_data=job_data.input_data,
            document_id=job_data.document_id,
            workflow_id=job_data.workflow_id,
            user_id=1  # Default user for now
        )
        
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        
        # Start processing in background if requested
        if background_tasks:
            background_tasks.add_task(
                self._process_job_async,
                db_job.id
            )
        
        return ProcessingJobResponse.from_orm(db_job)
    
    async def get_job(self, job_id: int) -> Optional[ProcessingJobResponse]:
        """Get a processing job by ID"""
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return None
        
        return ProcessingJobResponse.from_orm(job)
    
    async def get_job_by_celery_id(self, celery_job_id: str) -> Optional[ProcessingJobResponse]:
        """Get a processing job by Celery job ID"""
        job = self.db.query(ProcessingJob).filter(ProcessingJob.job_id == celery_job_id).first()
        if not job:
            return None
        
        return ProcessingJobResponse.from_orm(job)
    
    async def list_jobs(self) -> List[ProcessingJobResponse]:
        """List all processing jobs"""
        jobs = self.db.query(ProcessingJob).order_by(desc(ProcessingJob.created_at)).all()
        return [ProcessingJobResponse.from_orm(job) for job in jobs]
    
    async def cancel_job(self, job_id: int) -> bool:
        """Cancel a processing job"""
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return False
        
        # Only cancel if job is pending or running
        if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.FAILED
            job.error_message = "Job cancelled by user"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    async def get_system_status(self) -> dict:
        """Get overall processing system status"""
        
        # Count jobs by status
        total_jobs = self.db.query(ProcessingJob).count()
        pending_jobs = self.db.query(ProcessingJob).filter(ProcessingJob.status == JobStatus.PENDING).count()
        running_jobs = self.db.query(ProcessingJob).filter(ProcessingJob.status == JobStatus.RUNNING).count()
        completed_jobs = self.db.query(ProcessingJob).filter(ProcessingJob.status == JobStatus.COMPLETED).count()
        failed_jobs = self.db.query(ProcessingJob).filter(ProcessingJob.status == JobStatus.FAILED).count()
        
        # Calculate success rate
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Average processing time
        completed_jobs_with_duration = self.db.query(ProcessingJob).filter(
            ProcessingJob.status == JobStatus.COMPLETED,
            ProcessingJob.duration_seconds.isnot(None)
        ).all()
        
        avg_duration = 0
        if completed_jobs_with_duration:
            total_duration = sum(job.duration_seconds for job in completed_jobs_with_duration)
            avg_duration = total_duration / len(completed_jobs_with_duration)
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= recent_cutoff
        ).count()
        
        return {
            "total_jobs": total_jobs,
            "pending_jobs": pending_jobs,
            "running_jobs": running_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": round(success_rate, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "recent_jobs_24h": recent_jobs,
            "system_health": "healthy" if failed_jobs < total_jobs * 0.1 else "degraded"
        }
    
    async def _process_job_async(self, job_id: int):
        """Process a job asynchronously"""
        try:
            job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if not job:
                print(f"❌ Job {job_id} not found")
                return
            
            # Update status to running
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 0.0
            self.db.commit()
            
            print(f"🚀 Processing job {job.job_id} ({job.job_type})")
            
            # Simulate processing based on job type
            if job.job_type == "text_extraction":
                await self._process_text_extraction(job)
            elif job.job_type == "ai_analysis":
                await self._process_ai_analysis(job)
            elif job.job_type == "categorization":
                await self._process_categorization(job)
            elif job.job_type == "workflow":
                await self._process_workflow(job)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")
            
            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
            self.db.commit()
            
            print(f"✅ Job {job.job_id} completed successfully")
            
        except Exception as e:
            # Mark as failed
            job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                if job.started_at:
                    job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
                self.db.commit()
            print(f"❌ Job {job_id} failed: {e}")
    
    async def _process_text_extraction(self, job: ProcessingJob):
        """Process text extraction job"""
        import asyncio
        
        # Simulate text extraction
        for i in range(5):
            await asyncio.sleep(1)  # Simulate processing time
            job.progress = (i + 1) * 20
            self.db.commit()
        
        # Mock output
        job.output_data = {
            "extracted_text": f"Extracted text from document {job.document_id}",
            "word_count": 150,
            "language": "en"
        }
    
    async def _process_ai_analysis(self, job: ProcessingJob):
        """Process AI analysis job"""
        import asyncio
        
        # Simulate AI analysis
        for i in range(10):
            await asyncio.sleep(0.5)  # Simulate processing time
            job.progress = (i + 1) * 10
            self.db.commit()
        
        # Mock output
        job.output_data = {
            "summary": f"AI-generated summary for document {job.document_id}",
            "category": "Business Document",
            "confidence": 0.85,
            "key_points": ["Point 1", "Point 2", "Point 3"]
        }
    
    async def _process_categorization(self, job: ProcessingJob):
        """Process categorization job"""
        import asyncio
        
        # Simulate categorization
        for i in range(3):
            await asyncio.sleep(1)  # Simulate processing time
            job.progress = (i + 1) * 33.33
            self.db.commit()
        
        # Mock output
        job.output_data = {
            "category": "Technical Document",
            "confidence": 0.92,
            "subcategories": ["API Documentation", "Technical Specification"]
        }
    
    async def _process_workflow(self, job: ProcessingJob):
        """Process workflow job"""
        import asyncio
        
        # Simulate workflow execution
        for i in range(8):
            await asyncio.sleep(0.8)  # Simulate processing time
            job.progress = (i + 1) * 12.5
            self.db.commit()
        
        # Mock output
        job.output_data = {
            "workflow_id": job.workflow_id,
            "steps_completed": 5,
            "total_steps": 5,
            "execution_time": 6.4
        }
