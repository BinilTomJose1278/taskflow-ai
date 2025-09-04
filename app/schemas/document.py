"""
Pydantic schemas for document-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobStatus(str, Enum):
    """Processing job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(str, Enum):
    """Processing job types"""
    TEXT_EXTRACTION = "text_extraction"
    AI_ANALYSIS = "ai_analysis"
    WORKFLOW = "workflow"
    CATEGORIZATION = "categorization"

# Base schemas
class DocumentBase(BaseModel):
    """Base document schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., min_length=1, max_length=100)

class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    file_hash: str
    status: DocumentStatus
    processing_progress: float
    extracted_text: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_insights: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: Optional[float] = None
    organization_id: int
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Schema for document list response"""
    documents: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int

# Processing Job schemas
class ProcessingJobBase(BaseModel):
    """Base processing job schema"""
    job_type: JobType
    input_data: Dict[str, Any] = Field(default_factory=dict)

class ProcessingJobCreate(ProcessingJobBase):
    """Schema for creating a processing job"""
    document_id: Optional[int] = None
    workflow_id: Optional[int] = None

class ProcessingJobResponse(ProcessingJobBase):
    """Schema for processing job response"""
    id: int
    job_id: str
    status: JobStatus
    progress: float
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    document_id: Optional[int] = None
    user_id: int
    workflow_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Workflow schemas
class WorkflowStep(BaseModel):
    """Individual workflow step"""
    step_id: str
    step_type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    order: int

class WorkflowBase(BaseModel):
    """Base workflow schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_type: str = Field(..., pattern="^(manual|scheduled|webhook)$")
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    steps: List[WorkflowStep]

class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow"""
    pass

class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    steps: Optional[List[WorkflowStep]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(WorkflowBase):
    """Schema for workflow response"""
    id: int
    is_active: bool
    total_runs: int
    successful_runs: int
    failed_runs: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Analytics schemas
class DocumentAnalyticsResponse(BaseModel):
    """Schema for document analytics response"""
    id: int
    organization_id: int
    date: datetime
    total_documents: int
    processed_documents: int
    failed_documents: int
    average_processing_time: float
    document_types: Dict[str, int] = Field(default_factory=dict)
    ai_accuracy_score: float
    common_categories: List[str] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Analysis schemas
class AIAnalysisRequest(BaseModel):
    """Schema for AI analysis request"""
    document_id: int
    analysis_type: str = Field(..., pattern="^(summary|categorization|insights|all)$")
    custom_prompt: Optional[str] = None

class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis response"""
    document_id: int
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float
    processing_time: float
    created_at: datetime

# File upload schemas
class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    document_id: int
    filename: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    message: str

# Search and filter schemas
class DocumentSearchRequest(BaseModel):
    """Schema for document search request"""
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[DocumentStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class DocumentSearchResponse(BaseModel):
    """Schema for document search response"""
    documents: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int
    facets: Dict[str, Any] = Field(default_factory=dict)
