"""
API router for Event operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.types import Event, EventType, APIResponse, PaginatedResponse
from shared.utils import setup_logging
from backend.graph_service import events as event_service

logger = setup_logging(__name__)
router = APIRouter(tags=["events"])


@router.post("/", response_model=APIResponse)
async def create_event(event: Event):
    """Create a new event."""
    try:
        created_event = event_service.create_event(event)
        return APIResponse(
            success=True,
            data=created_event.model_dump(),
            message="Event created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_events(
    search: Optional[str] = Query(None, description="Search events by name"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List all events with optional search, filtering, and pagination."""
    try:
        if search:
            events = event_service.search_events(search)
        elif event_type:
            events = event_service.get_events_by_type(event_type)
        else:
            events = event_service.list_events()
        
        # Simple pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_events = events[start_idx:end_idx]
        
        return APIResponse(
            success=True,
            data=PaginatedResponse(
                items=[event.model_dump() for event in paginated_events],
                total=len(events),
                page=page,
                page_size=page_size,
                total_pages=(len(events) + page_size - 1) // page_size
            ).model_dump(),
            message="Events retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming", response_model=APIResponse)
async def get_upcoming_events(limit: int = Query(10, ge=1, le=50, description="Number of events to return")):
    """Get upcoming events (events with dates in the future)."""
    try:
        events = event_service.get_upcoming_events(limit)
        return APIResponse(
            success=True,
            data=[event.model_dump() for event in events],
            message="Upcoming events retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=APIResponse)
async def get_recent_events(limit: int = Query(10, ge=1, le=50, description="Number of events to return")):
    """Get recent events (events with dates in the past)."""
    try:
        events = event_service.get_recent_events(limit)
        return APIResponse(
            success=True,
            data=[event.model_dump() for event in events],
            message="Recent events retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting recent events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=APIResponse)
async def get_event(event_id: str):
    """Get an event by ID."""
    try:
        event = event_service.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return APIResponse(
            success=True,
            data=event.model_dump(),
            message="Event retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{event_id}", response_model=APIResponse)
async def update_event(event_id: str, event_data: dict):
    """Update an event."""
    try:
        updated_event = event_service.update_event(event_id, event_data)
        if not updated_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return APIResponse(
            success=True,
            data=updated_event.model_dump(),
            message="Event updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}", response_model=APIResponse)
async def delete_event(event_id: str):
    """Delete an event."""
    try:
        success = event_service.delete_event(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return APIResponse(
            success=True,
            message="Event deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Relationship endpoints

@router.post("/{event_id}/people/{person_id}", response_model=APIResponse)
async def link_person_to_event(event_id: str, person_id: str):
    """Link a person to an event (person attended event)."""
    try:
        success = event_service.link_person_to_event(person_id, event_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link person to event")
        
        return APIResponse(
            success=True,
            message="Person linked to event successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking person to event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}/people/{person_id}", response_model=APIResponse)
async def unlink_person_from_event(event_id: str, person_id: str):
    """Unlink a person from an event."""
    try:
        success = event_service.unlink_person_from_event(person_id, event_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unlink person from event")
        
        return APIResponse(
            success=True,
            message="Person unlinked from event successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking person from event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}/people", response_model=APIResponse)
async def get_people_at_event(event_id: str):
    """Get all people who attended a specific event."""
    try:
        people = event_service.get_people_at_event(event_id)
        return APIResponse(
            success=True,
            data=people,
            message="People at event retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting people at event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{event_id}/locations/{location_id}", response_model=APIResponse)
async def link_event_to_location(event_id: str, location_id: str):
    """Link an event to a location (event was held at location)."""
    try:
        success = event_service.link_event_to_location(event_id, location_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link event to location")
        
        return APIResponse(
            success=True,
            message="Event linked to location successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking event to location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}/location", response_model=APIResponse)
async def get_location_for_event(event_id: str):
    """Get the location where an event was held."""
    try:
        location = event_service.get_location_for_event(event_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found for event")
        
        return APIResponse(
            success=True,
            data=location,
            message="Location for event retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location for event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Special query endpoints

@router.get("/by-date-range", response_model=APIResponse)
async def get_events_by_date_range(
    start_date: datetime = Query(..., description="Start date for range"),
    end_date: datetime = Query(..., description="End date for range")
):
    """Get all events within a date range."""
    try:
        events = event_service.get_events_by_date_range(start_date, end_date)
        return APIResponse(
            success=True,
            data=[event.model_dump() for event in events],
            message="Events in date range retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting events by date range: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 