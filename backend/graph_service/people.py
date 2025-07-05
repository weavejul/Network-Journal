"""
Neo4j operations for Person nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Person, ContactStatus, DataSource, RelationshipType
from shared.utils import setup_logging
from .connection import get_session_context

logger = setup_logging(__name__)


def _convert_neo4j_datetime(neo4j_datetime):
    """Convert Neo4j datetime to Python datetime."""
    if neo4j_datetime is None:
        return None
    if hasattr(neo4j_datetime, 'to_native'):
        return neo4j_datetime.to_native()
    return neo4j_datetime


def _convert_neo4j_record(record):
    """Convert Neo4j record to dict with proper datetime conversion."""
    data = dict(record)
    for key, value in data.items():
        if hasattr(value, 'to_native'):  # Neo4j datetime object
            data[key] = value.to_native()
    return data


def create_person(person: Person) -> Person:
    """Create a new Person node in Neo4j."""
    if not person.id:
        person.id = str(uuid4())
    
    now = datetime.now(UTC)
    person.created_at = now
    person.updated_at = now
    
    # Convert HttpUrl to string for Neo4j compatibility
    person_data = person.model_dump()
    if person_data.get('linkedin_url'):
        person_data['linkedin_url'] = str(person_data['linkedin_url'])
    
    cypher_query = """
    CREATE (p:Person {
        id: $id,
        name: $name,
        email: $email,
        phone: $phone,
        linkedin_url: $linkedin_url,
        last_contacted_date: $last_contacted_date,
        birthday: $birthday,
        source_of_contact: $source_of_contact,
        status: $status,
        notes: $notes,
        created_at: $created_at,
        updated_at: $updated_at,
        data_source: $data_source
    })
    RETURN p
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **person_data)
        created_person = _convert_neo4j_record(result.single()["p"])
        logger.info(f"Created person: {person.name} with ID: {person.id}")
        return Person(**created_person)


def get_person(person_id: str) -> Optional[Person]:
    """Get a Person node by ID."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    RETURN p
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        record = result.single()
        if record:
            person_data = _convert_neo4j_record(record["p"])
            return Person(**person_data)
        return None


def list_people() -> List[Person]:
    """List all Person nodes."""
    cypher_query = """
    MATCH (p:Person)
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people


def update_person(person_id: str, person_data: Dict[str, Any]) -> Optional[Person]:
    """Update a Person node."""
    # Remove None values and add updated_at timestamp
    update_data = {k: v for k, v in person_data.items() if v is not None}
    update_data["updated_at"] = datetime.now(UTC)
    
    # Convert HttpUrl to string for Neo4j compatibility
    if update_data.get('linkedin_url'):
        update_data['linkedin_url'] = str(update_data['linkedin_url'])
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"p.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (p:Person {{id: $person_id}})
    SET {set_clause}
    RETURN p
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, **update_data)
        record = result.single()
        if record:
            person_data = _convert_neo4j_record(record["p"])
            logger.info(f"Updated person: {person_id}")
            return Person(**person_data)
        return None


def delete_person(person_id: str) -> bool:
    """Delete a Person node and all its relationships."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    DETACH DELETE p
    RETURN count(p) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted person: {person_id}")
            return True
        return False


def get_person_by_name(name: str) -> Optional[Person]:
    """Get a Person node by exact name match."""
    cypher_query = """
    MATCH (p:Person {name: $name})
    RETURN p
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, name=name)
        record = result.single()
        if record:
            person_data = _convert_neo4j_record(record["p"])
            return Person(**person_data)
        return None


def search_people(query: str) -> List[Person]:
    """Search people by name or email with fuzzy matching."""
    cypher_query = """
    MATCH (p:Person)
    WHERE p.name CONTAINS $search_query OR p.email CONTAINS $search_query
    RETURN p
    ORDER BY 
        CASE 
            WHEN p.name = $search_query THEN 1
            WHEN p.name STARTS WITH $search_query THEN 2
            ELSE 3
        END,
        p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, search_query=query)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people


# Employment relationship functions

def link_person_to_company(person_id: str, company_id: str, role: str, start_date: datetime, end_date: Optional[datetime] = None) -> bool:
    """Link a person to a company with employment details."""
    now = datetime.now(UTC)
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    MATCH (c:Company {id: $company_id})
    MERGE (p)-[r:WORKS_AT]->(c)
    SET r.role = $role, r.start_date = $start_date, r.end_date = $end_date, r.created_at = $created_at
    RETURN count(r) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, 
                           person_id=person_id, company_id=company_id, 
                           role=role, start_date=start_date, end_date=end_date, created_at=now)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked person {person_id} to company {company_id} as {role}")
            return True
        return False


def get_employment_history(person_id: str) -> List[Dict[str, Any]]:
    """Get employment history for a person."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:WORKS_AT]->(c:Company)
    RETURN c, r.role as role, r.start_date as start_date, r.end_date as end_date
    ORDER BY r.start_date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        employment = []
        for record in result:
            company_data = _convert_neo4j_record(record["c"])
            employment.append({
                "company": company_data,
                "role": record["role"],
                "start_date": _convert_neo4j_datetime(record["start_date"]),
                "end_date": _convert_neo4j_datetime(record["end_date"])
            })
        return employment


def get_current_employer(person_id: str) -> Optional[Dict[str, Any]]:
    """Get the current employer for a person."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:WORKS_AT]->(c:Company)
    WHERE r.end_date IS NULL
    RETURN c, r.role as role, r.start_date as start_date
    LIMIT 1
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        record = result.single()
        if record:
            company_data = _convert_neo4j_record(record["c"])
            return {
                "company": company_data,
                "role": record["role"],
                "start_date": _convert_neo4j_datetime(record["start_date"])
            }
        return None


def get_employees_at_company(company_id: str) -> List[Dict[str, Any]]:
    """Get all employees at a company."""
    cypher_query = """
    MATCH (p:Person)-[r:WORKS_AT]->(c:Company {id: $company_id})
    WHERE r.end_date IS NULL
    RETURN p, r.role as role, r.start_date as start_date
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, company_id=company_id)
        employees = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            employees.append({
                "person": person_data,
                "role": record["role"],
                "start_date": _convert_neo4j_datetime(record["start_date"])
            })
        return employees


# Person-to-person relationship functions

def create_person_relationship(from_person_id: str, to_person_id: str, relationship_type: RelationshipType, strength: int) -> bool:
    """Create a relationship between two people."""
    now = datetime.now(UTC)
    cypher_query = """
    MATCH (p1:Person {id: $from_person_id})
    MATCH (p2:Person {id: $to_person_id})
    MERGE (p1)-[r:KNOWS]->(p2)
    SET r.type = $relationship_type, r.strength = $strength, r.created_at = $created_at
    RETURN count(r) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, 
                           from_person_id=from_person_id, to_person_id=to_person_id,
                           relationship_type=relationship_type, strength=strength, created_at=now)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Created relationship between {from_person_id} and {to_person_id}")
            return True
        return False


def get_person_relationships(person_id: str) -> List[Dict[str, Any]]:
    """Get all relationships for a person."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:KNOWS]->(other:Person)
    RETURN other, r.type as type, r.strength as strength, r.created_at as created_at
    ORDER BY other.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        relationships = []
        for record in result:
            person_data = _convert_neo4j_record(record["other"])
            relationships.append({
                "person": person_data,
                "type": record["type"],
                "strength": record["strength"],
                "created_at": _convert_neo4j_datetime(record["created_at"])
            })
        return relationships


def get_people_by_relationship_type(person_id: str, relationship_type: RelationshipType) -> List[Dict[str, Any]]:
    """Get people connected to a person by a specific relationship type."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:KNOWS]->(other:Person)
    WHERE r.type = $relationship_type
    RETURN other, r.strength as strength
    ORDER BY other.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, relationship_type=relationship_type)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["other"])
            people.append({
                "person": person_data,
                "strength": record["strength"]
            })
        return people


# Advanced query functions

def get_network_connections(person_id: str, depth: int = 2) -> Dict[str, Any]:
    """Get network connections up to a certain depth."""
    cypher_query = """
    MATCH path = (p:Person {id: $person_id})-[*1..$depth]-(connected:Person)
    WHERE connected.id <> $person_id
    RETURN connected, length(path) as distance
    ORDER BY distance, connected.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, depth=depth)
        connections = []
        for record in result:
            person_data = _convert_neo4j_record(record["connected"])
            connections.append({
                "person": person_data,
                "distance": record["distance"]
            })
        return {"connections": connections, "depth": depth}


def get_people_by_company_and_role(company_id: str, role: str) -> List[Person]:
    """Get people at a company with a specific role."""
    cypher_query = """
    MATCH (p:Person)-[r:WORKS_AT]->(c:Company {id: $company_id})
    WHERE r.role CONTAINS $role AND r.end_date IS NULL
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, company_id=company_id, role=role)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people


def get_people_needing_followup() -> List[Person]:
    """Get people who need follow-up (status = needs_follow_up)."""
    cypher_query = """
    MATCH (p:Person)
    WHERE p.status = 'needs_follow_up'
    RETURN p
    ORDER BY p.last_contacted_date ASC NULLS FIRST
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people


def get_people_by_birthday_month(month: int) -> List[Person]:
    """Get people with birthdays in a specific month."""
    cypher_query = """
    MATCH (p:Person)
    WHERE p.birthday IS NOT NULL AND month(p.birthday) = $month
    RETURN p
    ORDER BY day(p.birthday)
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, month=month)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people


def get_people_by_location(location_id: str) -> List[Person]:
    """Get people who live at a specific location."""
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
            people.append(Person(**person_data))
        return people


def get_people_by_topic(topic_id: str) -> List[Person]:
    """Get people interested in a specific topic."""
    cypher_query = """
    MATCH (p:Person)-[:INTERESTED_IN]->(t:Topic {id: $topic_id})
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, topic_id=topic_id)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(Person(**person_data))
        return people 