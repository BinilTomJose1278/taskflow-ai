@echo off
REM Smart Document Processing Platform - Quick Start Script for Windows

echo 🚀 Starting Smart Document Processing Platform...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create environment file if it doesn't exist
if not exist .env (
    echo 📝 Creating environment file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file and add your OpenAI API key for AI features
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist uploads mkdir uploads
if not exist logs mkdir logs

REM Start the platform
echo 🐳 Starting Docker containers...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service health...
curl -f http://localhost/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Platform is running successfully!
    echo.
    echo 🌐 Access the platform at:
    echo    • Application: http://localhost
    echo    • API Documentation: http://localhost/docs
    echo    • Health Check: http://localhost/health
    echo.
    echo 📊 View logs with: docker-compose logs -f
    echo 🛑 Stop platform with: docker-compose down
) else (
    echo ❌ Platform failed to start. Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause
