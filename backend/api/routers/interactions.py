from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from shared.types import Interaction, APIResponse, InteractionUpdate
from backend.graph_service.interactions import (
    create_interaction as neo4j_create_interaction,
    get_interaction as neo4j_get_interaction,
    list_interactions as neo4j_list_interactions,
    update_interaction as neo4j_update_interaction,
    delete_interaction as neo4j_delete_interaction,
    link_interaction_to_person as neo4j_link_interaction_to_person,
    get_interactions_for_person as neo4j_get_interactions_for_person,
    get_people_for_interaction as neo4j_get_people_for_interaction
)

router = APIRouter()

@router.get("/", response_model=APIResponse)
def list_interactions():
    """List all interactions."""
    interactions = neo4j_list_interactions()
    return APIResponse(
        success=True,
        data=[interaction.model_dump() for interaction in interactions],
        message="Interactions retrieved successfully"
    )

@router.get("/{interaction_id}", response_model=APIResponse)
def get_interaction(interaction_id: str):
    """Get an interaction by ID."""
    interaction = neo4j_get_interaction(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return APIResponse(
        success=True,
        data=interaction.model_dump(),
        message="Interaction retrieved successfully"
    )

@router.post("/", response_model=APIResponse)
def create_interaction(interaction: Interaction):
    """Create a new interaction."""
    created = neo4j_create_interaction(interaction)
    return APIResponse(
        success=True,
        data=created.model_dump(),
        message="Interaction created successfully"
    )

@router.put("/{interaction_id}", response_model=APIResponse)
def update_interaction(interaction_id: str, interaction_data: InteractionUpdate):
    """Update an existing interaction."""
    updated_interaction = neo4j_update_interaction(interaction_id, interaction_data.model_dump(exclude_unset=True))
    if not updated_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return APIResponse(
        success=True,
        data=updated_interaction.model_dump(),
        message="Interaction updated successfully"
    )

@router.delete("/{interaction_id}", response_model=APIResponse)
def delete_interaction(interaction_id: str):
    """Delete an interaction by ID."""
    success = neo4j_delete_interaction(interaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return APIResponse(success=True, message="Interaction deleted")

@router.post("/{interaction_id}/link-person/{person_id}", response_model=APIResponse)
def link_interaction_to_person(interaction_id: str, person_id: str):
    """Link an interaction to a person."""
    success = neo4j_link_interaction_to_person(interaction_id, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction or person not found")
    return APIResponse(success=True, message="Interaction linked to person")

@router.get("/person/{person_id}", response_model=APIResponse)
def get_interactions_for_person(person_id: str):
    """Get all interactions for a specific person."""
    interactions = neo4j_get_interactions_for_person(person_id)
    return APIResponse(
        success=True,
        data=[interaction.model_dump() for interaction in interactions],
        message="Interactions for person retrieved successfully"
    )

@router.get("/{interaction_id}/people", response_model=APIResponse)
def get_people_for_interaction(interaction_id: str):
    """Get all people who participated in an interaction."""
    people = neo4j_get_people_for_interaction(interaction_id)
    return APIResponse(
        success=True,
        data=people,
        message="People for interaction retrieved successfully"
    ) 