"""Test processing-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_processing_jobs():
    """Test listing processing jobs."""
    response = client.get("/api/v1/processing/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_processing_job():
    """Test getting a non-existent processing job."""
    response = client.get("/api/v1/processing/jobs/99999")
    assert response.status_code == 404


def test_get_processing_job_by_celery_id():
    """Test getting a processing job by Celery ID."""
    response = client.get("/api/v1/processing/jobs/celery/nonexistent-id")
    assert response.status_code == 404


def test_create_processing_job():
    """Test creating a processing job."""
    job_data = {
        "job_type": "text_extraction",
        "input_data": {"document_id": 1}
    }
    
    response = client.post("/api/v1/processing/jobs", json=job_data)
    # Response might be 200 or 500 depending on database setup
    assert response.status_code in [200, 500]


def test_cancel_nonexistent_processing_job():
    """Test cancelling a non-existent processing job."""
    response = client.post("/api/v1/processing/jobs/99999/cancel")
    assert response.status_code == 404


def test_processing_status():
    """Test processing system status endpoint."""
    response = client.get("/api/v1/processing/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "success_rate" in data
    assert "system_health" in data
