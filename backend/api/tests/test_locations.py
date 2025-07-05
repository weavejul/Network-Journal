import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)
API_PREFIX = "/api/v1/locations"


def create_location_payload(city="Test City", state="Test State", country="Test Country"):
    return {"city": city, "state": state, "country": country}


def test_create_location():
    payload = create_location_payload()
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["data"]["city"] == payload["city"]
    location_id = data["data"]["id"]
    # Cleanup
    client.delete(f"{API_PREFIX}/{location_id}")


def test_get_location_not_found():
    response = client.get(f"{API_PREFIX}/nonexistent-id")
    assert response.status_code == 404


def test_crud_location():
    # Create
    payload = create_location_payload("CRUD City")
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    location = response.json()["data"]
    location_id = location["id"]
    # Get
    response = client.get(f"{API_PREFIX}/{location_id}")
    assert response.status_code == 200
    assert response.json()["data"]["city"] == "CRUD City"
    # Update
    update_payload = {"city": "Updated City"}
    response = client.put(f"{API_PREFIX}/{location_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["data"]["city"] == "Updated City"
    # Delete
    response = client.delete(f"{API_PREFIX}/{location_id}")
    assert response.status_code == 200
    # Get after delete
    response = client.get(f"{API_PREFIX}/{location_id}")
    assert response.status_code == 404


def test_list_locations():
    # Create a location
    payload = create_location_payload("List City")
    response = client.post(API_PREFIX + "/", json=payload)
    location_id = response.json()["data"]["id"]
    # List
    response = client.get(API_PREFIX + "/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "items" in data
    assert any(l["id"] == location_id for l in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{location_id}")


def test_search_locations():
    # Create a location
    payload = create_location_payload("Searchable City")
    response = client.post(API_PREFIX + "/", json=payload)
    location_id = response.json()["data"]["id"]
    # Search
    response = client.get(API_PREFIX + "/", params={"search": "Searchable"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(l["id"] == location_id for l in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{location_id}")


def test_link_and_unlink_person_to_location():
    # Create location
    location_resp = client.post(API_PREFIX + "/", json=create_location_payload("LinkCity"))
    location_id = location_resp.json()["data"]["id"]
    # Create person
    person_resp = client.post("/api/v1/people/", json={"name": "Location Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link
    link_resp = client.post(f"{API_PREFIX}/{location_id}/people/{person_id}")
    assert link_resp.status_code == 200
    # Get people at location
    resp = client.get(f"{API_PREFIX}/{location_id}/people")
    assert resp.status_code == 200
    people = resp.json()["data"]
    assert any(p["id"] == person_id for p in people)
    # Unlink
    unlink_resp = client.delete(f"{API_PREFIX}/{location_id}/people/{person_id}")
    assert unlink_resp.status_code == 200
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{location_id}")


def test_get_popular_locations():
    # Create location and person
    location_resp = client.post(API_PREFIX + "/", json=create_location_payload("PopularCity"))
    location_id = location_resp.json()["data"]["id"]
    person_resp = client.post("/api/v1/people/", json={"name": "Popular Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link
    client.post(f"{API_PREFIX}/{location_id}/people/{person_id}")
    # Get popular locations
    resp = client.get(f"{API_PREFIX}/popular")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(l["city"] == "PopularCity" for l in data)
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{location_id}") 