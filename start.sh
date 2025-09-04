#!/bin/bash

# Smart Document Processing Platform - Quick Start Script

echo "🚀 Starting Smart Document Processing Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key for AI features"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads logs

# Start the platform
echo "🐳 Starting Docker containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Platform is running successfully!"
    echo ""
    echo "🌐 Access the platform at:"
    echo "   • Application: http://localhost"
    echo "   • API Documentation: http://localhost/docs"
    echo "   • Health Check: http://localhost/health"
    echo ""
    echo "📊 View logs with: docker-compose logs -f"
    echo "🛑 Stop platform with: docker-compose down"
else
    echo "❌ Platform failed to start. Check logs with: docker-compose logs"
    exit 1
fi
