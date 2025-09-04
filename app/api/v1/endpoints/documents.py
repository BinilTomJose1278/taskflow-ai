"""
Document management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import hashlib
import aiofiles
from pathlib import Path

from app.core.database import get_db, get_mongo_db
from app.core.config import settings
from app.models.document import Document, Organization, User
from app.schemas.document import (
    DocumentResponse, DocumentCreate, DocumentUpdate, DocumentListResponse,
    DocumentSearchRequest, DocumentSearchResponse, FileUploadResponse
)
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
from app.services.file_service import FileService
from app.websocket.connection_manager import ConnectionManager

# Create a global connection manager instance
manager = ConnectionManager()

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Upload a new document for processing
    
    - **file**: The document file to upload
    - **title**: Optional title for the document
    - **description**: Optional description
    - **category**: Optional category
    - **tags**: Optional tags as JSON string
    """
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file.size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Initialize services
        file_service = FileService()
        document_service = DocumentService(db, mongo_db)
        
        # Process tags
        tag_list = []
        if tags:
            try:
                import json
                tag_list = json.loads(tags)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid tags format. Must be valid JSON array.")
        
        # Upload and process file
        result = await document_service.upload_document(
            file=file,
            title=title,
            description=description,
            category=category,
            tags=tag_list,
            background_tasks=background_tasks
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List documents with pagination and filtering
    
    - **page**: Page number (starts from 1)
    - **size**: Number of documents per page (max 100)
    - **category**: Filter by category
    - **status**: Filter by processing status
    - **search**: Search in title, description, and extracted text
    """
    
    try:
        document_service = DocumentService(db, None)
        result = await document_service.list_documents(
            page=page,
            size=size,
            category=category,
            status=status,
            search=search
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    
    try:
        document_service = DocumentService(db, None)
        document = await document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update document metadata
    """
    
    try:
        document_service = DocumentService(db, None)
        document = await document_service.update_document(document_id, document_update)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Delete a document and its associated files
    """
    
    try:
        document_service = DocumentService(db, mongo_db)
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Download the original document file
    """
    
    try:
        document_service = DocumentService(db, None)
        file_path = await document_service.get_document_file_path(document_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: int,
    analysis_type: str = Form("all"),
    custom_prompt: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Trigger AI analysis for a document
    
    - **analysis_type**: Type of analysis (summary, categorization, insights, all)
    - **custom_prompt**: Custom prompt for analysis
    """
    
    try:
        document_service = DocumentService(db, mongo_db)
        ai_service = AIService()
        
        # Check if document exists
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Start AI analysis in background
        background_tasks.add_task(
            ai_service.analyze_document,
            document_id=document_id,
            analysis_type=analysis_type,
            custom_prompt=custom_prompt
        )
        
        return {"message": "AI analysis started", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")

@router.get("/{document_id}/text")
async def get_extracted_text(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get extracted text from a document
    """
    
    try:
        document_service = DocumentService(db, None)
        text = await document_service.get_extracted_text(document_id)
        
        if text is None:
            raise HTTPException(status_code=404, detail="Document not found or text not extracted")
        
        return {"document_id": document_id, "extracted_text": text}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {str(e)}")

@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Advanced document search with faceted results
    """
    
    try:
        document_service = DocumentService(db, None)
        result = await document_service.search_documents(search_request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
