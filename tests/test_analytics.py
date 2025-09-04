"""Test analytics endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analytics_overview():
    """Test analytics overview endpoint."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "period_documents" in data
    assert "processing_rate" in data


def test_analytics_overview_with_days():
    """Test analytics overview with custom days."""
    response = client.get("/api/v1/analytics/overview?days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["period_days"] == 7


def test_document_analytics():
    """Test document analytics endpoint."""
    response = client.get("/api/v1/analytics/documents")
    assert response.status_code == 200
    data = response.json()
    assert "daily_counts" in data
    assert "status_distribution" in data
    assert "category_distribution" in data


def test_processing_performance():
    """Test processing performance endpoint."""
    response = client.get("/api/v1/analytics/processing-performance")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "success_rate" in data
    assert "average_duration" in data


def test_processing_performance_with_days():
    """Test processing performance with custom days."""
    response = client.get("/api/v1/analytics/processing-performance?days=30")
    assert response.status_code == 200
    data = response.json()
    assert "performance_trends" in data


def test_ai_insights():
    """Test AI insights endpoint."""
    response = client.get("/api/v1/analytics/ai-insights")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyzed" in data
    assert "average_confidence" in data
    assert "common_categories" in data


def test_category_analytics():
    """Test category analytics endpoint."""
    response = client.get("/api/v1/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert "category_distribution" in data
    assert "category_trends" in data
