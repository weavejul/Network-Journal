"""
Advanced Note Processor Service for Network Journal.

This service uses a multi-stage AI approach to intelligently process unstructured notes
and integrate them into the existing graph structure with proper disambiguation
and relationship validation.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from uuid import uuid4
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel as LangChainBaseModel

from shared.config import get_settings
from shared.utils import setup_logging
from shared.types import Person, Company, Topic, Event, Location, ContactStatus, DataSource, RelationshipType

# Import graph services
from backend.graph_service.people import create_person, link_person_to_company, create_person_relationship, get_person_by_name, search_people
from backend.graph_service.companies import create_company, get_company_by_name
from backend.graph_service.topics import create_topic, get_topic_by_name, link_person_to_topic
from backend.graph_service.events import create_event, get_event_by_name, link_person_to_event
from backend.graph_service.locations import create_location, get_location_by_city
from backend.graph_service.graph_queries import get_network_statistics

# Setup logging
logger = setup_logging(__name__)

# Get settings
settings = get_settings()


class EntityMention(LangChainBaseModel):
    """Schema for entities mentioned in notes."""
    
    name: str = Field(description="The name of the entity")
    entity_type: str = Field(description="Type: person, company, topic, event, location")
    confidence: float = Field(description="Confidence in identification (0.0 to 1.0)")
    context: str = Field(description="Context where this entity was mentioned")
    properties: Dict[str, Any] = Field(description="Additional properties", default_factory=dict)


class RelationshipMention(LangChainBaseModel):
    """Schema for relationships mentioned in notes."""
    
    from_entity: str = Field(description="Name of the source entity")
    to_entity: str = Field(description="Name of the target entity")
    relationship_type: str = Field(description="Type of relationship")
    strength: Optional[int] = Field(description="Relationship strength (1-5)", default=None)
    context: str = Field(description="Context where this relationship was mentioned")
    properties: Dict[str, Any] = Field(description="Additional properties", default_factory=dict)


class NoteAnalysis(LangChainBaseModel):
    """Schema for complete note analysis."""
    
    entities: List[EntityMention] = Field(description="All entities mentioned in the note")
    relationships: List[RelationshipMention] = Field(description="All relationships mentioned")
    main_person_context: Optional[str] = Field(description="Context about the main person (Alice)", default=None)
    ambiguous_entities: List[str] = Field(description="Entities that need disambiguation", default_factory=list)
    suggested_actions: List[str] = Field(description="Suggested actions to take", default_factory=list)
    confidence_score: float = Field(description="Overall confidence in the analysis", default=0.8)
    processing_notes: List[str] = Field(description="Processing notes and decisions", default_factory=list)


class DisambiguationResult(LangChainBaseModel):
    """Schema for disambiguation results."""
    
    entity_name: str = Field(description="The ambiguous entity name")
    candidates: List[Dict[str, Any]] = Field(description="Possible matches from existing data")
    suggested_action: str = Field(description="What to do: create_new, use_existing, ask_user")
    selected_candidate_id: Optional[str] = Field(description="ID of selected candidate if using existing", default=None)
    confidence: float = Field(description="Confidence in the decision", default=0.8)
    reasoning: str = Field(description="Reasoning for the decision")


class AdvancedNoteProcessorService:
    """Advanced service for processing unstructured notes with context awareness and disambiguation."""
    
    def __init__(self, main_person_name: str = "Alice"):
        """Initialize the advanced note processor service."""
        self.main_person_name = main_person_name
        self.main_person_id = None
        
        # Only initialize LLM if API key is available
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.DEFAULT_MODEL,
                temperature=settings.TEMPERATURE,
                api_key=settings.OPENAI_API_KEY
            )
            
            # Stage 1: Entity and Relationship Extraction
            self.extraction_prompt = ChatPromptTemplate.from_template("""
You are an expert data analyst specializing in network analysis. Your task is to extract entities and relationships from a personal note.

IMPORTANT CONTEXT:
- The main person in this network is "{main_person_name}"
- When someone says "I met X", it means {main_person_name} met X
- When someone says "X met Y", it means X and Y have a relationship
- Always consider the context and perspective of {main_person_name}

Think step-by-step:
1. Identify all people, companies, topics, events, and locations mentioned
2. Identify all relationships between entities
3. Determine if any entities are ambiguous (common names, partial names)
4. Consider the context and perspective of {main_person_name}
5. Suggest actions for handling ambiguous entities

CRITICAL: You must return a valid JSON object that matches this exact schema:
{{
  "entities": [
    {{
      "name": "entity name",
      "entity_type": "person|company|topic|event|location",
      "confidence": 0.0-1.0,
      "context": "context where mentioned",
      "properties": {{}}
    }}
  ],
  "relationships": [
    {{
      "from_entity": "source entity name",
      "to_entity": "target entity name", 
      "relationship_type": "KNOWS|WORKS_AT|INTERESTED_IN|ATTENDED|etc",
      "strength": 1-5,
      "context": "context where mentioned",
      "properties": {{}}
    }}
  ],
  "main_person_context": "context about main person",
  "ambiguous_entities": ["list of ambiguous entity names"],
  "suggested_actions": ["list of suggested actions"],
  "confidence_score": 0.0-1.0,
  "processing_notes": ["list of processing notes"]
}}

Here are examples:

Example 1:
Note: "I met John at the conference. He works at Google and is interested in AI."
Analysis:
- Entities: John (person), conference (event), Google (company), AI (topic)
- Relationships: {main_person_name} met John, John works at Google, John interested in AI
- Context: {main_person_name} is the one who met John

Example 2:
Note: "Sarah introduced me to Mike. They both work at Microsoft."
Analysis:
- Entities: Sarah (person), Mike (person), Microsoft (company)
- Relationships: Sarah introduced {main_person_name} to Mike, Sarah works at Microsoft, Mike works at Microsoft
- Context: Sarah and Mike are separate from {main_person_name}

Now analyze this note:
Note: "{note_text}"

Return ONLY the JSON object, no other text.
""")
            
            # Stage 2: Disambiguation Analysis
            self.disambiguation_prompt = ChatPromptTemplate.from_template("""
You are an expert at resolving ambiguous entity references in network data.

Given an ambiguous entity name and potential matches from the existing database, determine the best action to take.

Entity to disambiguate: "{entity_name}"
Entity type: "{entity_type}"
Context: "{context}"

Existing candidates:
{candidates_json}

Available actions:
1. "create_new" - Create a new entity (when no good match exists)
2. "use_existing" - Use an existing entity (when there's a clear match)
3. "ask_user" - Ask the user for clarification (when multiple good matches exist)

Consider:
- Name similarity (exact match, partial match, nickname)
- Context relevance (company, location, role)
- Confidence in the match
- Whether creating a duplicate would be problematic

CRITICAL: You must return a valid JSON object that matches this exact schema:
{{
  "entity_name": "the ambiguous entity name",
  "candidates": [],
  "suggested_action": "create_new|use_existing|ask_user",
  "selected_candidate_id": "id of selected candidate if using existing",
  "confidence": 0.0-1.0,
  "reasoning": "explanation of your decision"
}}

Return ONLY the JSON object, no other text.
""")
            
            # Create output parsers
            self.extraction_parser = JsonOutputParser(pydantic_object=NoteAnalysis)
            self.disambiguation_parser = JsonOutputParser(pydantic_object=DisambiguationResult)
            
            # Create chains
            self.extraction_chain = self.extraction_prompt | self.llm | self.extraction_parser
            self.disambiguation_chain = self.disambiguation_prompt | self.llm | self.disambiguation_parser
            
        else:
            self.llm = None
            self.extraction_chain = None
            self.disambiguation_chain = None
    
    async def process_note_advanced(self, note_text: str) -> Dict[str, Any]:
        """
        Advanced note processing with context awareness and disambiguation.
        
        Args:
            note_text: The unstructured note text
            
        Returns:
            Dictionary containing processed entities and relationships
        """
        try:
            logger.info(f"Processing note with advanced system: {note_text[:100]}...")
            
            # Check if LLM is initialized
            if not self.extraction_chain:
                raise Exception("AI service is not configured. Please set OPENAI_API_KEY environment variable.")
            
            # Ensure main person exists and is set up
            await self._ensure_main_person_exists()
            
            # Stage 1: Extract entities and relationships
            raw_analysis = await self.extraction_chain.ainvoke({
                "main_person_name": self.main_person_name,
                "note_text": note_text
            })
            
            # Handle both dictionary and Pydantic model responses
            if isinstance(raw_analysis, dict):
                logger.info("Received dictionary response from LLM, converting to NoteAnalysis")
                try:
                    analysis = NoteAnalysis(**raw_analysis)
                except Exception as e:
                    logger.warning(f"Failed to parse LLM response as NoteAnalysis: {e}")
                    # Create a fallback analysis with basic extraction
                    analysis = self._create_fallback_analysis(note_text, raw_analysis)
            else:
                analysis = raw_analysis
            
            logger.info(f"Stage 1 analysis complete: {len(analysis.entities)} entities, {len(analysis.relationships)} relationships")
            logger.info(f"Entities found: {[e.name for e in analysis.entities]}")
            logger.info(f"Relationships found: {[(r.from_entity, r.relationship_type, r.to_entity) for r in analysis.relationships]}")
            
            # Stage 2: Resolve ambiguous entities
            resolved_entities = await self._resolve_ambiguous_entities(analysis.entities, note_text)
            logger.info(f"Resolved entities: {resolved_entities}")
            
            # Stage 3: Validate and create relationships
            validated_relationships = await self._validate_relationships(analysis.relationships, resolved_entities)
            logger.info(f"Validated relationships: {validated_relationships}")
            
            # Stage 4: Create graph entities
            created_entities = await self._create_graph_entities(resolved_entities, validated_relationships)
            
            result = {
                "analysis": analysis.dict(),
                "resolved_entities": resolved_entities,
                "validated_relationships": validated_relationships,
                "created_entities": created_entities,
                "main_person_id": self.main_person_id
            }
            
            logger.info(f"Advanced processing complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced note processing: {e}")
            # Add more detailed error information
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def _ensure_main_person_exists(self):
        """Ensure the main person exists in the graph and set up the ID."""
        if not self.main_person_id:
            # First try exact name match
            existing_person = get_person_by_name(self.main_person_name)
            if existing_person:
                self.main_person_id = existing_person.id
                logger.info(f"Found existing main person: {self.main_person_name} (ID: {self.main_person_id})")
                return
            
            # Try case-insensitive search for similar names
            similar_people = search_people(self.main_person_name)
            if similar_people:
                # Use the first match (most likely to be the main person)
                self.main_person_id = similar_people[0].id
                logger.info(f"Found main person via search: {similar_people[0].name} (ID: {self.main_person_id})")
                # Update the main person name to match what's in the database
                self.main_person_name = similar_people[0].name
                return
            
            # Create the main person if they don't exist
            main_person = Person(
                name=self.main_person_name,
                email=None,
                phone=None,
                linkedin_url=None,
                source_of_contact="System",
                status=ContactStatus.ACTIVE,
                notes="Main person in the network",
                data_source=DataSource.MANUAL_ENTRY
            )
            created_person = create_person(main_person)
            self.main_person_id = created_person.id
            logger.info(f"Created main person: {self.main_person_name} (ID: {self.main_person_id})")
    
    async def _resolve_ambiguous_entities(self, entities: List[EntityMention], note_text: str) -> Dict[str, Any]:
        """Resolve ambiguous entities by checking existing data and using AI disambiguation."""
        resolved = {}
        
        # Always include the main person in resolved entities
        resolved[self.main_person_name] = {
            "action": "use_existing",
            "entity": EntityMention(
                name=self.main_person_name,
                entity_type="person",
                confidence=1.0,
                context="Main person in the network",
                properties={}
            ),
            "existing_id": self.main_person_id,
            "confidence": 1.0
        }
        
        for entity in entities:
            if entity.entity_type == "person":
                resolution = await self._resolve_person_entity(entity, note_text)
            elif entity.entity_type == "company":
                resolution = await self._resolve_company_entity(entity, note_text)
            elif entity.entity_type == "topic":
                resolution = await self._resolve_topic_entity(entity, note_text)
            elif entity.entity_type == "event":
                resolution = await self._resolve_event_entity(entity, note_text)
            elif entity.entity_type == "location":
                resolution = await self._resolve_location_entity(entity, note_text)
            else:
                resolution = {"action": "create_new", "entity": entity, "existing_id": None}
            
            resolved[entity.name] = resolution
        
        return resolved
    
    async def _resolve_person_entity(self, entity: EntityMention, note_text: str) -> Dict[str, Any]:
        """Resolve a person entity with sophisticated disambiguation."""
        
        # Skip if this is the main person (already handled)
        if entity.name.lower() == self.main_person_name.lower():
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": self.main_person_id,
                "confidence": 1.0
            }
        
        # First, try exact name match
        existing_person = get_person_by_name(entity.name)
        if existing_person:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": existing_person.id,
                "confidence": 1.0
            }
        
        # Search for similar names
        similar_people = search_people(entity.name)
        
        if not similar_people:
            return {
                "action": "create_new",
                "entity": entity,
                "existing_id": None,
                "confidence": 0.9
            }
        
        # Use AI to disambiguate if multiple candidates
        if len(similar_people) == 1:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": similar_people[0].id,
                "confidence": 0.8
            }
        
        # Multiple candidates - use AI disambiguation
        candidates_json = json.dumps([
            {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "company": getattr(p, 'company', None),
                "role": getattr(p, 'role', None)
            }
            for p in similar_people
        ])
        
        raw_disambiguation = await self.disambiguation_chain.ainvoke({
            "entity_name": entity.name,
            "entity_type": "person",
            "context": note_text,
            "candidates_json": candidates_json
        })
        
        # Handle both dictionary and Pydantic model responses
        if isinstance(raw_disambiguation, dict):
            logger.info("Received dictionary response from disambiguation LLM, converting to DisambiguationResult")
            try:
                disambiguation = DisambiguationResult(**raw_disambiguation)
            except Exception as e:
                logger.warning(f"Failed to parse disambiguation response: {e}")
                # Create a fallback disambiguation
                disambiguation = self._create_fallback_disambiguation(entity.name, similar_people)
        else:
            disambiguation = raw_disambiguation
        
        return {
            "action": disambiguation.suggested_action,
            "entity": entity,
            "existing_id": disambiguation.selected_candidate_id,
            "confidence": disambiguation.confidence,
            "reasoning": disambiguation.reasoning
        }
    
    async def _resolve_company_entity(self, entity: EntityMention, note_text: str) -> Dict[str, Any]:
        """Resolve a company entity."""
        existing_company = get_company_by_name(entity.name)
        if existing_company:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": existing_company.id,
                "confidence": 1.0
            }
        
        return {
            "action": "create_new",
            "entity": entity,
            "existing_id": None,
            "confidence": 0.9
        }
    
    async def _resolve_topic_entity(self, entity: EntityMention, note_text: str) -> Dict[str, Any]:
        """Resolve a topic entity."""
        existing_topic = get_topic_by_name(entity.name)
        if existing_topic:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": existing_topic.id,
                "confidence": 1.0
            }
        
        return {
            "action": "create_new",
            "entity": entity,
            "existing_id": None,
            "confidence": 0.9
        }
    
    async def _resolve_event_entity(self, entity: EntityMention, note_text: str) -> Dict[str, Any]:
        """Resolve an event entity."""
        existing_event = get_event_by_name(entity.name)
        if existing_event:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": existing_event.id,
                "confidence": 1.0
            }
        
        return {
            "action": "create_new",
            "entity": entity,
            "existing_id": None,
            "confidence": 0.9
        }
    
    async def _resolve_location_entity(self, entity: EntityMention, note_text: str) -> Dict[str, Any]:
        """Resolve a location entity."""
        existing_location = get_location_by_city(entity.name)
        if existing_location:
            return {
                "action": "use_existing",
                "entity": entity,
                "existing_id": existing_location.id,
                "confidence": 1.0
            }
        
        return {
            "action": "create_new",
            "entity": entity,
            "existing_id": None,
            "confidence": 0.9
        }
    
    async def _validate_relationships(self, relationships: List[RelationshipMention], resolved_entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate relationships and ensure they connect to existing entities."""
        validated = []
        
        # First, ensure all entities exist (create any that are marked as "create_new")
        for entity_name, entity_resolution in resolved_entities.items():
            if entity_resolution["action"] == "create_new" and not entity_resolution.get("existing_id"):
                await self._ensure_entity_exists(entity_resolution, resolved_entities)
        
        for rel in relationships:
            # Get resolved entities
            from_entity = resolved_entities.get(rel.from_entity)
            to_entity = resolved_entities.get(rel.to_entity)
            
            if not from_entity or not to_entity:
                logger.warning(f"Skipping relationship {rel.from_entity} -> {rel.to_entity}: entities not resolved")
                continue
            
            # Get entity IDs, ensuring they exist
            from_id = await self._ensure_entity_exists(from_entity, resolved_entities)
            to_id = await self._ensure_entity_exists(to_entity, resolved_entities)
            
            if not from_id or not to_id:
                logger.warning(f"Cannot create relationship: missing IDs for {rel.from_entity} -> {rel.to_entity}")
                continue
            
            validated.append({
                "from_entity": rel.from_entity,
                "to_entity": rel.to_entity,
                "from_id": from_id,
                "to_id": to_id,
                "relationship_type": rel.relationship_type,
                "strength": rel.strength,
                "properties": rel.properties,
                "context": rel.context
            })
        
        return validated
    
    async def _ensure_entity_exists(self, entity_resolution: Dict[str, Any], resolved_entities: Dict[str, Any]) -> Optional[str]:
        """Ensure an entity exists and return its ID. Create if necessary."""
        entity = entity_resolution["entity"]
        action = entity_resolution["action"]
        existing_id = entity_resolution.get("existing_id")
        
        if action == "use_existing":
            if existing_id:
                # Verify the entity actually exists
                if entity.entity_type == "person":
                    actual_entity = get_person_by_name(entity.name)
                elif entity.entity_type == "company":
                    actual_entity = get_company_by_name(entity.name)
                elif entity.entity_type == "topic":
                    actual_entity = get_topic_by_name(entity.name)
                elif entity.entity_type == "event":
                    actual_entity = get_event_by_name(entity.name)
                elif entity.entity_type == "location":
                    actual_entity = get_location_by_city(entity.name)
                else:
                    actual_entity = None
                
                if actual_entity:
                    return actual_entity.id
                else:
                    logger.warning(f"Entity marked as 'use_existing' but not found: {entity.name}")
                    # Fall back to creating the entity
                    return await self._create_entity_and_update_resolution(entity, entity_resolution, resolved_entities)
            else:
                logger.warning(f"Entity marked as 'use_existing' but no ID provided: {entity.name}")
                # Fall back to creating the entity
                return await self._create_entity_and_update_resolution(entity, entity_resolution, resolved_entities)
        
        elif action == "create_new":
            if existing_id:
                return existing_id
            else:
                return await self._create_entity_and_update_resolution(entity, entity_resolution, resolved_entities)
        
        return None
    
    async def _create_entity_and_update_resolution(self, entity: EntityMention, entity_resolution: Dict[str, Any], resolved_entities: Dict[str, Any]) -> Optional[str]:
        """Create an entity and update its resolution with the new ID."""
        try:
            if entity.entity_type == "person":
                person = Person(
                    name=entity.name,
                    email=None,
                    phone=None,
                    linkedin_url=None,
                    source_of_contact="AI Note Processing",
                    status=ContactStatus.ACTIVE,
                    notes=f"Created from note: {entity.context}",
                    data_source=DataSource.AGENT_SUGGESTION
                )
                created_entity = create_person(person)
            elif entity.entity_type == "company":
                company = Company(
                    name=entity.name,
                    industry=None,
                    website=None
                )
                created_entity = create_company(company)
            elif entity.entity_type == "topic":
                topic = Topic(name=entity.name)
                created_entity = create_topic(topic)
            elif entity.entity_type == "event":
                event = Event(
                    name=entity.name,
                    date=datetime.now(UTC).isoformat(),
                    type="meeting"
                )
                created_entity = create_event(event)
            elif entity.entity_type == "location":
                location = Location(
                    city=entity.name,
                    state=None,
                    country=None
                )
                created_entity = create_location(location)
            else:
                logger.warning(f"Unknown entity type: {entity.entity_type}")
                return None
            
            # Update the resolution with the new ID
            entity_resolution["existing_id"] = created_entity.id
            entity_resolution["action"] = "created"
            
            logger.info(f"Created missing entity: {entity.name} ({entity.entity_type}) with ID: {created_entity.id}")
            return created_entity.id
            
        except Exception as e:
            logger.error(f"Error creating entity {entity.name}: {e}")
            return None
    
    async def _create_graph_entities(self, resolved_entities: Dict[str, Any], validated_relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create graph entities and relationships."""
        created_entities = {
            "people": [],
            "companies": [],
            "topics": [],
            "events": [],
            "locations": [],
            "relationships": []
        }
        
        # Log all entities (created or existing)
        for entity_name, resolution in resolved_entities.items():
            entity = resolution["entity"]
            entity_id = resolution["existing_id"]
            action = resolution["action"]
            
            if entity.entity_type == "person":
                created_entities["people"].append({
                    "name": entity.name,
                    "id": entity_id,
                    "action": action
                })
            elif entity.entity_type == "company":
                created_entities["companies"].append({
                    "name": entity.name,
                    "id": entity_id,
                    "action": action
                })
            elif entity.entity_type == "topic":
                created_entities["topics"].append({
                    "name": entity.name,
                    "id": entity_id,
                    "action": action
                })
            elif entity.entity_type == "event":
                created_entities["events"].append({
                    "name": entity.name,
                    "id": entity_id,
                    "action": action
                })
            elif entity.entity_type == "location":
                created_entities["locations"].append({
                    "name": entity.name,
                    "id": entity_id,
                    "action": action
                })
        
        # Create relationships
        for rel in validated_relationships:
            try:
                from_id = rel["from_id"]
                to_id = rel["to_id"]
                
                # Handle different relationship types
                if rel["relationship_type"] == "WORKS_AT":
                    # Link person to company
                    link_person_to_company(
                        from_id,
                        to_id,
                        rel.get("properties", {}).get("role", "Unknown"),
                        datetime.now(UTC)
                    )
                    logger.info(f"Created WORKS_AT relationship: {rel['from_entity']} -> {rel['to_entity']}")
                    
                elif rel["relationship_type"] == "KNOWS":
                    # Create person-to-person relationship
                    create_person_relationship(
                        from_id,
                        to_id,
                        rel.get("strength", 3),
                        rel.get("properties", {}).get("type", "acquaintance")
                    )
                    logger.info(f"Created KNOWS relationship: {rel['from_entity']} -> {rel['to_entity']}")
                    
                elif rel["relationship_type"] == "INTERESTED_IN":
                    # Link person to topic
                    link_person_to_topic(from_id, to_id)
                    logger.info(f"Created INTERESTED_IN relationship: {rel['from_entity']} -> {rel['to_entity']}")
                    
                elif rel["relationship_type"] == "ATTENDED":
                    # Link person to event
                    link_person_to_event(from_id, to_id)
                    logger.info(f"Created ATTENDED relationship: {rel['from_entity']} -> {rel['to_entity']}")
                
                created_entities["relationships"].append({
                    "from": rel["from_entity"],
                    "to": rel["to_entity"],
                    "type": rel["relationship_type"],
                    "action": "created"
                })
                
            except Exception as e:
                logger.error(f"Error creating relationship {rel['from_entity']} -> {rel['to_entity']}: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return created_entities
    
    def set_main_person(self, person_name: str, person_id: Optional[str] = None):
        """Set the main person for context awareness."""
        self.main_person_name = person_name
        self.main_person_id = person_id
    
    def get_main_person_id(self) -> Optional[str]:
        """Get the main person ID."""
        return self.main_person_id


# Global instance
advanced_note_processor = AdvancedNoteProcessorService() 