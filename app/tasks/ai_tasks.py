"""
Celery tasks for AI processing
"""

from celery import current_task
from app.celery_app import celery_app
from app.services.ai_service import AIService
from app.core.database import SessionLocal
from app.models.document import Document
import asyncio

@celery_app.task(bind=True)
def analyze_document_with_ai(self, document_id: int, analysis_type: str = "all", custom_prompt: str = None):
    """Analyze a document using AI asynchronously."""
    
    db = SessionLocal()
    try:
        ai_service = AIService()
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Starting AI analysis'})
        
        # Perform AI analysis
        analysis_results = asyncio.run(ai_service.analyze_document(
            document_id=document_id,
            analysis_type=analysis_type,
            custom_prompt=custom_prompt
        ))
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Saving analysis results'})
        
        # Update document with AI results
        if analysis_results.get('results'):
            results = analysis_results['results']
            
            if 'summary' in results:
                document.ai_summary = results['summary']
            
            if 'categorization' in results:
                document.category = results['categorization'].get('category', document.category)
                document.confidence_score = results['categorization'].get('confidence', 0.0)
            
            if 'insights' in results:
                document.ai_insights = results['insights']
        
        document.status = "completed"
        document.processing_progress = 100.0
        db.commit()
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'AI analysis completed'})
        
        return {
            'document_id': document_id,
            'analysis_type': analysis_type,
            'results': analysis_results,
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
def batch_analyze_documents(self, document_ids: list, analysis_type: str = "all"):
    """Analyze multiple documents with AI in batch."""
    
    db = SessionLocal()
    try:
        ai_service = AIService()
        
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
                        'status': f'Analyzing document {i+1}/{total_documents}',
                        'current_document': document_id
                    }
                )
                
                # Get document
                document = db.query(Document).filter(Document.id == document_id).first()
                if not document:
                    results.append({'document_id': document_id, 'status': 'not_found'})
                    continue
                
                # Perform AI analysis
                analysis_results = asyncio.run(ai_service.analyze_document(
                    document_id=document_id,
                    analysis_type=analysis_type
                ))
                
                # Update document with results
                if analysis_results.get('results'):
                    results_data = analysis_results['results']
                    
                    if 'summary' in results_data:
                        document.ai_summary = results_data['summary']
                    
                    if 'categorization' in results_data:
                        document.category = results_data['categorization'].get('category', document.category)
                        document.confidence_score = results_data['categorization'].get('confidence', 0.0)
                    
                    if 'insights' in results_data:
                        document.ai_insights = results_data['insights']
                
                results.append({
                    'document_id': document_id, 
                    'status': 'completed',
                    'analysis_results': analysis_results
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
def generate_document_tags(document_id: int):
    """Generate tags for a document using AI."""
    
    db = SessionLocal()
    try:
        ai_service = AIService()
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        if not document.extracted_text:
            raise ValueError(f"Document {document_id} has no extracted text")
        
        # Generate tags
        tags = asyncio.run(ai_service.generate_tags(document.extracted_text))
        
        # Update document with tags
        document.tags = tags
        db.commit()
        
        return {
            'document_id': document_id,
            'tags': tags,
            'status': 'completed'
        }
        
    except Exception as e:
        return {
            'document_id': document_id,
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()
