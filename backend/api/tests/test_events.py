import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)
API_PREFIX = "/api/v1/events"


def create_event_payload(name="Test Event", date="2030-01-01T00:00:00Z", type="conference"):
    return {"name": name, "date": date, "type": type}


def test_create_event():
    payload = create_event_payload()
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["data"]["name"] == payload["name"]
    event_id = data["data"]["id"]
    # Cleanup
    client.delete(f"{API_PREFIX}/{event_id}")


def test_get_event_not_found():
    response = client.get(f"{API_PREFIX}/nonexistent-id")
    assert response.status_code == 404


def test_crud_event():
    # Create
    payload = create_event_payload("CRUD Event")
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    event = response.json()["data"]
    event_id = event["id"]
    # Get
    response = client.get(f"{API_PREFIX}/{event_id}")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "CRUD Event"
    # Update
    update_payload = {"name": "Updated Event"}
    response = client.put(f"{API_PREFIX}/{event_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Event"
    # Delete
    response = client.delete(f"{API_PREFIX}/{event_id}")
    assert response.status_code == 200
    # Get after delete
    response = client.get(f"{API_PREFIX}/{event_id}")
    assert response.status_code == 404


def test_list_events():
    # Create an event
    payload = create_event_payload("List Event")
    response = client.post(API_PREFIX + "/", json=payload)
    event_id = response.json()["data"]["id"]
    # List
    response = client.get(API_PREFIX + "/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "items" in data
    assert any(e["id"] == event_id for e in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{event_id}")


def test_search_events():
    # Create an event
    payload = create_event_payload("Searchable Event")
    response = client.post(API_PREFIX + "/", json=payload)
    event_id = response.json()["data"]["id"]
    # Search
    response = client.get(API_PREFIX + "/", params={"search": "Searchable"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(e["id"] == event_id for e in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{event_id}")


def test_link_and_unlink_person_to_event():
    # Create event
    event_resp = client.post(API_PREFIX + "/", json=create_event_payload("LinkTest"))
    event_id = event_resp.json()["data"]["id"]
    # Create person
    person_resp = client.post("/api/v1/people/", json={"name": "Event Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link
    link_resp = client.post(f"{API_PREFIX}/{event_id}/people/{person_id}")
    assert link_resp.status_code == 200
    # Get people at event
    resp = client.get(f"{API_PREFIX}/{event_id}/people")
    assert resp.status_code == 200
    people = resp.json()["data"]
    assert any(p["id"] == person_id for p in people)
    # Unlink
    unlink_resp = client.delete(f"{API_PREFIX}/{event_id}/people/{person_id}")
    assert unlink_resp.status_code == 200
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{event_id}")


def test_get_upcoming_and_recent_events():
    # Create a future event
    payload = create_event_payload("Future Event", date="2099-01-01T00:00:00Z")
    response = client.post(API_PREFIX + "/", json=payload)
    event_id = response.json()["data"]["id"]
    # Upcoming
    resp = client.get(f"{API_PREFIX}/upcoming")
    assert resp.status_code == 200
    assert any(e["id"] == event_id for e in resp.json()["data"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{event_id}") 