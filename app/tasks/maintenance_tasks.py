"""
Celery tasks for system maintenance
"""

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import ProcessingJob, Document
from datetime import datetime, timedelta
import os

@celery_app.task
def cleanup_old_jobs():
    """Clean up old processing jobs."""
    
    db = SessionLocal()
    try:
        # Delete jobs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_jobs = db.query(ProcessingJob).filter(
            ProcessingJob.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for job in old_jobs:
            db.delete(job)
            deleted_count += 1
        
        db.commit()
        
        return {
            'status': 'completed',
            'deleted_jobs': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def system_health_check():
    """Perform system health check."""
    
    db = SessionLocal()
    try:
        # Check database connectivity
        db.execute("SELECT 1")
        
        # Check recent job success rate
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_jobs = db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= recent_cutoff
        ).all()
        
        if recent_jobs:
            successful_jobs = len([job for job in recent_jobs if job.status == "completed"])
            success_rate = (successful_jobs / len(recent_jobs)) * 100
        else:
            success_rate = 100.0
        
        # Check disk space for uploads directory
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            stat = os.statvfs(uploads_dir)
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        else:
            free_space_gb = 0
        
        # Determine system health
        health_status = "healthy"
        if success_rate < 80:
            health_status = "degraded"
        if success_rate < 50 or free_space_gb < 1:
            health_status = "critical"
        
        return {
            'status': 'completed',
            'health_status': health_status,
            'success_rate': success_rate,
            'free_space_gb': free_space_gb,
            'recent_jobs_count': len(recent_jobs),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'health_status': 'critical',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    finally:
        db.close()

@celery_app.task
def optimize_database():
    """Optimize database performance."""
    
    db = SessionLocal()
    try:
        # This would contain database optimization tasks
        # For example, updating statistics, rebuilding indexes, etc.
        
        # For PostgreSQL, we could run ANALYZE
        db.execute("ANALYZE")
        
        return {
            'status': 'completed',
            'message': 'Database optimization completed'
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def cleanup_orphaned_files():
    """Clean up orphaned files in the uploads directory."""
    
    db = SessionLocal()
    try:
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return {
                'status': 'completed',
                'message': 'Uploads directory does not exist'
            }
        
        # Get all file paths from database
        documents = db.query(Document).all()
        db_file_paths = {doc.file_path for doc in documents if doc.file_path}
        
        # Find files in uploads directory
        orphaned_files = []
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_file_paths:
                    orphaned_files.append(file_path)
        
        # Delete orphaned files
        deleted_count = 0
        for file_path in orphaned_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        return {
            'status': 'completed',
            'orphaned_files_found': len(orphaned_files),
            'deleted_files': deleted_count
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()
