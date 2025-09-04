"""
Celery tasks for analytics and reporting
"""

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document, DocumentAnalytics, ProcessingJob
from app.services.analytics_service import AnalyticsService
from datetime import datetime, timedelta

@celery_app.task
def generate_daily_analytics():
    """Generate daily analytics data."""
    
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        # Get yesterday's date
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        
        # Check if analytics already exist for yesterday
        existing_analytics = db.query(DocumentAnalytics).filter(
            DocumentAnalytics.date == yesterday
        ).first()
        
        if existing_analytics:
            return {
                'status': 'skipped',
                'message': f'Analytics for {yesterday} already exist'
            }
        
        # Generate analytics for yesterday
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = datetime.combine(yesterday, datetime.max.time())
        
        # Get document analytics
        document_analytics = analytics_service.get_document_analytics(start_date, end_date)
        
        # Calculate metrics
        total_documents = sum(item['count'] for item in document_analytics['daily_counts'])
        processed_documents = sum(
            item['count'] for item in document_analytics['status_distribution'] 
            if item['status'] == 'completed'
        )
        failed_documents = sum(
            item['count'] for item in document_analytics['status_distribution'] 
            if item['status'] == 'failed'
        )
        
        # Calculate average processing time
        processing_jobs = db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= start_date,
            ProcessingJob.created_at <= end_date,
            ProcessingJob.status == 'completed',
            ProcessingJob.duration_seconds.isnot(None)
        ).all()
        
        avg_processing_time = 0
        if processing_jobs:
            avg_processing_time = sum(job.duration_seconds for job in processing_jobs) / len(processing_jobs)
        
        # Document types breakdown
        document_types = {}
        for item in document_analytics['category_distribution']:
            document_types[item['category']] = item['count']
        
        # Create analytics record
        analytics_record = DocumentAnalytics(
            organization_id=1,  # Default organization
            date=start_date,
            total_documents=total_documents,
            processed_documents=processed_documents,
            failed_documents=failed_documents,
            average_processing_time=avg_processing_time,
            document_types=document_types,
            ai_accuracy_score=0.0,  # Would be calculated from AI results
            common_categories=list(document_types.keys())[:10]
        )
        
        db.add(analytics_record)
        db.commit()
        
        return {
            'status': 'completed',
            'date': yesterday.isoformat(),
            'total_documents': total_documents,
            'processed_documents': processed_documents,
            'failed_documents': failed_documents,
            'average_processing_time': avg_processing_time
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def generate_weekly_report():
    """Generate weekly analytics report."""
    
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        # Get last week's data
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        # Generate comprehensive analytics
        overview = analytics_service.get_overview(7)
        document_analytics = analytics_service.get_document_analytics(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        processing_performance = analytics_service.get_processing_performance(7)
        ai_insights = analytics_service.get_ai_insights(7)
        
        # Compile weekly report
        weekly_report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': 7
            },
            'overview': overview,
            'document_analytics': document_analytics,
            'processing_performance': processing_performance,
            'ai_insights': ai_insights,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # In a real application, this would be saved to a file or sent via email
        # For now, we'll just return the report
        
        return {
            'status': 'completed',
            'report': weekly_report
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def generate_monthly_report():
    """Generate monthly analytics report."""
    
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        # Get last month's data
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        # Generate comprehensive analytics
        overview = analytics_service.get_overview(30)
        document_analytics = analytics_service.get_document_analytics(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        processing_performance = analytics_service.get_processing_performance(30)
        ai_insights = analytics_service.get_ai_insights(30)
        category_analytics = analytics_service.get_category_analytics()
        
        # Compile monthly report
        monthly_report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': 30
            },
            'overview': overview,
            'document_analytics': document_analytics,
            'processing_performance': processing_performance,
            'ai_insights': ai_insights,
            'category_analytics': category_analytics,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return {
            'status': 'completed',
            'report': monthly_report
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def calculate_ai_accuracy_metrics():
    """Calculate AI accuracy metrics from recent processing."""
    
    db = SessionLocal()
    try:
        # Get documents with AI analysis from the last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        ai_documents = db.query(Document).filter(
            Document.created_at >= cutoff_date,
            Document.ai_insights.isnot(None),
            Document.confidence_score.isnot(None)
        ).all()
        
        if not ai_documents:
            return {
                'status': 'completed',
                'message': 'No AI-analyzed documents found in the last 7 days'
            }
        
        # Calculate accuracy metrics
        confidence_scores = [doc.confidence_score for doc in ai_documents]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        high_confidence_count = len([score for score in confidence_scores if score >= 0.8])
        medium_confidence_count = len([score for score in confidence_scores if 0.5 <= score < 0.8])
        low_confidence_count = len([score for score in confidence_scores if score < 0.5])
        
        # Category accuracy
        category_accuracy = {}
        for doc in ai_documents:
            if doc.ai_insights and 'categorization' in doc.ai_insights:
                category = doc.ai_insights['categorization'].get('category', 'Unknown')
                if category not in category_accuracy:
                    category_accuracy[category] = {'total': 0, 'high_confidence': 0}
                
                category_accuracy[category]['total'] += 1
                if doc.confidence_score >= 0.8:
                    category_accuracy[category]['high_confidence'] += 1
        
        # Calculate accuracy percentages
        for category in category_accuracy:
            total = category_accuracy[category]['total']
            high_conf = category_accuracy[category]['high_confidence']
            category_accuracy[category]['accuracy_percentage'] = (high_conf / total * 100) if total > 0 else 0
        
        return {
            'status': 'completed',
            'total_analyzed_documents': len(ai_documents),
            'average_confidence': avg_confidence,
            'confidence_distribution': {
                'high_confidence': high_confidence_count,
                'medium_confidence': medium_confidence_count,
                'low_confidence': low_confidence_count
            },
            'category_accuracy': category_accuracy,
            'calculated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()
