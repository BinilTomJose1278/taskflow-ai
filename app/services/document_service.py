"""
Document service for handling document operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any
import os
import hashlib
import aiofiles
from pathlib import Path
import json
from datetime import datetime

from app.models.document import Document, Organization, User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    DocumentSearchRequest, DocumentSearchResponse, FileUploadResponse, DocumentStatus
)
from app.core.config import settings
from app.services.file_service import FileService
from app.services.text_extraction_service import TextExtractionService

class DocumentService:
    """Service for document operations"""
    
    def __init__(self, db: Session, mongo_db=None):
        self.db = db
        self.mongo_db = mongo_db
        self.file_service = FileService()
        self.text_extraction_service = TextExtractionService()
    
    async def upload_document(
        self,
        file,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: List[str] = None,
        background_tasks=None
    ) -> FileUploadResponse:
        """Upload and process a new document"""
        
        if tags is None:
            tags = []
        
        # Generate file hash for deduplication
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicate files
        existing_document = self.db.query(Document).filter(Document.file_hash == file_hash).first()
        if existing_document:
            return FileUploadResponse(
                document_id=existing_document.id,
                filename=existing_document.filename,
                file_size=existing_document.file_size,
                mime_type=existing_document.mime_type,
                status=DocumentStatus(existing_document.status),
                message="Document already exists"
            )
        
        # Save file to disk
        file_path = await self.file_service.save_file(file, file_content)
        
        # Create document record
        document = Document(
            filename=os.path.basename(file_path),
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            mime_type=file.content_type,
            file_hash=file_hash,
            title=title or file.filename,
            description=description,
            category=category,
            tags=tags,
            status=DocumentStatus.UPLOADED,
            organization_id=1,  # Default organization for now
            uploaded_by=1  # Default user for now
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Start text extraction in background
        if background_tasks:
            background_tasks.add_task(
                self._extract_text_async,
                document.id
            )
        
        return FileUploadResponse(
            document_id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            status=DocumentStatus.UPLOADED,
            message="Document uploaded successfully"
        )
    
    async def _extract_text_async(self, document_id: int):
        """Extract text from document asynchronously"""
        try:
            # Update status to processing
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.PROCESSING
                document.processing_progress = 0.0
                self.db.commit()
                
                # Extract text
                extracted_text = await self.text_extraction_service.extract_text(document.file_path)
                
                # Update document with extracted text
                document.extracted_text = extracted_text
                document.status = DocumentStatus.COMPLETED
                document.processing_progress = 100.0
                self.db.commit()
                
                print(f"✅ Text extracted for document {document_id}")
                
        except Exception as e:
            # Update status to failed
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                self.db.commit()
            print(f"❌ Error extracting text for document {document_id}: {e}")
    
    async def get_document(self, document_id: int) -> Optional[DocumentResponse]:
        """Get a document by ID"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        
        return DocumentResponse.from_orm(document)
    
    async def update_document(
        self,
        document_id: int,
        document_update: DocumentUpdate
    ) -> Optional[DocumentResponse]:
        """Update document metadata"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        
        # Update fields
        update_data = document_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        
        return DocumentResponse.from_orm(document)
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete a document and its files"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    async def list_documents(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> DocumentListResponse:
        """List documents with pagination and filtering"""
        
        query = self.db.query(Document)
        
        # Apply filters
        if category:
            query = query.filter(Document.category == category)
        
        if status:
            query = query.filter(Document.status == status)
        
        if search:
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
                Document.extracted_text.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        documents = query.order_by(desc(Document.created_at)).offset(offset).limit(size).all()
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return DocumentListResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    async def search_documents(
        self,
        search_request: DocumentSearchRequest
    ) -> DocumentSearchResponse:
        """Advanced document search with faceted results"""
        
        query = self.db.query(Document)
        
        # Apply search filters
        if search_request.query:
            search_filter = or_(
                Document.title.ilike(f"%{search_request.query}%"),
                Document.description.ilike(f"%{search_request.query}%"),
                Document.extracted_text.ilike(f"%{search_request.query}%")
            )
            query = query.filter(search_filter)
        
        if search_request.category:
            query = query.filter(Document.category == search_request.category)
        
        if search_request.tags:
            for tag in search_request.tags:
                query = query.filter(Document.tags.contains([tag]))
        
        if search_request.status:
            query = query.filter(Document.status == search_request.status)
        
        if search_request.date_from:
            query = query.filter(Document.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.filter(Document.created_at <= search_request.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.size
        documents = query.order_by(desc(Document.created_at)).offset(offset).limit(search_request.size).all()
        
        # Calculate pages
        pages = (total + search_request.size - 1) // search_request.size
        
        # Generate facets
        facets = await self._generate_facets()
        
        return DocumentSearchResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=search_request.page,
            size=search_request.size,
            pages=pages,
            facets=facets
        )
    
    async def _generate_facets(self) -> Dict[str, Any]:
        """Generate search facets"""
        # Categories
        categories = self.db.query(
            Document.category,
            func.count(Document.id).label('count')
        ).filter(
            Document.category.isnot(None)
        ).group_by(Document.category).all()
        
        # Statuses
        statuses = self.db.query(
            Document.status,
            func.count(Document.id).label('count')
        ).group_by(Document.status).all()
        
        # File types
        file_types = self.db.query(
            Document.mime_type,
            func.count(Document.id).label('count')
        ).group_by(Document.mime_type).all()
        
        return {
            "categories": [{"name": cat, "count": count} for cat, count in categories],
            "statuses": [{"name": status, "count": count} for status, count in statuses],
            "file_types": [{"name": mime_type, "count": count} for mime_type, count in file_types]
        }
    
    async def get_document_file_path(self, document_id: int) -> Optional[str]:
        """Get the file path for a document"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        return document.file_path
    
    async def get_extracted_text(self, document_id: int) -> Optional[str]:
        """Get extracted text for a document"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        return document.extracted_text
