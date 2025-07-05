"""
Advanced graph queries for network analysis and visualization.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import Session
from shared.types import GraphNode, GraphEdge, GraphData
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


def get_full_network_graph() -> GraphData:
    """Get the complete network graph for visualization."""
    cypher_query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN DISTINCT n, labels(n) as labels, type(r) as relationship_type, m, labels(m) as target_labels
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        
        nodes = {}
        edges = []
        
        for record in result:
            # Process source node
            source_node = record["n"]
            if source_node:
                source_id = source_node["id"]
                if source_id not in nodes:
                    node_labels = record["labels"]
                    node_type = node_labels[0].lower() if node_labels else "unknown"
                    nodes[source_id] = GraphNode(
                        id=source_id,
                        label=source_node.get("name", source_node.get("id", "Unknown")),
                        type=node_type,
                        properties=_convert_neo4j_record(source_node)
                    )
            
            # Process target node and relationship
            target_node = record["m"]
            relationship_type = record["relationship_type"]
            
            if target_node and relationship_type:
                target_id = target_node["id"]
                if target_id not in nodes:
                    target_labels = record["target_labels"]
                    target_node_type = target_labels[0].lower() if target_labels else "unknown"
                    nodes[target_id] = GraphNode(
                        id=target_id,
                        label=target_node.get("name", target_node.get("id", "Unknown")),
                        type=target_node_type,
                        properties=_convert_neo4j_record(target_node)
                    )
                
                # Create edge
                edge_id = f"{source_id}-{relationship_type}-{target_id}"
                edges.append(GraphEdge(
                    id=edge_id,
                    source=source_id,
                    target=target_id,
                    type=relationship_type,
                    properties={}
                ))
        
        return GraphData(
            nodes=list(nodes.values()),
            edges=edges
        )


def get_person_network_graph(person_id: str, depth: int = 2) -> GraphData:
    """Get a person's network graph up to a certain depth."""
    cypher_query = """
    MATCH path = (p:Person {id: $person_id})-[*1..$depth]-(connected)
    RETURN DISTINCT connected, labels(connected) as labels, length(path) as distance
    ORDER BY distance, connected.name
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, depth=depth)
        
        nodes = {}
        edges = []
        
        # Add the central person
        central_person = get_person_details(person_id)
        if central_person:
            nodes[person_id] = GraphNode(
                id=person_id,
                label=central_person.get("name", "Unknown"),
                type="person",
                properties=central_person
            )
        
        for record in result:
            node = record["connected"]
            node_id = node["id"]
            node_labels = record["labels"]
            node_type = node_labels[0].lower() if node_labels else "unknown"
            
            if node_id not in nodes:
                nodes[node_id] = GraphNode(
                    id=node_id,
                    label=node.get("name", node.get("id", "Unknown")),
                    type=node_type,
                    properties=_convert_neo4j_record(node)
                )
        
        # Get relationships between nodes
        relationship_query = """
        MATCH (n)-[r]-(m)
        WHERE n.id IN $node_ids AND m.id IN $node_ids
        RETURN n.id as source, type(r) as type, m.id as target
        """
        
        node_ids = list(nodes.keys())
        if node_ids:
            rel_result = session.run(relationship_query, node_ids=node_ids)
            for rel_record in rel_result:
                edge_id = f"{rel_record['source']}-{rel_record['type']}-{rel_record['target']}"
                edges.append(GraphEdge(
                    id=edge_id,
                    source=rel_record["source"],
                    target=rel_record["target"],
                    type=rel_record["type"],
                    properties={}
                ))
        
        return GraphData(
            nodes=list(nodes.values()),
            edges=edges
        )


def get_person_details(person_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a person including relationships."""
    cypher_query = """
    MATCH (p:Person {id: $person_id})
    OPTIONAL MATCH (p)-[r:WORKS_AT]->(c:Company)
    OPTIONAL MATCH (p)-[:LIVES_IN]->(l:Location)
    OPTIONAL MATCH (p)-[:INTERESTED_IN]->(t:Topic)
    RETURN p, collect(DISTINCT c) as companies, collect(DISTINCT l) as locations, collect(DISTINCT t) as topics
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id)
        record = result.single()
        
        if record:
            person_data = _convert_neo4j_record(record["p"])
            person_data["companies"] = [_convert_neo4j_record(c) for c in record["companies"] if c]
            person_data["locations"] = [_convert_neo4j_record(l) for l in record["locations"] if l]
            person_data["topics"] = [_convert_neo4j_record(t) for t in record["topics"] if t]
            return person_data
        return None


def get_network_statistics() -> Dict[str, Any]:
    """Get overall network statistics."""
    cypher_query = """
    MATCH (n)
    RETURN labels(n) as labels, count(n) as count
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query)
        
        stats = {
            "total_nodes": 0,
            "node_types": {},
            "total_relationships": 0,
            "relationship_types": {}
        }
        
        for record in result:
            labels = record["labels"]
            count = record["count"]
            node_type = labels[0].lower() if labels else "unknown"
            
            stats["total_nodes"] += count
            stats["node_types"][node_type] = count
        
        # Get relationship statistics
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(r) as count
        """
        
        rel_result = session.run(rel_query)
        for record in rel_result:
            rel_type = record["type"]
            count = record["count"]
            
            stats["total_relationships"] += count
            stats["relationship_types"][rel_type] = count
        
        return stats


def get_network_insights() -> Dict[str, Any]:
    """Get insights about the network."""
    insights = {}
    
    # Most connected people
    with get_session_context() as session:
        # People with most connections
        connected_query = """
        MATCH (p:Person)-[r]-(other)
        RETURN p, count(r) as connection_count
        ORDER BY connection_count DESC
        LIMIT 10
        """
        
        result = session.run(connected_query)
        most_connected = []
        for record in result:
            person_data = _convert_neo4j_record(record["p"])
            most_connected.append({
                "person": person_data,
                "connection_count": record["connection_count"]
            })
        insights["most_connected_people"] = most_connected
        
        # Companies with most employees
        company_query = """
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.end_date IS NULL
        RETURN c, count(p) as employee_count
        ORDER BY employee_count DESC
        LIMIT 10
        """
        
        result = session.run(company_query)
        top_companies = []
        for record in result:
            company_data = _convert_neo4j_record(record["c"])
            top_companies.append({
                "company": company_data,
                "employee_count": record["employee_count"]
            })
        insights["top_companies"] = top_companies
        
        # Most popular topics
        topic_query = """
        MATCH (p:Person)-[:INTERESTED_IN]->(t:Topic)
        RETURN t, count(p) as interest_count
        ORDER BY interest_count DESC
        LIMIT 10
        """
        
        result = session.run(topic_query)
        popular_topics = []
        for record in result:
            topic_data = _convert_neo4j_record(record["t"])
            popular_topics.append({
                "topic": topic_data,
                "interest_count": record["interest_count"]
            })
        insights["popular_topics"] = popular_topics
        
        # Recent activity
        recent_query = """
        MATCH (i:Interaction)
        WHERE i.date >= datetime() - duration({days: 30})
        RETURN count(i) as recent_interactions
        """
        
        result = session.run(recent_query)
        record = result.single()
        insights["recent_interactions"] = record["recent_interactions"] if record else 0
    
    return insights


def search_network(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search across the entire network."""
    cypher_query = """
    MATCH (n)
    WHERE n.name CONTAINS $query OR n.email CONTAINS $query OR n.industry CONTAINS $query
    RETURN n, labels(n) as labels
    ORDER BY n.name
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, query=query, limit=limit)
        
        results = {
            "people": [],
            "companies": [],
            "topics": [],
            "locations": [],
            "events": []
        }
        
        for record in result:
            node = record["n"]
            labels = record["labels"]
            node_type = labels[0].lower() if labels else "unknown"
            
            node_data = _convert_neo4j_record(node)
            
            if node_type == "person":
                results["people"].append(node_data)
            elif node_type == "company":
                results["companies"].append(node_data)
            elif node_type == "topic":
                results["topics"].append(node_data)
            elif node_type == "location":
                results["locations"].append(node_data)
            elif node_type == "event":
                results["events"].append(node_data)
        
        return results


def get_network_paths(from_person_id: str, to_person_id: str, max_length: int = 3) -> List[Dict[str, Any]]:
    """Find paths between two people in the network."""
    cypher_query = """
    MATCH path = (p1:Person {id: $from_person_id})-[*1..$max_length]-(p2:Person {id: $to_person_id})
    RETURN path, length(path) as path_length
    ORDER BY path_length
    LIMIT 10
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, from_person_id=from_person_id, to_person_id=to_person_id, max_length=max_length)
        
        paths = []
        for record in result:
            path = record["path"]
            path_length = record["path_length"]
            
            path_nodes = []
            path_relationships = []
            
            for i, node in enumerate(path.nodes):
                node_data = _convert_neo4j_record(node)
                path_nodes.append({
                    "id": node["id"],
                    "type": list(node.labels)[0].lower(),
                    "data": node_data
                })
                
                if i < len(path.relationships):
                    rel = path.relationships[i]
                    path_relationships.append({
                        "type": rel.type,
                        "source": rel.start_node["id"],
                        "target": rel.end_node["id"]
                    })
            
            paths.append({
                "length": path_length,
                "nodes": path_nodes,
                "relationships": path_relationships
            })
        
        return paths


def get_network_clusters() -> List[Dict[str, Any]]:
    """Identify clusters or communities in the network."""
    # This is a simplified community detection using connected components
    cypher_query = """
    CALL gds.wcc.stream('person-graph')
    YIELD nodeId, componentId
    RETURN componentId, collect(nodeId) as nodes
    ORDER BY size(collect(nodeId)) DESC
    """
    
    # For now, return a simplified version using connected components
    simple_query = """
    MATCH (p:Person)
    WITH p
    OPTIONAL MATCH (p)-[:KNOWS*]-(connected:Person)
    RETURN p, collect(DISTINCT connected) as connected_group
    """
    
    with get_session_context() as session:
        result = session.run(simple_query)
        
        clusters = []
        processed = set()
        
        for record in result:
            person = record["p"]
            connected_group = record["connected_group"]
            
            if person["id"] not in processed:
                cluster_nodes = [person] + [p for p in connected_group if p]
                cluster_ids = [n["id"] for n in cluster_nodes]
                
                # Mark all nodes in this cluster as processed
                processed.update(cluster_ids)
                
                clusters.append({
                    "id": f"cluster_{len(clusters)}",
                    "size": len(cluster_nodes),
                    "nodes": [_convert_neo4j_record(n) for n in cluster_nodes]
                })
        
        return clusters


def get_network_recommendations(person_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get network recommendations for a person."""
    # Find people who are connected to people this person knows but not directly connected
    cypher_query = """
    MATCH (p:Person {id: $person_id})-[:KNOWS]->(friend:Person)-[:KNOWS]->(recommended:Person)
    WHERE recommended.id <> $person_id
    AND NOT (p)-[:KNOWS]->(recommended)
    RETURN recommended, count(friend) as mutual_connections
    ORDER BY mutual_connections DESC
    LIMIT $limit
    """
    
    with get_session_context() as session:
        result = session.run(cypher_query, person_id=person_id, limit=limit)
        
        recommendations = []
        for record in result:
            person_data = _convert_neo4j_record(record["recommended"])
            recommendations.append({
                "person": person_data,
                "mutual_connections": record["mutual_connections"],
                "reason": f"Connected through {record['mutual_connections']} mutual friends"
            })
        
        return recommendations 