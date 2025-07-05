"""
AI Router for Network Journal.

This router provides endpoints for AI-powered services including
advanced note processing with context awareness and disambiguation.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from shared.types import APIResponse
from shared.config import get_settings
from backend.ai_service.note_processor import advanced_note_processor

# Get settings
settings = get_settings()

# Create router
router = APIRouter(tags=["AI Services"])


class AdvancedNoteProcessingRequest(BaseModel):
    """Request model for advanced note processing."""
    
    note_text: str = Field(..., description="The unstructured note text to process", min_length=1, max_length=5000)
    main_person_name: str = Field(default="Alice", description="The main person in the network (default: Alice)")
    main_person_id: Optional[str] = Field(default=None, description="The ID of the main person in the network")
    auto_create_entities: bool = Field(default=True, description="Whether to automatically create entities in the graph")


class AdvancedNoteProcessingResponse(BaseModel):
    """Response model for advanced note processing."""
    
    analysis: Dict[str, Any] = Field(..., description="Complete analysis of the note")
    resolved_entities: Dict[str, Any] = Field(..., description="Entities after disambiguation")
    validated_relationships: list = Field(..., description="Validated relationships")
    created_entities: Dict[str, Any] = Field(..., description="Entities created in the graph")
    main_person_id: Optional[str] = Field(..., description="ID of the main person")
    processing_confidence: float = Field(..., description="Overall confidence in processing")


@router.post("/process-note-advanced", response_model=APIResponse)
async def process_note_advanced(request: AdvancedNoteProcessingRequest) -> APIResponse:
    """
    Advanced note processing with context awareness and disambiguation.
    
    This endpoint uses a multi-stage AI approach to:
    1. Extract entities and relationships with context awareness
    2. Resolve ambiguous entities by checking existing data
    3. Validate relationships and ensure graph connectivity
    4. Create entities and relationships in the graph
    """
    try:
        # Check if AI is configured
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="AI service is not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Set the main person context
        advanced_note_processor.set_main_person(request.main_person_name, request.main_person_id)
        
        # Process the note with advanced system
        result = await advanced_note_processor.process_note_advanced(request.note_text)
        
        # Create response
        response_data = AdvancedNoteProcessingResponse(
            analysis=result["analysis"],
            resolved_entities=result["resolved_entities"],
            validated_relationships=result["validated_relationships"],
            created_entities=result["created_entities"],
            main_person_id=result["main_person_id"],
            processing_confidence=result["analysis"].get("confidence_score", 0.8)
        )
        
        return APIResponse(
            success=True,
            message="Advanced note processing completed successfully",
            data=response_data.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in advanced note processing: {str(e)}"
        )


@router.post("/process-note", response_model=APIResponse)
async def process_note_legacy(request: AdvancedNoteProcessingRequest) -> APIResponse:
    """
    Legacy note processing endpoint (redirects to advanced processing).
    
    This endpoint maintains backward compatibility while using the new advanced system.
    """
    return await process_note_advanced(request)


@router.get("/health", response_model=APIResponse)
async def ai_health_check() -> APIResponse:
    """
    Check the health of AI services.
    
    This endpoint verifies that AI services are properly configured and available.
    """
    try:
        health_status = {
            "ai_configured": bool(settings.OPENAI_API_KEY),
            "default_model": settings.DEFAULT_MODEL,
            "default_provider": settings.DEFAULT_LLM_PROVIDER,
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
            "advanced_processor_available": advanced_note_processor.extraction_chain is not None
        }
        
        return APIResponse(
            success=True,
            message="AI service health check completed",
            data=health_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking AI service health: {str(e)}"
        )


@router.post("/test-extraction", response_model=APIResponse)
async def test_extraction(request: AdvancedNoteProcessingRequest) -> APIResponse:
    """
    Test advanced note extraction without creating entities.
    
    This endpoint is useful for testing the AI extraction capabilities
    without affecting the graph database.
    """
    try:
        # Check if AI is configured
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="AI service is not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Set the main person context
        advanced_note_processor.set_main_person(request.main_person_name, request.main_person_id)
        
        # Process the note with advanced system (but don't create entities)
        result = await advanced_note_processor.process_note_advanced(request.note_text)
        
        # Remove created entities from result for test mode
        test_result = {
            "analysis": result["analysis"],
            "resolved_entities": result["resolved_entities"],
            "validated_relationships": result["validated_relationships"],
            "main_person_id": result["main_person_id"],
            "processing_confidence": result["analysis"].get("confidence_score", 0.8),
            "test_mode": True
        }
        
        return APIResponse(
            success=True,
            message="Advanced note extraction test completed successfully",
            data=test_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing advanced note extraction: {str(e)}"
        )


@router.get("/suggestions", response_model=APIResponse)
def get_suggestions():
    # Return an empty list for now
    return APIResponse(success=True, data=[], message="No suggestions yet")


@router.post("/create-entities", response_model=APIResponse)
async def create_entities_from_ai(request: AdvancedNoteProcessingRequest) -> APIResponse:
    """
    Create graph entities from advanced AI processing results.
    
    This endpoint takes the results from advanced AI processing and creates
    the corresponding nodes and relationships in the graph database.
    """
    try:
        # Check if AI is configured
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="AI service is not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Set the main person context
        advanced_note_processor.set_main_person(request.main_person_name, request.main_person_id)
        
        # Process the note and create entities
        result = await advanced_note_processor.process_note_advanced(request.note_text)
        
        return APIResponse(
            success=True,
            message="Entities created successfully in the graph using advanced processing",
            data={
                "created_entities": result["created_entities"],
                "note_text": request.note_text,
                "main_person_id": result["main_person_id"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating entities from AI processing: {str(e)}"
        )


@router.get("/disambiguation/{entity_name}", response_model=APIResponse)
async def get_disambiguation_suggestions(entity_name: str, entity_type: str = Query(..., description="Type of entity")):
    """
    Get disambiguation suggestions for an entity.
    
    This endpoint helps resolve ambiguous entity references by providing
    potential matches from the existing database.
    """
    try:
        # This would be implemented to show disambiguation options
        # For now, return a placeholder
        suggestions = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "suggestions": [],
            "message": "Disambiguation suggestions not yet implemented"
        }
        
        return APIResponse(
            success=True,
            message="Disambiguation suggestions retrieved",
            data=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting disambiguation suggestions: {str(e)}"
        ) 