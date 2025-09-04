"""
Document-related SQLAlchemy models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Organization(Base):
    """Organization model for multi-tenancy"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    workflows = relationship("Workflow", back_populates="organization")

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    documents = relationship("Document", back_populates="uploaded_by_user")
    processing_jobs = relationship("ProcessingJob", back_populates="user")

class Document(Base):
    """Document metadata model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash
    
    # Document metadata
    title = Column(String(500))
    description = Column(Text)
    category = Column(String(100))
    tags = Column(JSON, default=list)
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    processing_progress = Column(Float, default=0.0)
    error_message = Column(Text)
    
    # AI analysis results
    extracted_text = Column(Text)
    ai_summary = Column(Text)
    ai_insights = Column(JSON, default=dict)
    confidence_score = Column(Float)
    
    # Analysis status and results
    analysis_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    analysis_results = Column(Text)  # JSON string of analysis results
    analysis_started_at = Column(DateTime)
    analysis_completed_at = Column(DateTime)
    analysis_error = Column(Text)
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="documents")
    processing_jobs = relationship("ProcessingJob", back_populates="document")

class Workflow(Base):
    """Workflow automation model"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False)  # manual, scheduled, webhook
    trigger_config = Column(JSON, default=dict)
    
    # Workflow steps
    steps = Column(JSON, nullable=False)  # Array of processing steps
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="workflows")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingJob(Base):
    """Document processing job model"""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True)  # Celery task ID
    
    # Job details
    job_type = Column(String(100), nullable=False)  # text_extraction, ai_analysis, workflow
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)
    
    # Input/Output
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Relationships
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    
    document = relationship("Document", back_populates="processing_jobs")
    user = relationship("User", back_populates="processing_jobs")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentAnalytics(Base):
    """Document processing analytics model"""
    __tablename__ = "document_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Analytics data
    date = Column(DateTime(timezone=True), nullable=False)
    total_documents = Column(Integer, default=0)
    processed_documents = Column(Integer, default=0)
    failed_documents = Column(Integer, default=0)
    average_processing_time = Column(Float, default=0.0)
    
    # Document types breakdown
    document_types = Column(JSON, default=dict)
    
    # AI insights
    ai_accuracy_score = Column(Float, default=0.0)
    common_categories = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
