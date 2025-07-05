"""
Neo4j operations for Location nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Location
from shared.utils import setup_logging
from .connection import get_session_context

logger = setup_logging(__name__)


def _convert_neo4j_record(record):
    """Convert Neo4j record to dict with proper datetime conversion."""
    data = dict(record)
    for key, value in data.items():
        if hasattr(value, 'to_native'):  # Neo4j datetime object
            data[key] = value.to_native()
    return data


def create_location(location: Location) -> Location:
    """Create a new Location node in Neo4j."""
    if not location.id:
        location.id = str(uuid4())
    
    now = datetime.now(UTC)
    location.created_at = now
    
    cypher_query = """
    CREATE (l:Location {
        id: $id,
        city: $city,
        state: $state,
        country: $country,
        created_at: $created_at
    })
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **location.model_dump())
        created_location = _convert_neo4j_record(result.single()["l"])
        logger.info(f"Created location: {location.city} with ID: {location.id}")
        return Location(**created_location)


def get_location(location_id: str) -> Optional[Location]:
    """Get a Location node by ID."""
    cypher_query = """
    MATCH (l:Location {id: $location_id})
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, location_id=location_id)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            return Location(**location_data)
        return None


def list_locations() -> List[Location]:
    """List all Location nodes."""
    cypher_query = """
    MATCH (l:Location)
    RETURN l
    ORDER BY l.city, l.state, l.country
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            locations.append(Location(**location_data))
        return locations


def update_location(location_id: str, location_data: Dict[str, Any]) -> Optional[Location]:
    """Update a Location node."""
    # Remove None values
    update_data = {k: v for k, v in location_data.items() if v is not None}
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"l.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (l:Location {{id: $location_id}})
    SET {set_clause}
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, location_id=location_id, **update_data)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            logger.info(f"Updated location: {location_id}")
            return Location(**location_data)
        return None


def delete_location(location_id: str) -> bool:
    """Delete a Location node and all its relationships."""
    cypher_query = """
    MATCH (l:Location {id: $location_id})
    DETACH DELETE l
    RETURN count(l) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, location_id=location_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted location: {location_id}")
            return True
        return False


def search_locations(search_term: str) -> List[Location]:
    """Search locations by city, state, or country."""
    cypher_query = """
    MATCH (l:Location)
    WHERE l.city CONTAINS $search_term OR l.state CONTAINS $search_term OR l.country CONTAINS $search_term
    RETURN l
    ORDER BY l.city, l.state, l.country
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, search_term=search_term)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            locations.append(Location(**location_data))
        return locations


def get_locations_by_city(city: str) -> List[Location]:
    """Get all locations in a specific city."""
    cypher_query = """
    MATCH (l:Location)
    WHERE l.city = $city
    RETURN l
    ORDER BY l.state, l.country
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, city=city)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            locations.append(Location(**location_data))
        return locations


def get_locations_by_state(state: str) -> List[Location]:
    """Get all locations in a specific state."""
    cypher_query = """
    MATCH (l:Location)
    WHERE l.state = $state
    RETURN l
    ORDER BY l.city, l.country
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, state=state)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            locations.append(Location(**location_data))
        return locations


def get_locations_by_country(country: str) -> List[Location]:
    """Get all locations in a specific country."""
    cypher_query = """
    MATCH (l:Location)
    WHERE l.country = $country
    RETURN l
    ORDER BY l.city, l.state
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, country=country)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            locations.append(Location(**location_data))
        return locations


def link_person_to_location(person_id: str, location_id: str) -> bool:
    """Link a person to a location (person lives in location)."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    MATCH (l:Location {id: $location_id})
    MERGE (p)-[:LIVES_IN]->(l)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, location_id=location_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked person {person_id} to location {location_id}")
            return True
        return False


def unlink_person_from_location(person_id: str, location_id: str) -> bool:
    """Unlink a person from a location."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:LIVES_IN]->(l:Location {id: $location_id})
    DELETE r
    RETURN count(r) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, location_id=location_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Unlinked person {person_id} from location {location_id}")
            return True
        return False


def get_people_at_location(location_id: str) -> List[Dict[str, Any]]:
    """Get all people who live at a specific location."""
    cypher_query = """
    MATCH (p:Person)-[:LIVES_IN]->(l:Location {id: $location_id})
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, location_id=location_id)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(person_data)
        return people


def get_location_for_person(person_id: str) -> Optional[Dict[str, Any]]:
    """Get the location where a person lives."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[:LIVES_IN]->(l:Location)
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            return location_data
        return None


def get_popular_locations(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the most popular locations (by number of people living there)."""
    cypher_query = """
    MATCH (p:Person)-[:LIVES_IN]->(l:Location)
    RETURN l, count(p) as resident_count
    ORDER BY resident_count DESC
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, limit=limit)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            location_data["resident_count"] = record["resident_count"]
            locations.append(location_data)
        return locations


def get_locations_with_events(limit: int = 10) -> List[Dict[str, Any]]:
    """Get locations that have hosted events, ordered by number of events."""
    cypher_query = """
    MATCH (e:Event)-[:HELD_AT]->(l:Location)
    RETURN l, count(e) as event_count
    ORDER BY event_count DESC
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, limit=limit)
        locations = []
        for record in result:
            location_data = _convert_neo4j_record(record["l"])
            location_data["event_count"] = record["event_count"]
            locations.append(location_data)
        return locations


def find_or_create_location(city: str, state: Optional[str] = None, country: Optional[str] = None) -> Location:
    """Find an existing location or create a new one if it doesn't exist."""
    # First try to find existing location
    if state and country:
        cypher_query = """
        MATCH (l:Location)
        WHERE l.city = $city AND l.state = $state AND l.country = $country
        RETURN l
        """
        params = {"city": city, "state": state, "country": country}
    elif state:
        cypher_query = """
        MATCH (l:Location)
        WHERE l.city = $city AND l.state = $state
        RETURN l
        """
        params = {"city": city, "state": state}
    else:
        cypher_query = """
        MATCH (l:Location)
        WHERE l.city = $city
        RETURN l
        """
        params = {"city": city}
    
    with get_session_context() as session:
        result = session.run(cypher_query, **params)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            return Location(**location_data)
        
        # Create new location if not found
        new_location = Location(city=city, state=state, country=country)
        return create_location(new_location)


def get_location_by_city(city: str) -> Optional[Location]:
    """Get a Location node by exact city match."""
    cypher_query = """
    MATCH (l:Location {city: $city})
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, city=city)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            return Location(**location_data)
        return None 