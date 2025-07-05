"""
Neo4j operations for Topic nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Topic
from shared.utils import setup_logging
from .connection import get_session_context

logger = setup_logging(__name__)


def _convert_neo4j_record(record):
    """Convert Neo4j record to dict with proper datetime conversion."""
    data = dict(record)
    for key, value in data.items():
        if hasattr(value, 'to_native'):  # Neo4j datetime object
            data[key] = value.to_native()
        # Handle potential data corruption - ensure name is string
        if key == 'name' and not isinstance(value, str):
            logger.warning(f"Found non-string name value: {value} (type: {type(value)})")
            data[key] = str(value) if value is not None else ""
    return data


def create_topic(topic: Topic) -> Topic:
    """Create a new Topic node in Neo4j."""
    if not topic.id:
        topic.id = str(uuid4())
    
    now = datetime.now(UTC)
    topic.created_at = now
    
    cypher_query = """
    CREATE (t:Topic {
        id: $id,
        name: $name,
        created_at: $created_at
    })
    RETURN t
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **topic.model_dump())
        created_topic = _convert_neo4j_record(result.single()["t"])
        logger.info(f"Created topic: {topic.name} with ID: {topic.id}")
        return Topic(**created_topic)


def get_topic(topic_id: str) -> Optional[Topic]:
    """Get a Topic node by ID."""
    cypher_query = """
    MATCH (t:Topic {id: $topic_id})
    RETURN t
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, topic_id=topic_id)
        record = result.single()
        if record:
            topic_data = _convert_neo4j_record(record["t"])
            return Topic(**topic_data)
        return None


def list_topics() -> List[Topic]:
    """List all Topic nodes."""
    cypher_query = """
    MATCH (t:Topic)
    RETURN t
    ORDER BY t.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            topics.append(Topic(**topic_data))
        return topics


def update_topic(topic_id: str, topic_data: Dict[str, Any]) -> Optional[Topic]:
    """Update a Topic node."""
    # Validate data before updating
    if 'name' in topic_data and not isinstance(topic_data['name'], str):
        raise ValueError(f"Topic name must be a string, got {type(topic_data['name'])}")
    
    # Remove None values
    update_data = {k: v for k, v in topic_data.items() if v is not None}
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"t.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (t:Topic {{id: $topic_id}})
    SET {set_clause}
    RETURN t
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, topic_id=topic_id, **update_data)
        record = result.single()
        if record:
            topic_data = _convert_neo4j_record(record["t"])
            logger.info(f"Updated topic: {topic_id}")
            return Topic(**topic_data)
        return None


def delete_topic(topic_id: str) -> bool:
    """Delete a Topic node and all its relationships."""
    cypher_query = """
    MATCH (t:Topic {id: $topic_id})
    DETACH DELETE t
    RETURN count(t) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, topic_id=topic_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted topic: {topic_id}")
            return True
        return False


def search_topics(search_term: str) -> List[Topic]:
    """Search topics by name."""
    cypher_query = """
    MATCH (t:Topic)
    WHERE t.name CONTAINS $search_term
    RETURN t
    ORDER BY t.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, search_term=search_term)
        topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            topics.append(Topic(**topic_data))
        return topics


def link_person_to_topic(person_id: str, topic_id: str) -> bool:
    """Link a person to a topic (person is interested in topic)."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    MATCH (t:Topic {id: $topic_id})
    MERGE (p)-[:INTERESTED_IN]->(t)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, topic_id=topic_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked person {person_id} to topic {topic_id}")
            return True
        return False


def unlink_person_from_topic(person_id: str, topic_id: str) -> bool:
    """Unlink a person from a topic."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[r:INTERESTED_IN]->(t:Topic {id: $topic_id})
    DELETE r
    RETURN count(r) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, topic_id=topic_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Unlinked person {person_id} from topic {topic_id}")
            return True
        return False


def get_people_interested_in_topic(topic_id: str) -> List[Dict[str, Any]]:
    """Get all people interested in a specific topic."""
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
            people.append(person_data)
        return people


def get_topics_for_person(person_id: str) -> List[Topic]:
    """Get all topics a person is interested in."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[:INTERESTED_IN]->(t:Topic)
    RETURN t
    ORDER BY t.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            topics.append(Topic(**topic_data))
        return topics


def link_interaction_to_topic(interaction_id: str, topic_id: str) -> bool:
    """Link an interaction to a topic (topic was discussed in interaction)."""
    cypher_query = """
    MATCH (i:Interaction {id: $interaction_id})
    MATCH (t:Topic {id: $topic_id})
    MERGE (i)-[:DISCUSSED]->(t)
    RETURN count(*) as link_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id, topic_id=topic_id)
        link_count = result.single()["link_count"]
        if link_count > 0:
            logger.info(f"Linked interaction {interaction_id} to topic {topic_id}")
            return True
        return False


def get_topics_for_interaction(interaction_id: str) -> List[Topic]:
    """Get all topics discussed in an interaction."""
    cypher_query = """
    MATCH (i:Interaction {id: $interaction_id})-[:DISCUSSED]->(t:Topic)
    RETURN t
    ORDER BY t.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, interaction_id=interaction_id)
        topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            topics.append(Topic(**topic_data))
        return topics


def get_interactions_for_topic(topic_id: str) -> List[Dict[str, Any]]:
    """Get all interactions that discussed a specific topic."""
    cypher_query = """
    MATCH (i:Interaction)-[:DISCUSSED]->(t:Topic {id: $topic_id})
    RETURN i
    ORDER BY i.date DESC
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, topic_id=topic_id)
        interactions = []
        for record in result:
            interaction_data = _convert_neo4j_record(record["i"])
            interactions.append(interaction_data)
        return interactions


def get_popular_topics(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the most popular topics (by number of people interested)."""
    cypher_query = """
    MATCH (t:Topic)
    OPTIONAL MATCH (p:Person)-[:INTERESTED_IN]->(t)
    RETURN t, count(p) as interest_count
    ORDER BY interest_count DESC, t.name
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, limit=limit)
        topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            topic_data["interest_count"] = record["interest_count"]
            topics.append(topic_data)
        return topics


def get_topic_by_name(name: str) -> Optional[Topic]:
    """Get a Topic node by exact name match."""
    cypher_query = """
    MATCH (t:Topic {name: $name})
    RETURN t
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, name=name)
        record = result.single()
        if record:
            topic_data = _convert_neo4j_record(record["t"])
            return Topic(**topic_data)
        return None 