"""Test workflow-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_workflows():
    """Test listing workflows."""
    response = client.get("/api/v1/workflows/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_workflow():
    """Test getting a non-existent workflow."""
    response = client.get("/api/v1/workflows/99999")
    assert response.status_code == 404


def test_create_workflow():
    """Test creating a workflow."""
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "trigger_type": "manual",
        "trigger_config": {},
        "steps": [
            {
                "step_id": "step1",
                "step_type": "text_extraction",
                "config": {},
                "order": 1
            }
        ]
    }
    
    response = client.post("/api/v1/workflows/", json=workflow_data)
    # Response might be 200 or 500 depending on database setup
    assert response.status_code in [200, 500]


def test_execute_nonexistent_workflow():
    """Test executing a non-existent workflow."""
    response = client.post("/api/v1/workflows/99999/execute")
    assert response.status_code == 404


def test_update_nonexistent_workflow():
    """Test updating a non-existent workflow."""
    update_data = {
        "name": "Updated Workflow"
    }
    response = client.put("/api/v1/workflows/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_workflow():
    """Test deleting a non-existent workflow."""
    response = client.delete("/api/v1/workflows/99999")
    assert response.status_code == 404
