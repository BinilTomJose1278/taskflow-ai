"""
Analytics service for generating insights and reports
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.document import Document, DocumentAnalytics, ProcessingJob

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_overview(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics overview for the specified period"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total documents
        total_documents = self.db.query(Document).count()
        
        # Documents in period
        period_documents = self.db.query(Document).filter(
            Document.created_at >= start_date
        ).count()
        
        # Processing statistics
        completed_documents = self.db.query(Document).filter(
            and_(
                Document.created_at >= start_date,
                Document.status == "completed"
            )
        ).count()
        
        failed_documents = self.db.query(Document).filter(
            and_(
                Document.created_at >= start_date,
                Document.status == "failed"
            )
        ).count()
        
        # Processing rate
        processing_rate = (completed_documents / period_documents * 100) if period_documents > 0 else 0
        
        # Average processing time
        avg_processing_time = self.db.query(
            func.avg(ProcessingJob.duration_seconds)
        ).filter(
            and_(
                ProcessingJob.created_at >= start_date,
                ProcessingJob.status == "completed"
            )
        ).scalar() or 0
        
        # Document types breakdown
        document_types = self.db.query(
            Document.mime_type,
            func.count(Document.id).label('count')
        ).filter(
            Document.created_at >= start_date
        ).group_by(Document.mime_type).all()
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_documents": total_documents,
            "period_documents": period_documents,
            "completed_documents": completed_documents,
            "failed_documents": failed_documents,
            "processing_rate": round(processing_rate, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "document_types": [
                {"type": doc_type, "count": count} 
                for doc_type, count in document_types
            ]
        }
    
    async def get_document_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get detailed document analytics"""
        
        query = self.db.query(Document)
        
        if start_date:
            query = query.filter(Document.created_at >= start_date)
        if end_date:
            query = query.filter(Document.created_at <= end_date)
        
        # Daily document counts
        daily_counts = self.db.query(
            func.date(Document.created_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            and_(
                Document.created_at >= (start_date or datetime.utcnow() - timedelta(days=30)),
                Document.created_at <= (end_date or datetime.utcnow())
            )
        ).group_by(func.date(Document.created_at)).order_by('date').all()
        
        # Status distribution
        status_distribution = self.db.query(
            Document.status,
            func.count(Document.id).label('count')
        ).filter(
            and_(
                Document.created_at >= (start_date or datetime.utcnow() - timedelta(days=30)),
                Document.created_at <= (end_date or datetime.utcnow())
            )
        ).group_by(Document.status).all()
        
        # Category distribution
        category_distribution = self.db.query(
            Document.category,
            func.count(Document.id).label('count')
        ).filter(
            and_(
                Document.created_at >= (start_date or datetime.utcnow() - timedelta(days=30)),
                Document.created_at <= (end_date or datetime.utcnow()),
                Document.category.isnot(None)
            )
        ).group_by(Document.category).all()
        
        return {
            "daily_counts": [
                {"date": str(date), "count": count} 
                for date, count in daily_counts
            ],
            "status_distribution": [
                {"status": status, "count": count} 
                for status, count in status_distribution
            ],
            "category_distribution": [
                {"category": category, "count": count} 
                for category, count in category_distribution
            ]
        }
    
    async def get_processing_performance(self, days: int = 7) -> Dict[str, Any]:
        """Get document processing performance metrics"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Processing jobs in period
        jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= start_date
        ).all()
        
        if not jobs:
            return {
                "total_jobs": 0,
                "successful_jobs": 0,
                "failed_jobs": 0,
                "success_rate": 0,
                "average_duration": 0,
                "performance_trends": []
            }
        
        # Calculate metrics
        total_jobs = len(jobs)
        successful_jobs = len([job for job in jobs if job.status == "completed"])
        failed_jobs = len([job for job in jobs if job.status == "failed"])
        success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Average duration
        completed_jobs = [job for job in jobs if job.duration_seconds is not None]
        average_duration = sum(job.duration_seconds for job in completed_jobs) / len(completed_jobs) if completed_jobs else 0
        
        # Performance trends (daily)
        daily_performance = {}
        for job in jobs:
            date = job.created_at.date()
            if date not in daily_performance:
                daily_performance[date] = {"total": 0, "successful": 0, "failed": 0}
            
            daily_performance[date]["total"] += 1
            if job.status == "completed":
                daily_performance[date]["successful"] += 1
            elif job.status == "failed":
                daily_performance[date]["failed"] += 1
        
        performance_trends = [
            {
                "date": str(date),
                "total": data["total"],
                "successful": data["successful"],
                "failed": data["failed"],
                "success_rate": (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            }
            for date, data in sorted(daily_performance.items())
        ]
        
        return {
            "total_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": round(success_rate, 2),
            "average_duration": round(average_duration, 2),
            "performance_trends": performance_trends
        }
    
    async def get_ai_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get AI analysis insights and trends"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Documents with AI analysis
        ai_documents = self.db.query(Document).filter(
            and_(
                Document.created_at >= start_date,
                Document.ai_insights.isnot(None)
            )
        ).all()
        
        if not ai_documents:
            return {
                "total_analyzed": 0,
                "average_confidence": 0,
                "common_categories": [],
                "insights_trends": []
            }
        
        # Calculate average confidence
        confidence_scores = [doc.confidence_score for doc in ai_documents if doc.confidence_score is not None]
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Common categories from AI analysis
        categories = {}
        for doc in ai_documents:
            if doc.ai_insights and "categorization" in doc.ai_insights:
                category = doc.ai_insights["categorization"].get("category", "Unknown")
                categories[category] = categories.get(category, 0) + 1
        
        common_categories = [
            {"category": category, "count": count}
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # AI insights trends (daily)
        daily_insights = {}
        for doc in ai_documents:
            date = doc.created_at.date()
            if date not in daily_insights:
                daily_insights[date] = {"analyzed": 0, "confidence_sum": 0}
            
            daily_insights[date]["analyzed"] += 1
            if doc.confidence_score:
                daily_insights[date]["confidence_sum"] += doc.confidence_score
        
        insights_trends = [
            {
                "date": str(date),
                "analyzed": data["analyzed"],
                "average_confidence": (data["confidence_sum"] / data["analyzed"]) if data["analyzed"] > 0 else 0
            }
            for date, data in sorted(daily_insights.items())
        ]
        
        return {
            "total_analyzed": len(ai_documents),
            "average_confidence": round(average_confidence, 3),
            "common_categories": common_categories,
            "insights_trends": insights_trends
        }
    
    async def get_category_analytics(self) -> Dict[str, Any]:
        """Get document category distribution and trends"""
        
        # Category distribution
        categories = self.db.query(
            Document.category,
            func.count(Document.id).label('count')
        ).filter(
            Document.category.isnot(None)
        ).group_by(Document.category).order_by(desc('count')).all()
        
        # Category trends over time (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        category_trends = self.db.query(
            Document.category,
            func.date(Document.created_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            and_(
                Document.created_at >= start_date,
                Document.category.isnot(None)
            )
        ).group_by(Document.category, func.date(Document.created_at)).all()
        
        # Organize trends by category
        trends_by_category = {}
        for category, date, count in category_trends:
            if category not in trends_by_category:
                trends_by_category[category] = []
            trends_by_category[category].append({"date": str(date), "count": count})
        
        return {
            "category_distribution": [
                {"category": category, "count": count}
                for category, count in categories
            ],
            "category_trends": trends_by_category
        }
