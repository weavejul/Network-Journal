"""
API router for Topic operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
from pathlib import Path
from pydantic import ValidationError

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.types import Topic, APIResponse, PaginatedResponse
from shared.utils import setup_logging
from backend.graph_service import topics as topic_service

logger = setup_logging(__name__)
router = APIRouter(tags=["topics"])


@router.post("/", response_model=APIResponse)
async def create_topic(topic: Topic):
    """Create a new topic."""
    try:
        created_topic = topic_service.create_topic(topic)
        return APIResponse(
            success=True,
            data=created_topic.model_dump(),
            message="Topic created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_topics(
    search: Optional[str] = Query(None, description="Search topics by name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List all topics with optional search and pagination."""
    try:
        if search:
            topics = topic_service.search_topics(search)
        else:
            topics = topic_service.list_topics()
        
        # Simple pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_topics = topics[start_idx:end_idx]
        
        return APIResponse(
            success=True,
            data=PaginatedResponse(
                items=[topic.model_dump() for topic in paginated_topics],
                total=len(topics),
                page=page,
                page_size=page_size,
                total_pages=(len(topics) + page_size - 1) // page_size
            ).model_dump(),
            message="Topics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular", response_model=APIResponse)
async def get_popular_topics(limit: int = Query(10, ge=1, le=50, description="Number of topics to return")):
    """Get the most popular topics (by number of people interested)."""
    try:
        topics = topic_service.get_popular_topics(limit)
        return APIResponse(
            success=True,
            data=topics,
            message="Popular topics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting popular topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}", response_model=APIResponse)
async def get_topic(topic_id: str):
    """Get a topic by ID."""
    try:
        topic = topic_service.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return APIResponse(
            success=True,
            data=topic.model_dump(),
            message="Topic retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}", response_model=APIResponse)
async def update_topic(topic_id: str, topic_data: dict):
    """Update a topic."""
    try:
        updated_topic = topic_service.update_topic(topic_id, topic_data)
        if not updated_topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return APIResponse(
            success=True,
            data=updated_topic.model_dump(),
            message="Topic updated successfully"
        )
    except ValueError as ve:
        logger.error(f"Validation error updating topic: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except ValidationError as ve:
        logger.error(f"Validation error updating topic: {ve}")
        raise HTTPException(status_code=422, detail=ve.errors())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}", response_model=APIResponse)
async def delete_topic(topic_id: str):
    """Delete a topic."""
    try:
        success = topic_service.delete_topic(topic_id)
        if not success:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return APIResponse(
            success=True,
            message="Topic deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Relationship endpoints

@router.post("/{topic_id}/people/{person_id}", response_model=APIResponse)
async def link_person_to_topic(topic_id: str, person_id: str):
    """Link a person to a topic (person is interested in topic)."""
    try:
        success = topic_service.link_person_to_topic(person_id, topic_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link person to topic")
        
        return APIResponse(
            success=True,
            message="Person linked to topic successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking person to topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}/people/{person_id}", response_model=APIResponse)
async def unlink_person_from_topic(topic_id: str, person_id: str):
    """Unlink a person from a topic."""
    try:
        success = topic_service.unlink_person_from_topic(person_id, topic_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unlink person from topic")
        
        return APIResponse(
            success=True,
            message="Person unlinked from topic successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking person from topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}/people", response_model=APIResponse)
async def get_people_interested_in_topic(topic_id: str):
    """Get all people interested in a specific topic."""
    try:
        people = topic_service.get_people_interested_in_topic(topic_id)
        return APIResponse(
            success=True,
            data=people,
            message="People interested in topic retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting people interested in topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/interactions/{interaction_id}", response_model=APIResponse)
async def link_interaction_to_topic(topic_id: str, interaction_id: str):
    """Link an interaction to a topic (topic was discussed in interaction)."""
    try:
        success = topic_service.link_interaction_to_topic(interaction_id, topic_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link interaction to topic")
        
        return APIResponse(
            success=True,
            message="Interaction linked to topic successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking interaction to topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}/interactions", response_model=APIResponse)
async def get_interactions_for_topic(topic_id: str):
    """Get all interactions that discussed a specific topic."""
    try:
        interactions = topic_service.get_interactions_for_topic(topic_id)
        return APIResponse(
            success=True,
            data=interactions,
            message="Interactions for topic retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting interactions for topic: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 