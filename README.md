# 🚀 Smart Document Processing Platform

A sophisticated AI-powered document processing and workflow automation platform built with FastAPI, demonstrating advanced backend development skills perfect for Hypergen's requirements.

## ✨ Features

### 🔧 Core Functionality
- **Document Processing**: Upload and analyze various document types (PDF, DOCX, TXT, Images)
- **AI Integration**: Smart text extraction, categorization, and insights using OpenAI
- **Workflow Automation**: Automated processing pipelines with custom steps
- **Real-time Updates**: WebSocket connections for live processing updates
- **Multi-tenant**: Support for multiple organizations
- **Analytics**: Comprehensive document processing analytics and reporting

### 🛠 Technology Stack

#### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Relational database for structured data
- **MongoDB**: Document database for flexible data storage
- **Redis**: Caching and message broker
- **Celery**: Distributed task queue for background processing

#### AI & Processing
- **OpenAI GPT**: AI-powered document analysis and insights
- **Tesseract OCR**: Text extraction from images
- **PyPDF2**: PDF text extraction
- **python-docx**: Word document processing
- **spaCy**: Natural language processing

#### DevOps & Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and load balancer
- **CI/CD Ready**: GitHub Actions configuration

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Nginx Proxy   │    │   FastAPI App   │
│                 │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   PostgreSQL    │◄─────────────┤
                       │   (Metadata)    │              │
                       └─────────────────┘              │
                                                        │
                       ┌─────────────────┐              │
                       │     MongoDB     │◄─────────────┤
                       │ (Document Store)│              │
                       └─────────────────┘              │
                                                        │
                       ┌─────────────────┐              │
                       │      Redis      │◄─────────────┤
                       │ (Cache & Queue) │              │
                       └─────────────────┘              │
                                                        │
                       ┌─────────────────┐              │
                       │  Celery Worker  │◄─────────────┘
                       │ (Background Jobs)│
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd taskflow-ai
```

### 2. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# Add your OpenAI API key for AI features
```

### 3. Start the Platform
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 4. Access the Platform
- **API Documentation**: http://localhost/docs
- **Application**: http://localhost
- **Health Check**: http://localhost/health

## 📚 API Documentation

### Core Endpoints

#### Documents
- `POST /api/v1/documents/upload` - Upload a document
- `GET /api/v1/documents/` - List documents with pagination
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/documents/{id}/analyze` - Trigger AI analysis
- `GET /api/v1/documents/{id}/text` - Get extracted text

#### Workflows
- `POST /api/v1/workflows/` - Create a workflow
- `GET /api/v1/workflows/` - List workflows
- `POST /api/v1/workflows/{id}/execute` - Execute workflow

#### Analytics
- `GET /api/v1/analytics/overview` - Get analytics overview
- `GET /api/v1/analytics/documents` - Document analytics
- `GET /api/v1/analytics/processing-performance` - Processing metrics

#### Processing
- `POST /api/v1/processing/jobs` - Create processing job
- `GET /api/v1/processing/jobs` - List processing jobs
- `GET /api/v1/processing/status` - System status

### WebSocket
- `WS /ws/{client_id}` - Real-time updates

## 🔧 Development

### Local Development Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start databases
docker-compose up -d postgres mongodb redis

# Run the application
uvicorn app.main:app --reload
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🐳 Docker Commands

```bash
# Build the application
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## 📊 Key Features Demonstrated

### 1. **Advanced Backend Development**
- FastAPI with async/await patterns
- Complex data models with relationships
- Comprehensive error handling
- API versioning and documentation

### 2. **Database Design**
- PostgreSQL for relational data (users, documents, workflows)
- MongoDB for document storage and flexible schemas
- Proper indexing and query optimization
- Database migrations with Alembic

### 3. **AI Integration**
- OpenAI API integration for document analysis
- Text extraction from multiple formats
- Smart categorization and insights
- Confidence scoring and error handling

### 4. **Workflow Automation**
- Configurable processing pipelines
- Step-by-step execution with progress tracking
- Error handling and retry mechanisms
- Background job processing with Celery

### 5. **Real-time Features**
- WebSocket connections for live updates
- Progress tracking for long-running tasks
- Connection management and heartbeat

### 6. **DevOps & Deployment**
- Multi-stage Docker builds
- Docker Compose orchestration
- Nginx reverse proxy configuration
- Health checks and monitoring
- Environment-based configuration

### 7. **Security & Performance**
- JWT authentication
- Rate limiting
- File upload security
- CORS configuration
- Gzip compression

## 🎯 Hypergen Alignment

This project demonstrates all the skills Hypergen is looking for:

✅ **Backend Development**: Strong Python and FastAPI experience  
✅ **Databases**: Both MongoDB and PostgreSQL integration  
✅ **Data Modeling**: Complex relational and document structures  
✅ **APIs**: RESTful design with comprehensive documentation  
✅ **DevOps**: Docker, CI/CD, and deployment ready  
✅ **AI Integration**: Modern AI-assisted features  
✅ **Portfolio**: Demonstrable individual work showcasing all concepts  

## 📈 Future Enhancements

- [ ] React frontend with document visualization
- [ ] Advanced workflow designer UI
- [ ] Machine learning model training
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] API rate limiting and quotas
- [ ] Document versioning
- [ ] Advanced search with Elasticsearch

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for Hypergen's Junior Software Developer position**
