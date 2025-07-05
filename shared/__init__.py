"""
Shared package for the Network Journal application.
"""

from .types import (
    Person, Company, Topic, Location, Event, Interaction,
    PersonRelationship, EmploymentRelationship,
    GraphNode, GraphEdge, GraphData,
    NoteProcessingRequest, NoteProcessingResult, AgentSuggestion,
    APIResponse, PaginatedResponse,
    RelationshipType, InteractionChannel, EventType, ContactStatus, DataSource
)

from .utils import (
    generate_id, get_current_timestamp, setup_logging,
    safe_get, validate_email, sanitize_string,
    get_project_root, format_date_for_display, format_datetime_for_display,
    calculate_age, days_since_last_contact, normalize_company_name,
    extract_domain_from_url, chunk_list, merge_dicts
)

from .config import (
    Settings, get_settings, is_development, is_production,
    get_database_url, get_ai_provider_config
)

__all__ = [
    # Types
    "Person", "Company", "Topic", "Location", "Event", "Interaction",
    "PersonRelationship", "EmploymentRelationship",
    "GraphNode", "GraphEdge", "GraphData",
    "NoteProcessingRequest", "NoteProcessingResult", "AgentSuggestion",
    "APIResponse", "PaginatedResponse",
    "RelationshipType", "InteractionChannel", "EventType", "ContactStatus", "DataSource",
    
    # Utils
    "generate_id", "get_current_timestamp", "setup_logging",
    "safe_get", "validate_email", "sanitize_string",
    "get_project_root", "format_date_for_display", "format_datetime_for_display",
    "calculate_age", "days_since_last_contact", "normalize_company_name",
    "extract_domain_from_url", "chunk_list", "merge_dicts",
    
    # Config
    "Settings", "get_settings", "is_development", "is_production",
    "get_database_url", "get_ai_provider_config"
] 