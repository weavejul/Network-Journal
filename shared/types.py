"""
Shared data models for the Network Journal application.
These models define the core entities and relationships in the graph database.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships between people."""
    COLLEAGUE = "colleague"
    FRIEND = "friend"
    FAMILY = "family"
    ACQUAINTANCE = "acquaintance"
    MENTOR = "mentor"
    MENTEE = "mentee"


class InteractionChannel(str, Enum):
    """Channels through which interactions occur."""
    EMAIL = "email"
    CALL = "call"
    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"
    TEXT = "text"
    SOCIAL_MEDIA = "social_media"


class EventType(str, Enum):
    """Types of events."""
    CONFERENCE = "conference"
    MEETUP = "meetup"
    PARTY = "party"
    MEETING = "meeting"
    LUNCH = "lunch"
    DINNER = "dinner"


class ContactStatus(str, Enum):
    """Status of a contact."""
    ACTIVE = "active"
    NEEDS_FOLLOW_UP = "needs_follow_up"
    INACTIVE = "inactive"


class DataSource(str, Enum):
    """Source of data in the system."""
    USER_NOTE = "user_note"
    AGENT_SUGGESTION = "agent_suggestion"
    MANUAL_ENTRY = "manual_entry"


# Base Models
class Person(BaseModel):
    """A person in the network."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    last_contacted_date: Optional[datetime] = None
    birthday: Optional[datetime] = None
    source_of_contact: Optional[str] = None
    status: ContactStatus = ContactStatus.ACTIVE
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    data_source: DataSource = DataSource.MANUAL_ENTRY


class Company(BaseModel):
    """A company where people work."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Topic(BaseModel):
    """An interest, skill, or concept."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    created_at: Optional[datetime] = None


class Location(BaseModel):
    """A geographical location."""
    id: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None


class Event(BaseModel):
    """A specific gathering or event."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    date: datetime
    type: EventType
    location_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Interaction(BaseModel):
    """A specific communication or meeting event."""
    id: Optional[str] = None
    date: datetime
    channel: InteractionChannel
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    data_source: DataSource = DataSource.MANUAL_ENTRY


# Relationship Models
class PersonRelationship(BaseModel):
    """Relationship between two people."""
    from_person_id: str
    to_person_id: str
    strength: int = Field(..., ge=1, le=5)  # 1-5 scale
    type: RelationshipType
    created_at: Optional[datetime] = None


class EmploymentRelationship(BaseModel):
    """Employment relationship between a person and company."""
    person_id: str
    company_id: str
    role: str = Field(..., min_length=1, max_length=200)
    start_date: datetime
    end_date: Optional[datetime] = None  # None if current
    created_at: Optional[datetime] = None


# Graph Query Models
class GraphNode(BaseModel):
    """A node in the graph visualization."""
    id: str
    label: str
    type: str  # 'person', 'company', 'topic', etc.
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    """An edge in the graph visualization."""
    id: str
    source: str
    target: str
    type: str  # relationship type
    properties: Dict[str, Any]


class GraphData(BaseModel):
    """Complete graph data for visualization."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# AI Processing Models
class NoteProcessingRequest(BaseModel):
    """Request to process unstructured notes."""
    note_text: str = Field(..., min_length=1)
    person_id: Optional[str] = None  # If processing for existing person


class NoteProcessingResult(BaseModel):
    """Result of note processing by AI."""
    person_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    topics_of_interest: List[str] = []
    events_mentioned: List[str] = []
    location: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)


class AgentSuggestion(BaseModel):
    """Suggestion from the autonomous agent."""
    id: Optional[str] = None
    person_id: str
    suggestion_type: str  # 'new_job', 'new_company', 'new_topic', etc.
    suggested_data: Dict[str, Any]
    source_url: Optional[HttpUrl] = None
    source_description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: str = "pending_review"  # 'pending_review', 'accepted', 'rejected'
    created_at: Optional[datetime] = None


# API Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated API response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class InteractionUpdate(BaseModel):
    date: Optional[datetime] = None
    channel: Optional[InteractionChannel] = None
    summary: Optional[str] = None
    data_source: Optional[DataSource] = None
    # id, created_at are not updatable 