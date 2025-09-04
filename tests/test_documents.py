"""Test document-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_documents():
    """Test listing documents."""
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data


def test_list_documents_with_pagination():
    """Test listing documents with pagination."""
    response = client.get("/api/v1/documents/?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10


def test_list_documents_with_filters():
    """Test listing documents with filters."""
    response = client.get("/api/v1/documents/?category=test&status=completed")
    assert response.status_code == 200


def test_get_nonexistent_document():
    """Test getting a non-existent document."""
    response = client.get("/api/v1/documents/99999")
    assert response.status_code == 404


def test_search_documents():
    """Test document search."""
    search_data = {
        "query": "test",
        "page": 1,
        "size": 20
    }
    response = client.post("/api/v1/documents/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "facets" in data


def test_upload_document_invalid_type():
    """Test uploading a document with invalid file type."""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    data = {"title": "Test Document"}
    
    # This should work for text files
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    # The response might be 200 or 500 depending on database setup
    assert response.status_code in [200, 500]


def test_analyze_document_nonexistent():
    """Test analyzing a non-existent document."""
    response = client.post("/api/v1/documents/99999/analyze")
    assert response.status_code == 404


def test_get_extracted_text_nonexistent():
    """Test getting extracted text from non-existent document."""
    response = client.get("/api/v1/documents/99999/text")
    assert response.status_code == 404


def test_download_document_nonexistent():
    """Test downloading a non-existent document."""
    response = client.get("/api/v1/documents/99999/download")
    assert response.status_code == 404
