"""
Neo4j operations for Interaction nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Interaction, InteractionChannel, DataSource
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


def create_interaction(interaction: Interaction) -> Interaction:
    """Create a new Interaction node in Neo4j."""
    if not interaction.id:
        interaction.id = str(uuid4())
    
    now = datetime.now(UTC)
    interaction.created_at = now
    
    cypher_query = """
    CREATE (i:Interaction {
        id: $id,
        date: $date,
        channel: $channel,
        summary: $summary,
        created_at: $created_at,
        data_source: $data_source
    })
    RETURN i
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **interaction.model_dump())
        created_interaction = _convert_neo4j_record(result.single()["i"])
        logger.info(f"Created interaction: {interaction.id}")
        return Interaction(**created_interaction)


def get_interaction(interaction_id: str) -> Optional[Interaction]:
    """Get an Interaction node by ID."""
    cypher_query = """
    MATCH (i:Interaction {id: $interaction_id})
    RETURN i
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id)
        record = result.single()
        if record:
            interaction_data = _convert_neo4j_record(record["i"])
            return Interaction(**interaction_data)
        return None


def list_interactions() -> List[Interaction]:
    """List all Interaction nodes."""
    cypher_query = """
    MATCH (i:Interaction)
    RETURN i
    ORDER BY i.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        interactions = []
        for record in result:
            interaction_data = _convert_neo4j_record(record["i"])
            interactions.append(Interaction(**interaction_data))
        return interactions


def update_interaction(interaction_id: str, interaction_data: Dict[str, Any]) -> Optional[Interaction]:
    """Update an Interaction node."""
    # Remove None values
    update_data = {k: v for k, v in interaction_data.items() if v is not None}
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"i.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (i:Interaction {{id: $interaction_id}})
    SET {set_clause}
    RETURN i
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id, **update_data)
        record = result.single()
        if record:
            interaction_data = _convert_neo4j_record(record["i"])
            logger.info(f"Updated interaction: {interaction_id}")
            return Interaction(**interaction_data)
        return None


def delete_interaction(interaction_id: str) -> bool:
    """Delete an Interaction node and all its relationships."""
    cypher_query = """
    MATCH (i:Interaction {id: $interaction_id})
    DETACH DELETE i
    RETURN count(i) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted interaction: {interaction_id}")
            return True
        return False


def link_interaction_to_person(interaction_id: str, person_id: str) -> bool:
    """Link an interaction to a person."""
    cypher_query = """
    MATCH (i:Interaction {id: $interaction_id})
    MATCH (p:Person {id: $person_id})
    CREATE (p)-[:PARTICIPATED_IN]->(i)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id, person_id=person_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked interaction {interaction_id} to person {person_id}")
            return True
        return False


def get_interactions_for_person(person_id: str) -> List[Interaction]:
    """Get all interactions for a specific person."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[:PARTICIPATED_IN]->(i:Interaction)
    RETURN i
    ORDER BY i.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        interactions = []
        for record in result:
            interaction_data = _convert_neo4j_record(record["i"])
            interactions.append(Interaction(**interaction_data))
        return interactions


def get_people_for_interaction(interaction_id: str) -> List[Dict[str, Any]]:
    """Get all people who participated in an interaction."""
    cypher_query = """
    MATCH (p:Person)-[:PARTICIPATED_IN]->(i:Interaction {id: $interaction_id})
    RETURN p
    ORDER BY p.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id)
        people = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            people.append(person_data)
        return people


def search_interactions(query: str) -> List[Interaction]:
    """Search interactions by summary content."""
    cypher_query = """
    MATCH (i:Interaction)
    WHERE i.summary CONTAINS $query
    RETURN i
    ORDER BY i.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, query=query)
        interactions = []
        for record in result:
            interaction_data = _convert_neo4j_record(record["i"])
            interactions.append(Interaction(**interaction_data))
        return interactions 