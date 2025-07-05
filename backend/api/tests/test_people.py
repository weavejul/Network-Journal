"""
Tests for Person CRUD operations.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.api.main import app

client = TestClient(app)


class TestPersonCRUD:
    """Test Person CRUD operations."""
    
    def test_create_person(self):
        """Test creating a new person."""
        person_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        response = client.post("/api/v1/people/", json=person_data)
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["name"] == person_data["name"]
        assert data["email"] == person_data["email"]
        assert data["phone"] == person_data["phone"]
        assert data["id"] is not None
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
        assert data["status"] == "active"
        assert data["data_source"] == "manual_entry"
    
    def test_create_person_minimal(self):
        """Test creating a person with only required fields."""
        person_data = {"name": "Jane Smith"}
        
        response = client.post("/api/v1/people/", json=person_data)
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["name"] == person_data["name"]
        assert data["email"] is None
        assert data["id"] is not None
    
    def test_get_person(self):
        """Test getting a person by ID."""
        # First create a person
        person_data = {"name": "Alice Johnson", "email": "alice@example.com"}
        create_response = client.post("/api/v1/people/", json=person_data)
        person_id = create_response.json()["data"]["id"]
        
        # Then get the person
        response = client.get(f"/api/v1/people/{person_id}")
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["id"] == person_id
        assert data["name"] == person_data["name"]
        assert data["email"] == person_data["email"]
    
    def test_get_person_not_found(self):
        """Test getting a non-existent person."""
        response = client.get("/api/v1/people/non-existent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_list_people(self):
        """Test listing all people."""
        # Create a few people first
        people_data = [
            {"name": "Bob Wilson", "email": "bob@example.com"},
            {"name": "Carol Brown", "email": "carol@example.com"}
        ]
        
        for person_data in people_data:
            client.post("/api/v1/people/", json=person_data)
        
        response = client.get("/api/v1/people/")
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check that our created people are in the list
        names = [person["name"] for person in data]
        assert "Bob Wilson" in names
        assert "Carol Brown" in names
    
    def test_update_person(self):
        """Test updating a person."""
        # First create a person
        person_data = {"name": "David Lee", "email": "david@example.com"}
        create_response = client.post("/api/v1/people/", json=person_data)
        person_id = create_response.json()["data"]["id"]
        
        # Then update the person
        update_data = {
            "name": "David Lee Updated",
            "email": "david.updated@example.com",
            "phone": "+9876543210"
        }
        
        response = client.put(f"/api/v1/people/{person_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["id"] == person_id
        assert data["name"] == update_data["name"]
        assert data["email"] == update_data["email"]
        assert data["phone"] == update_data["phone"]
        assert data["updated_at"] is not None
    
    def test_update_person_not_found(self):
        """Test updating a non-existent person."""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/people/non-existent-id", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_delete_person(self):
        """Test deleting a person."""
        # First create a person
        person_data = {"name": "Eve Davis", "email": "eve@example.com"}
        create_response = client.post("/api/v1/people/", json=person_data)
        person_id = create_response.json()["data"]["id"]
        
        # Then delete the person
        response = client.delete(f"/api/v1/people/{person_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Person deleted successfully"
        
        # Verify the person is deleted
        get_response = client.get(f"/api/v1/people/{person_id}")
        assert get_response.status_code == 404
    
    def test_delete_person_not_found(self):
        """Test deleting a non-existent person."""
        response = client.delete("/api/v1/people/non-existent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_person_validation(self):
        """Test person data validation."""
        # Test missing required field
        response = client.post("/api/v1/people/", json={})
        assert response.status_code == 422
        
        # Test invalid URL format (linkedin_url)
        response = client.post("/api/v1/people/", json={
            "name": "Test User",
            "linkedin_url": "not-a-url"
        })
        assert response.status_code == 422 