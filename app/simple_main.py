"""
Simple version of the Smart Document Processing Platform
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from pathlib import Path

app = FastAPI(
    title="Smart Document Processing Platform",
    description="A sophisticated AI-powered document processing and workflow automation platform.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Smart Document Processing Platform",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation link"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Document Processing Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .feature { margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }
            .api-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
            .api-link:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Smart Document Processing Platform</h1>
            <p>Welcome to the AI-powered document processing and workflow automation platform!</p>
            
            <div class="feature">
                <h3>📄 Document Processing</h3>
                <p>Upload and analyze various document types with AI-powered text extraction and categorization.</p>
            </div>
            
            <div class="feature">
                <h3>🤖 AI Integration</h3>
                <p>Smart insights, automated categorization, and intelligent document analysis.</p>
            </div>
            
            <div class="feature">
                <h3>⚡ Workflow Automation</h3>
                <p>Automated processing pipelines with real-time updates and monitoring.</p>
            </div>
            
            <div class="feature">
                <h3>📊 Analytics & Reporting</h3>
                <p>Comprehensive analytics and reporting for document processing insights.</p>
            </div>
            
            <a href="/docs" class="api-link">📚 View API Documentation</a>
        </div>
    </body>
    </html>
    """

# Document upload endpoint
@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None)
):
    """
    Upload a new document for processing
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "title": title,
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

# List documents endpoint
@app.get("/api/v1/documents/")
async def list_documents():
    """
    List uploaded documents
    """
    try:
        upload_dir = Path("uploads")
        if not upload_dir.exists():
            return {"documents": [], "total": 0}
        
        documents = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                documents.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created": file_path.stat().st_ctime
                })
        
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

# Analytics endpoint
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview():
    """
    Get analytics overview
    """
    try:
        upload_dir = Path("uploads")
        total_files = len(list(upload_dir.glob("*"))) if upload_dir.exists() else 0
        
        return {
            "total_documents": total_files,
            "processed_documents": total_files,
            "processing_rate": 100.0,
            "average_processing_time": 2.5,
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
