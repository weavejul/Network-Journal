"""
Neo4j operations for Event nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Event, EventType
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


def create_event(event: Event) -> Event:
    """Create a new Event node in Neo4j."""
    if not event.id:
        event.id = str(uuid4())
    
    now = datetime.now(UTC)
    event.created_at = now
    
    cypher_query = """
    CREATE (e:Event {
        id: $id,
        name: $name,
        date: $date,
        type: $type,
        location_id: $location_id,
        created_at: $created_at
    })
    RETURN e
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **event.model_dump())
        created_event = _convert_neo4j_record(result.single()["e"])
        logger.info(f"Created event: {event.name} with ID: {event.id}")
        return Event(**created_event)


def get_event(event_id: str) -> Optional[Event]:
    """Get an Event node by ID."""
    cypher_query = """
    MATCH (e:Event {id: $event_id})
    RETURN e
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id)
        record = result.single()
        if record:
            event_data = _convert_neo4j_record(record["e"])
            return Event(**event_data)
        return None


def list_events() -> List[Event]:
    """List all Event nodes."""
    cypher_query = """
    MATCH (e:Event)
    RETURN e
    ORDER BY e.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def update_event(event_id: str, event_data: Dict[str, Any]) -> Optional[Event]:
    """Update an Event node."""
    # Remove None values
    update_data = {k: v for k, v in event_data.items() if v is not None}
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"e.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (e:Event {{id: $event_id}})
    SET {set_clause}
    RETURN e
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id, **update_data)
        record = result.single()
        if record:
            event_data = _convert_neo4j_record(record["e"])
            logger.info(f"Updated event: {event_id}")
            return Event(**event_data)
        return None


def delete_event(event_id: str) -> bool:
    """Delete an Event node and all its relationships."""
    cypher_query = """
    MATCH (e:Event {id: $event_id})
    DETACH DELETE e
    RETURN count(e) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted event: {event_id}")
            return True
        return False


def search_events(search_term: str) -> List[Event]:
    """Search events by name."""
    cypher_query = """
    MATCH (e:Event)
    WHERE e.name CONTAINS $search_term
    RETURN e
    ORDER BY e.date DESC, e.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, search_term=search_term)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def get_events_by_type(event_type: EventType) -> List[Event]:
    """Get all events of a specific type."""
    cypher_query = """
    MATCH (e:Event)
    WHERE e.type = $event_type
    RETURN e
    ORDER BY e.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_type=event_type)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def get_events_by_date_range(start_date: datetime, end_date: datetime) -> List[Event]:
    """Get all events within a date range."""
    cypher_query = """
    MATCH (e:Event)
    WHERE e.date >= $start_date AND e.date <= $end_date
    RETURN e
    ORDER BY e.date
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, start_date=start_date, end_date=end_date)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def link_person_to_event(person_id: str, event_id: str) -> bool:
    """Link a person to an event (person attended event)."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    MATCH (e:Event {id: $event_id})
    MERGE (p)-[:ATTENDED]->(e)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, event_id=event_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked person {person_id} to event {event_id}")
            return True
        return False


def unlink_person_from_event(person_id: str, event_id: str) -> bool:
    """Unlink a person from an event."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:ATTENDED]->(e:Event {id: $event_id})
    DELETE r
    RETURN count(r) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, event_id=event_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Unlinked person {person_id} from event {event_id}")
            return True
        return False


def get_people_at_event(event_id: str) -> List[Dict[str, Any]]:
    """Get all people who attended a specific event."""
    cypher_query = """
    MATCH (p:Person)-[:ATTENDED]->(e:Event {id: $event_id})
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(person_data)
        return people


def get_events_for_person(person_id: str) -> List[Event]:
    """Get all events a person attended."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[:ATTENDED]->(e:Event)
    RETURN e
    ORDER BY e.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def link_event_to_location(event_id: str, location_id: str) -> bool:
    """Link an event to a location (event was held at location)."""
    cypher_query = """
    MATCH (e:Event {id: $event_id})
    MATCH (l:Location {id: $location_id})
    MERGE (e)-[:HELD_AT]->(l)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id, location_id=location_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked event {event_id} to location {location_id}")
            return True
        return False


def get_location_for_event(event_id: str) -> Optional[Dict[str, Any]]:
    """Get the location where an event was held."""
    cypher_query = """
    MATCH (e:Event {id: $event_id})-[:HELD_AT]->(l:Location)
    RETURN l
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, event_id=event_id)
        record = result.single()
        if record:
            location_data = _convert_neo4j_record(record["l"])
            return location_data
        return None


def get_events_at_location(location_id: str) -> List[Event]:
    """Get all events held at a specific location."""
    cypher_query = """
    MATCH (e:Event)-[:HELD_AT]->(l:Location {id: $location_id})
    RETURN e
    ORDER BY e.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, location_id=location_id)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def get_upcoming_events(limit: int = 10) -> List[Event]:
    """Get upcoming events (events with dates in the future)."""
    now = datetime.now(UTC)
    cypher_query = """
    MATCH (e:Event)
    WHERE e.date > $now
    RETURN e
    ORDER BY e.date
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, now=now, limit=limit)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def get_recent_events(limit: int = 10) -> List[Event]:
    """Get recent events (events with dates in the past)."""
    now = datetime.now(UTC)
    cypher_query = """
    MATCH (e:Event)
    WHERE e.date <= $now
    RETURN e
    ORDER BY e.date DESC
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, now=now, limit=limit)
        events = []
        for record in result:
            event_data = _convert_neo4j_record(record["e"])
            events.append(Event(**event_data))
        return events


def get_event_by_name(name: str) -> Optional[Event]:
    """Get an Event node by exact name match."""
    cypher_query = """
    MATCH (e:Event {name: $name})
    RETURN e
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, name=name)
        record = result.single()
        if record:
            event_data = _convert_neo4j_record(record["e"])
            return Event(**event_data)
        return None 