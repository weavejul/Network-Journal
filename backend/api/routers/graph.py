"""
Graph-related API endpoints for network visualization and analysis.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import APIRouter, HTTPException, Query
from shared.types import APIResponse
from shared.utils import setup_logging
from backend.graph_service.people import list_people
from backend.graph_service.companies import list_companies
from backend.graph_service.topics import list_topics
from backend.graph_service.events import list_events
from backend.graph_service.locations import list_locations
from backend.graph_service.interactions import list_interactions
from backend.graph_service.graph_queries import (
    get_full_network_graph,
    get_person_network_graph,
    get_person_details,
    get_network_statistics,
    get_network_insights,
    search_network,
    get_network_paths,
    get_network_clusters,
    get_network_recommendations
)

logger = setup_logging(__name__)
router = APIRouter(tags=["graph"])


def _convert_neo4j_record(record):
    """Convert Neo4j record to dict with proper datetime conversion."""
    data = dict(record)
    for key, value in data.items():
        if hasattr(value, 'to_native'):  # Neo4j datetime object
            data[key] = value.to_native()
        elif value is None:
            data[key] = None
    return data


@router.get("/full", response_model=APIResponse)
async def get_full_network_graph():
    """Get the complete network graph for visualization."""
    try:
        graph = get_full_network_graph()
        return APIResponse(success=True, data=graph.model_dump(), message="Full network graph retrieved")
    except Exception as e:
        logger.error(f"Error getting full network graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/person/{person_id}", response_model=APIResponse)
async def get_person_network_graph(person_id: str, depth: int = Query(2, ge=1, le=5)):
    """Get a person's network graph up to a certain depth."""
    try:
        graph = get_person_network_graph(person_id, depth)
        return APIResponse(success=True, data=graph.model_dump(), message="Person network graph retrieved")
    except Exception as e:
        logger.error(f"Error getting person network graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/person/{person_id}/details", response_model=APIResponse)
async def get_person_details_endpoint(person_id: str):
    """Get detailed information about a person including relationships."""
    try:
        person_details = get_person_details(person_id)
        if not person_details:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return APIResponse(
            success=True,
            data=person_details,
            message="Person details retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting person details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_network_statistics():
    """Get overall network statistics."""
    try:
        stats = get_network_statistics()
        return APIResponse(success=True, data=stats, message="Network statistics retrieved")
    except Exception as e:
        logger.error(f"Error getting network statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=APIResponse)
async def get_network_insights():
    """Get insights about the network."""
    try:
        insights = get_network_insights()
        return APIResponse(success=True, data=insights, message="Network insights retrieved")
    except Exception as e:
        logger.error(f"Error getting network insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=APIResponse)
async def search_network(query: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search across the entire network."""
    try:
        results = search_network(query, limit)
        return APIResponse(success=True, data=results, message="Network search results")
    except Exception as e:
        logger.error(f"Error searching network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paths", response_model=APIResponse)
async def get_network_paths(from_person_id: str, to_person_id: str, max_length: int = Query(3, ge=1, le=6)):
    """Find paths between two people in the network."""
    try:
        paths = get_network_paths(from_person_id, to_person_id, max_length)
        return APIResponse(success=True, data=paths, message="Network paths found")
    except Exception as e:
        logger.error(f"Error finding network paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters", response_model=APIResponse)
async def get_network_clusters():
    """Identify clusters or communities in the network."""
    try:
        clusters = get_network_clusters()
        return APIResponse(success=True, data=clusters, message="Network clusters identified")
    except Exception as e:
        logger.error(f"Error getting network clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{person_id}", response_model=APIResponse)
async def get_network_recommendations(person_id: str, limit: int = Query(5, ge=1, le=20)):
    """Get network recommendations for a person."""
    try:
        recommendations = get_network_recommendations(person_id, limit)
        return APIResponse(success=True, data=recommendations, message="Network recommendations retrieved")
    except Exception as e:
        logger.error(f"Error getting network recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=APIResponse)
async def get_graph_data():
    """Get all graph data for visualization (nodes and real edges)."""
    try:
        # Fetch all entities
        people = list_people()
        companies = list_companies()
        topics = list_topics()
        events = list_events()
        locations = list_locations()
        interactions = list_interactions()

        # Convert to graph format
        nodes = []
        edges = []

        # Add people nodes
        for person in people:
            nodes.append({
                "id": person.id,
                "label": person.name,
                "type": "person",
                "properties": person.model_dump()
            })

        # Add company nodes
        for company in companies:
            nodes.append({
                "id": company.id,
                "label": company.name,
                "type": "company",
                "properties": company.model_dump()
            })

        # Add topic nodes
        for topic in topics:
            nodes.append({
                "id": topic.id,
                "label": topic.name,
                "type": "topic",
                "properties": topic.model_dump()
            })

        # Add event nodes
        for event in events:
            nodes.append({
                "id": event.id,
                "label": event.name,
                "type": "event",
                "properties": event.model_dump()
            })

        # Add location nodes
        for location in locations:
            nodes.append({
                "id": location.id,
                "label": location.city,
                "type": "location",
                "properties": location.model_dump()
            })

        # Add interaction nodes
        for interaction in interactions:
            # Create a readable label for the interaction
            try:
                # Parse the date and format it nicely
                if isinstance(interaction.date, str):
                    date_obj = datetime.fromisoformat(interaction.date.replace('Z', '+00:00'))
                else:
                    date_obj = interaction.date
                date_str = date_obj.strftime("%Y-%m-%d")
                
                # Create a readable channel name
                channel_map = {
                    "in_person": "Meeting",
                    "call": "Phone Call", 
                    "email": "Email",
                    "video_call": "Video Call",
                    "text": "Text Message"
                }
                channel_name = channel_map.get(interaction.channel, interaction.channel.title())
                
                # Use summary if available, otherwise use channel + date
                if interaction.summary and len(interaction.summary) > 0:
                    # Truncate summary if too long
                    summary = interaction.summary[:30] + "..." if len(interaction.summary) > 30 else interaction.summary
                    label = f"{summary} ({date_str})"
                else:
                    label = f"{channel_name} ({date_str})"
                    
            except Exception:
                # Fallback to original format if date parsing fails
                label = f"{interaction.channel} - {interaction.date}"
            
            nodes.append({
                "id": interaction.id,
                "label": label,
                "type": "interaction",
                "properties": interaction.model_dump()
            })

        # --- Build edges from real relationships ---
        from backend.graph_service.connection import get_session_context
        import uuid
        edge_id = 1
        with get_session_context() as session:
            # WORKS_AT
            works_at = session.run("""
                MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
                RETURN p.id AS source, c.id AS target, r.role AS role, r.start_date AS start_date, r.end_date AS end_date
            """)
            for record in works_at:
                # Convert Neo4j record to handle datetime objects
                converted_record = _convert_neo4j_record(record)
                edges.append({
                    "id": f"e{edge_id}",
                    "source": converted_record["source"],
                    "target": converted_record["target"],
                    "type": "WORKS_AT",
                    "properties": {
                        "role": converted_record["role"], 
                        "start_date": converted_record["start_date"], 
                        "end_date": converted_record["end_date"]
                    }
                })
                edge_id += 1

            # INTERESTED_IN
            interested_in = session.run("""
                MATCH (p:Person)-[r:INTERESTED_IN]->(t:Topic)
                RETURN p.id AS source, t.id AS target
            """)
            for record in interested_in:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": record["source"],
                    "target": record["target"],
                    "type": "INTERESTED_IN",
                    "properties": {}
                })
                edge_id += 1

            # ATTENDED
            attended = session.run("""
                MATCH (p:Person)-[r:ATTENDED]->(e:Event)
                RETURN p.id AS source, e.id AS target
            """)
            for record in attended:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": record["source"],
                    "target": record["target"],
                    "type": "ATTENDED",
                    "properties": {}
                })
                edge_id += 1

            # KNOWS
            knows = session.run("""
                MATCH (p1:Person)-[r:KNOWS]->(p2:Person)
                RETURN p1.id AS source, p2.id AS target, r.strength AS strength, r.type AS rel_type
            """)
            for record in knows:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": record["source"],
                    "target": record["target"],
                    "type": "KNOWS",
                    "properties": {"strength": record["strength"], "type": record["rel_type"]}
                })
                edge_id += 1

            # PARTICIPATED_IN (Person -> Interaction)
            participated_in = session.run("""
                MATCH (p:Person)-[r:PARTICIPATED_IN]->(i:Interaction)
                RETURN p.id AS source, i.id AS target
            """)
            for record in participated_in:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": record["source"],
                    "target": record["target"],
                    "type": "PARTICIPATED_IN",
                    "properties": {}
                })
                edge_id += 1

            # LOCATED_AT (Event -> Location)
            located_at = session.run("""
                MATCH (e:Event)-[r:LOCATED_AT]->(l:Location)
                RETURN e.id AS source, l.id AS target
            """)
            for record in located_at:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": record["source"],
                    "target": record["target"],
                    "type": "LOCATED_AT",
                    "properties": {}
                })
                edge_id += 1

        graph_data = {
            "nodes": nodes,
            "edges": edges
        }

        return APIResponse(
            success=True,
            data=graph_data,
            message="Graph data retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=APIResponse)
async def get_graph_stats():
    """Get statistics about the graph."""
    try:
        people = list_people()
        companies = list_companies()
        topics = list_topics()
        events = list_events()
        locations = list_locations()
        interactions = list_interactions()

        # Calculate recent interactions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_interactions = 0
        
        for interaction in interactions:
            try:
                if isinstance(interaction.date, str):
                    interaction_date = datetime.fromisoformat(interaction.date.replace('Z', '+00:00'))
                else:
                    interaction_date = interaction.date
                
                if interaction_date >= thirty_days_ago:
                    recent_interactions += 1
            except Exception:
                # Skip interactions with invalid dates
                continue

        # Calculate people needing follow-up
        people_needing_followup = 0
        for person in people:
            if person.status == "needs_follow_up":
                people_needing_followup += 1

        # TODO: Get pending suggestions count from AI service
        pending_suggestions = 0

        stats = {
            "total_people": len(people),
            "total_companies": len(companies),
            "total_interactions": len(interactions),
            "recent_interactions": recent_interactions,
            "people_needing_followup": people_needing_followup,
            "pending_suggestions": pending_suggestions
        }

        return APIResponse(
            success=True,
            data=stats,
            message="Graph statistics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error getting graph stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 