from fastapi import APIRouter, HTTPException
from typing import List
from shared.types import Company, APIResponse
from backend.graph_service.companies import (
    create_company as neo4j_create_company,
    get_company as neo4j_get_company,
    list_companies as neo4j_list_companies,
    update_company as neo4j_update_company,
    delete_company as neo4j_delete_company
)

router = APIRouter()

@router.get("/", response_model=List[Company])
def list_companies():
    """List all companies."""
    return neo4j_list_companies()

@router.get("/{company_id}", response_model=Company)
def get_company(company_id: str):
    """Get a company by ID."""
    company = neo4j_get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/", response_model=Company)
def create_company(company: Company):
    """Create a new company."""
    return neo4j_create_company(company)

@router.put("/{company_id}", response_model=Company)
def update_company(company_id: str, company_data: Company):
    """Update an existing company."""
    updated_company = neo4j_update_company(company_id, company_data.model_dump())
    if not updated_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated_company

@router.delete("/{company_id}", response_model=APIResponse)
def delete_company(company_id: str):
    """Delete a company by ID."""
    success = neo4j_delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
    return APIResponse(success=True, message="Company deleted") 