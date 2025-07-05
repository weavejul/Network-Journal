"""
Neo4j operations for Company nodes.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import Company
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


def create_company(company: Company) -> Company:
    """Create a new Company node in Neo4j."""
    if not company.id:
        company.id = str(uuid4())
    
    now = datetime.now(UTC)
    company.created_at = now
    company.updated_at = now
    
    # Convert HttpUrl to string for Neo4j compatibility
    company_data = company.model_dump()
    if company_data.get('website'):
        company_data['website'] = str(company_data['website'])
    
    cypher_query = """
    CREATE (c:Company {
        id: $id,
        name: $name,
        industry: $industry,
        website: $website,
        created_at: $created_at,
        updated_at: $updated_at
    })
    RETURN c
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, **company_data)
        created_company = _convert_neo4j_record(result.single()["c"])
        logger.info(f"Created company: {company.name} with ID: {company.id}")
        return Company(**created_company)


def get_company(company_id: str) -> Optional[Company]:
    """Get a Company node by ID."""
    cypher_query = """
    MATCH (c:Company {id: $company_id})
    RETURN c
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, company_id=company_id)
        record = result.single()
        if record:
            company_data = _convert_neo4j_record(record["c"])
            return Company(**company_data)
        return None


def list_companies() -> List[Company]:
    """List all Company nodes."""
    cypher_query = """
    MATCH (c:Company)
    RETURN c
    ORDER BY c.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        companies = []
        for record in result:
            company_data = _convert_neo4j_record(record["c"])
            companies.append(Company(**company_data))
        return companies


def update_company(company_id: str, company_data: Dict[str, Any]) -> Optional[Company]:
    """Update a Company node."""
    # Remove None values and add updated_at timestamp
    update_data = {k: v for k, v in company_data.items() if v is not None}
    update_data["updated_at"] = datetime.now(UTC)
    
    # Convert HttpUrl to string for Neo4j compatibility
    if update_data.get('website'):
        update_data['website'] = str(update_data['website'])
    
    # Build dynamic SET clause
    set_clause = ", ".join([f"c.{key} = ${key}" for key in update_data.keys()])
    
    cypher_query = f"""
    MATCH (c:Company {{id: $company_id}})
    SET {set_clause}
    RETURN c
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, company_id=company_id, **update_data)
        record = result.single()
        if record:
            company_data = _convert_neo4j_record(record["c"])
            logger.info(f"Updated company: {company_id}")
            return Company(**company_data)
        return None


def delete_company(company_id: str) -> bool:
    """Delete a Company node and all its relationships."""
    cypher_query = """
    MATCH (c:Company {id: $company_id})
    DETACH DELETE c
    RETURN count(c) as deleted_count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, company_id=company_id)
        deleted_count = result.single()["deleted_count"]
        if deleted_count > 0:
            logger.info(f"Deleted company: {company_id}")
            return True
        return False


def search_companies(query: str) -> List[Company]:
    """Search companies by name or industry."""
    cypher_query = """
    MATCH (c:Company)
    WHERE c.name CONTAINS $query OR c.industry CONTAINS $query
    RETURN c
    ORDER BY c.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, query=query)
        companies = []
        for record in result:
            company_data = _convert_neo4j_record(record["c"])
            companies.append(Company(**company_data))
        return companies


def get_company_by_name(name: str) -> Optional[Company]:
    """Get a Company node by exact name match."""
    cypher_query = """
    MATCH (c:Company {name: $name})
    RETURN c
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, name=name)
        record = result.single()
        if record:
            company_data = _convert_neo4j_record(record["c"])
            return Company(**company_data)
        return None 