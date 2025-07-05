"""
API router for Location operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
from pathlib import Path

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.types import Location, APIResponse, PaginatedResponse
from shared.utils import setup_logging
from backend.graph_service import locations as location_service

logger = setup_logging(__name__)
router = APIRouter(tags=["locations"])


@router.post("/", response_model=APIResponse)
async def create_location(location: Location):
    """Create a new location."""
    try:
        created_location = location_service.create_location(location)
        return APIResponse(
            success=True,
            data=created_location.model_dump(),
            message="Location created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_locations(
    search: Optional[str] = Query(None, description="Search locations by city, state, or country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List all locations with optional search, filtering, and pagination."""
    try:
        if search:
            locations = location_service.search_locations(search)
        elif city:
            locations = location_service.get_locations_by_city(city)
        elif state:
            locations = location_service.get_locations_by_state(state)
        elif country:
            locations = location_service.get_locations_by_country(country)
        else:
            locations = location_service.list_locations()
        
        # Simple pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_locations = locations[start_idx:end_idx]
        
        return APIResponse(
            success=True,
            data=PaginatedResponse(
                items=[location.model_dump() for location in paginated_locations],
                total=len(locations),
                page=page,
                page_size=page_size,
                total_pages=(len(locations) + page_size - 1) // page_size
            ).model_dump(),
            message="Locations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular", response_model=APIResponse)
async def get_popular_locations(limit: int = Query(10, ge=1, le=50, description="Number of locations to return")):
    """Get the most popular locations (by number of people living there)."""
    try:
        locations = location_service.get_popular_locations(limit)
        return APIResponse(
            success=True,
            data=locations,
            message="Popular locations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting popular locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=APIResponse)
async def get_location(location_id: str):
    """Get a location by ID."""
    try:
        location = location_service.get_location(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return APIResponse(
            success=True,
            data=location.model_dump(),
            message="Location retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{location_id}", response_model=APIResponse)
async def update_location(location_id: str, location_data: dict):
    """Update a location."""
    try:
        updated_location = location_service.update_location(location_id, location_data)
        if not updated_location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return APIResponse(
            success=True,
            data=updated_location.model_dump(),
            message="Location updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}", response_model=APIResponse)
async def delete_location(location_id: str):
    """Delete a location."""
    try:
        success = location_service.delete_location(location_id)
        if not success:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return APIResponse(
            success=True,
            message="Location deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Relationship endpoints

@router.post("/{location_id}/people/{person_id}", response_model=APIResponse)
async def link_person_to_location(location_id: str, person_id: str):
    """Link a person to a location (person lives in location)."""
    try:
        success = location_service.link_person_to_location(person_id, location_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link person to location")
        
        return APIResponse(
            success=True,
            message="Person linked to location successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking person to location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}/people/{person_id}", response_model=APIResponse)
async def unlink_person_from_location(location_id: str, person_id: str):
    """Unlink a person from a location."""
    try:
        success = location_service.unlink_person_from_location(person_id, location_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unlink person from location")
        
        return APIResponse(
            success=True,
            message="Person unlinked from location successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking person from location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/people", response_model=APIResponse)
async def get_people_at_location(location_id: str):
    """Get all people who live at a specific location."""
    try:
        people = location_service.get_people_at_location(location_id)
        return APIResponse(
            success=True,
            data=people,
            message="People at location retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting people at location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Special query endpoints

@router.get("/with-events", response_model=APIResponse)
async def get_locations_with_events(limit: int = Query(10, ge=1, le=50, description="Number of locations to return")):
    """Get locations that have hosted events, ordered by number of events."""
    try:
        locations = location_service.get_locations_with_events(limit)
        return APIResponse(
            success=True,
            data=locations,
            message="Locations with events retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting locations with events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-or-create", response_model=APIResponse)
async def find_or_create_location(
    city: str = Query(..., description="City name"),
    state: Optional[str] = Query(None, description="State/province"),
    country: Optional[str] = Query(None, description="Country")
):
    """Find an existing location or create a new one if it doesn't exist."""
    try:
        location = location_service.find_or_create_location(city, state, country)
        return APIResponse(
            success=True,
            data=location.model_dump(),
            message="Location found or created successfully"
        )
    except Exception as e:
        logger.error(f"Error finding or creating location: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 