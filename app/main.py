"""
Smart Document Processing & AI Workflow Platform
A sophisticated system for document analysis, AI-powered insights, and workflow automation.
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.websocket.connection_manager import ConnectionManager
from app.core.logging import setup_logging

# Initialize logging
setup_logging()

# WebSocket connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Smart Document Processing Platform...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Smart Document Processing Platform...")

# Create FastAPI app
app = FastAPI(
    title="Smart Document Processing Platform",
    description="""
    A sophisticated AI-powered document processing and workflow automation platform.
    
    ## Features
    
    * **Document Processing**: Upload and analyze various document types
    * **AI Integration**: Smart text extraction, categorization, and insights
    * **Workflow Automation**: Automated processing pipelines
    * **Real-time Updates**: WebSocket connections for live processing updates
    * **Analytics**: Document processing analytics and reporting
    * **Multi-tenant**: Support for multiple organizations
    
    ## Technology Stack
    
    * **Backend**: FastAPI, Python 3.11+
    * **Databases**: PostgreSQL (relational) + MongoDB (document storage)
    * **AI/ML**: OpenAI, spaCy, scikit-learn
    * **Queue**: Celery + Redis
    * **Deployment**: Docker, CI/CD ready
    """,
    version="1.0.0",
    contact={
        "name": "Smart Document Processing Platform",
        "email": "contact@example.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or process the message
            await manager.send_personal_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
