import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, UTC

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.types import Interaction, InteractionChannel, DataSource
from backend.api.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"

@pytest.fixture
def sample_interaction():
    return {
        "date": datetime.now(UTC).isoformat(),
        "channel": InteractionChannel.EMAIL,
        "summary": "Had a great conversation about AI and machine learning",
        "data_source": DataSource.USER_NOTE
    }

@pytest.fixture
def sample_person():
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "data_source": "user_note"
    }

def test_create_interaction(sample_interaction):
    """Test creating a new interaction."""
    response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["channel"] == sample_interaction["channel"]
    assert data["summary"] == sample_interaction["summary"]
    assert "id" in data
    assert "created_at" in data

def test_get_interaction(sample_interaction):
    """Test getting an interaction by ID."""
    # Create an interaction first
    create_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = create_response.json()["data"]["id"]
    
    # Get the interaction
    response = client.get(f"{API_PREFIX}/interactions/{interaction_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == interaction_id
    assert data["summary"] == sample_interaction["summary"]

def test_get_interaction_not_found():
    """Test getting a non-existent interaction."""
    response = client.get(f"{API_PREFIX}/interactions/non-existent-id")
    assert response.status_code == 404

def test_list_interactions(sample_interaction):
    """Test listing all interactions."""
    # Create an interaction first
    client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    
    # List all interactions
    response = client.get(f"{API_PREFIX}/interactions/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0

def test_update_interaction(sample_interaction):
    """Test updating an interaction."""
    # Create an interaction first
    create_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = create_response.json()["data"]["id"]
    
    # Update the interaction
    update_data = {
        "summary": "Updated summary about AI discussion",
        "channel": InteractionChannel.CALL
    }
    response = client.put(f"{API_PREFIX}/interactions/{interaction_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["summary"] == update_data["summary"]
    assert data["channel"] == update_data["channel"]

def test_update_interaction_not_found():
    """Test updating a non-existent interaction."""
    update_data = {"summary": "Updated summary"}
    response = client.put(f"{API_PREFIX}/interactions/non-existent-id", json=update_data)
    assert response.status_code == 404

def test_delete_interaction(sample_interaction):
    """Test deleting an interaction."""
    # Create an interaction first
    create_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = create_response.json()["data"]["id"]
    
    # Delete the interaction
    response = client.delete(f"{API_PREFIX}/interactions/{interaction_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verify it's deleted
    get_response = client.get(f"{API_PREFIX}/interactions/{interaction_id}")
    assert get_response.status_code == 404

def test_delete_interaction_not_found():
    """Test deleting a non-existent interaction."""
    response = client.delete(f"{API_PREFIX}/interactions/non-existent-id")
    assert response.status_code == 404

def test_link_interaction_to_person(sample_interaction, sample_person):
    """Test linking an interaction to a person."""
    # Create a person first
    person_response = client.post(f"{API_PREFIX}/people/", json=sample_person)
    person_id = person_response.json()["data"]["id"]
    
    # Create an interaction
    interaction_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = interaction_response.json()["data"]["id"]
    
    # Link them
    response = client.post(f"{API_PREFIX}/interactions/{interaction_id}/link-person/{person_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_link_interaction_to_person_not_found(sample_interaction):
    """Test linking an interaction to a non-existent person."""
    # Create an interaction
    interaction_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = interaction_response.json()["data"]["id"]
    
    # Try to link to non-existent person
    response = client.post(f"{API_PREFIX}/interactions/{interaction_id}/link-person/non-existent-person")
    assert response.status_code == 404

def test_get_interactions_for_person(sample_interaction, sample_person):
    """Test getting all interactions for a person."""
    # Create a person
    person_response = client.post(f"{API_PREFIX}/people/", json=sample_person)
    person_id = person_response.json()["data"]["id"]
    
    # Create an interaction
    interaction_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = interaction_response.json()["data"]["id"]
    
    # Link them
    client.post(f"{API_PREFIX}/interactions/{interaction_id}/link-person/{person_id}")
    
    # Get interactions for the person
    response = client.get(f"{API_PREFIX}/interactions/person/{person_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == interaction_id

def test_get_people_for_interaction(sample_interaction, sample_person):
    """Test getting all people for an interaction."""
    # Create a person
    person_response = client.post(f"{API_PREFIX}/people/", json=sample_person)
    person_id = person_response.json()["data"]["id"]
    
    # Create an interaction
    interaction_response = client.post(f"{API_PREFIX}/interactions/", json=sample_interaction)
    interaction_id = interaction_response.json()["data"]["id"]
    
    # Link them
    client.post(f"{API_PREFIX}/interactions/{interaction_id}/link-person/{person_id}")
    
    # Get people for the interaction
    response = client.get(f"{API_PREFIX}/interactions/{interaction_id}/people")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == person_id

def test_interaction_with_different_channels():
    """Test creating interactions with different channels."""
    channels = [InteractionChannel.EMAIL, InteractionChannel.CALL, InteractionChannel.IN_PERSON]
    
    for channel in channels:
        interaction_data = {
            "date": datetime.now(UTC).isoformat(),
            "channel": channel,
            "summary": f"Test interaction via {channel}",
            "data_source": DataSource.USER_NOTE
        }
        response = client.post(f"{API_PREFIX}/interactions/", json=interaction_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["channel"] == channel

def test_interaction_validation():
    """Test interaction validation with invalid data."""
    # Test with missing required fields
    invalid_interaction = {
        "channel": InteractionChannel.EMAIL
        # Missing date and summary
    }
    response = client.post(f"{API_PREFIX}/interactions/", json=invalid_interaction)
    assert response.status_code == 422  # Validation error 