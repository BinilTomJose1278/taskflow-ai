"""
Celery tasks for document processing
"""

from celery import current_task
from app.celery_app import celery_app
from app.services.document_service import DocumentService
from app.services.text_extraction_service import TextExtractionService
from app.core.database import SessionLocal
from app.models.document import Document
import asyncio

@celery_app.task(bind=True)
def extract_text_from_document(self, document_id: int):
    """Extract text from a document asynchronously."""
    
    db = SessionLocal()
    try:
        document_service = DocumentService(db, None)
        text_extraction_service = TextExtractionService()
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Starting text extraction'})
        
        # Extract text
        extracted_text = asyncio.run(text_extraction_service.extract_text(document.file_path))
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Saving extracted text'})
        
        # Update document
        document.extracted_text = extracted_text
        document.status = "completed"
        document.processing_progress = 100.0
        db.commit()
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Text extraction completed'})
        
        return {
            'document_id': document_id,
            'extracted_text_length': len(extracted_text),
            'status': 'completed'
        }
        
    except Exception as e:
        # Update document status to failed
        if 'document' in locals():
            document.status = "failed"
            document.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()

@celery_app.task(bind=True)
def process_document_batch(self, document_ids: list):
    """Process multiple documents in batch."""
    
    db = SessionLocal()
    try:
        document_service = DocumentService(db, None)
        text_extraction_service = TextExtractionService()
        
        results = []
        total_documents = len(document_ids)
        
        for i, document_id in enumerate(document_ids):
            try:
                # Update progress
                progress = int((i / total_documents) * 100)
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'progress': progress, 
                        'status': f'Processing document {i+1}/{total_documents}',
                        'current_document': document_id
                    }
                )
                
                # Get document
                document = db.query(Document).filter(Document.id == document_id).first()
                if not document:
                    results.append({'document_id': document_id, 'status': 'not_found'})
                    continue
                
                # Extract text
                extracted_text = asyncio.run(text_extraction_service.extract_text(document.file_path))
                
                # Update document
                document.extracted_text = extracted_text
                document.status = "completed"
                document.processing_progress = 100.0
                
                results.append({
                    'document_id': document_id, 
                    'status': 'completed',
                    'text_length': len(extracted_text)
                })
                
            except Exception as e:
                # Update document status to failed
                if 'document' in locals():
                    document.status = "failed"
                    document.error_message = str(e)
                
                results.append({
                    'document_id': document_id, 
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Commit all changes
        db.commit()
        
        return {
            'total_documents': total_documents,
            'results': results,
            'status': 'completed'
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()

@celery_app.task
def cleanup_processed_documents():
    """Clean up temporary files and optimize database."""
    
    db = SessionLocal()
    try:
        # This would contain cleanup logic
        # For example, removing temporary files, optimizing database, etc.
        
        return {
            'status': 'completed',
            'message': 'Document cleanup completed'
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()
