"""
Tests for Company CRUD operations.
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


class TestCompanyCRUD:
    """Test Company CRUD operations."""
    
    def test_create_company(self):
        """Test creating a new company."""
        company_data = {
            "name": "Acme Corp",
            "industry": "Technology",
            "website": "https://acme.com"
        }
        
        response = client.post("/api/v1/companies/", json=company_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == company_data["name"]
        assert data["industry"] == company_data["industry"]
        assert data["website"] == company_data["website"] + "/"  # Pydantic adds trailing slash
        assert data["id"] is not None
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
    
    def test_create_company_minimal(self):
        """Test creating a company with only required fields."""
        company_data = {"name": "Simple Corp"}
        
        response = client.post("/api/v1/companies/", json=company_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == company_data["name"]
        assert data["industry"] is None
        assert data["website"] is None
        assert data["id"] is not None
    
    def test_get_company(self):
        """Test getting a company by ID."""
        # First create a company
        company_data = {"name": "Test Company", "industry": "Finance"}
        create_response = client.post("/api/v1/companies/", json=company_data)
        company_id = create_response.json()["id"]
        
        # Then get the company
        response = client.get(f"/api/v1/companies/{company_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == company_data["name"]
        assert data["industry"] == company_data["industry"]
    
    def test_get_company_not_found(self):
        """Test getting a non-existent company."""
        response = client.get("/api/v1/companies/non-existent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"
    
    def test_list_companies(self):
        """Test listing all companies."""
        # Create a few companies first
        companies_data = [
            {"name": "Alpha Corp", "industry": "Technology"},
            {"name": "Beta Inc", "industry": "Healthcare"}
        ]
        
        for company_data in companies_data:
            client.post("/api/v1/companies/", json=company_data)
        
        response = client.get("/api/v1/companies/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check that our created companies are in the list
        names = [company["name"] for company in data]
        assert "Alpha Corp" in names
        assert "Beta Inc" in names
    
    def test_update_company(self):
        """Test updating a company."""
        # First create a company
        company_data = {"name": "Old Company", "industry": "Old Industry"}
        create_response = client.post("/api/v1/companies/", json=company_data)
        company_id = create_response.json()["id"]
        
        # Then update the company
        update_data = {
            "name": "New Company",
            "industry": "New Industry",
            "website": "https://newcompany.com"
        }
        
        response = client.put(f"/api/v1/companies/{company_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == update_data["name"]
        assert data["industry"] == update_data["industry"]
        assert data["website"] == update_data["website"] + "/"  # Pydantic adds trailing slash
        assert data["updated_at"] is not None
    
    def test_update_company_not_found(self):
        """Test updating a non-existent company."""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/companies/non-existent-id", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"
    
    def test_delete_company(self):
        """Test deleting a company."""
        # First create a company
        company_data = {"name": "Delete Me", "industry": "Temporary"}
        create_response = client.post("/api/v1/companies/", json=company_data)
        company_id = create_response.json()["id"]
        
        # Then delete the company
        response = client.delete(f"/api/v1/companies/{company_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Company deleted"
        
        # Verify the company is deleted
        get_response = client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 404
    
    def test_delete_company_not_found(self):
        """Test deleting a non-existent company."""
        response = client.delete("/api/v1/companies/non-existent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"
    
    def test_company_validation(self):
        """Test company data validation."""
        # Test missing required field
        response = client.post("/api/v1/companies/", json={})
        assert response.status_code == 422
        
        # Test invalid URL format
        response = client.post("/api/v1/companies/", json={
            "name": "Test Company",
            "website": "not-a-url"
        })
        assert response.status_code == 422 