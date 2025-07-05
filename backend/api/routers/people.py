from fastapi import APIRouter, HTTPException
from typing import List
from shared.types import Person, APIResponse
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from backend.graph_service.people import (
    create_person as neo4j_create_person,
    get_person as neo4j_get_person,
    list_people as neo4j_list_people,
    update_person as neo4j_update_person,
    delete_person as neo4j_delete_person
)

router = APIRouter()

@router.get("/", response_model=APIResponse)
def list_people():
    """List all people."""
    people = neo4j_list_people()
    return APIResponse(
        success=True,
        data=[person.model_dump() for person in people],
        message="People retrieved successfully"
    )

@router.get("/{person_id}", response_model=APIResponse)
def get_person(person_id: str):
    """Get a person by ID."""
    person = neo4j_get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return APIResponse(
        success=True,
        data=person.model_dump(),
        message="Person retrieved successfully"
    )

@router.post("/", response_model=APIResponse)
def create_person(person: Person):
    """Create a new person."""
    created_person = neo4j_create_person(person)
    return APIResponse(
        success=True,
        data=created_person.model_dump(),
        message="Person created successfully"
    )

@router.put("/{person_id}", response_model=APIResponse)
def update_person(person_id: str, person_data: Person):
    """Update an existing person."""
    updated_person = neo4j_update_person(person_id, person_data.model_dump())
    if not updated_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return APIResponse(
        success=True,
        data=updated_person.model_dump(),
        message="Person updated successfully"
    )

@router.delete("/{person_id}", response_model=APIResponse)
def delete_person(person_id: str):
    """Delete a person by ID."""
    success = neo4j_delete_person(person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return APIResponse(success=True, message="Person deleted successfully") 