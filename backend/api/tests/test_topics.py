import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from shared.types import Topic

client = TestClient(app)
API_PREFIX = "/api/v1/topics"

def create_topic_payload(name="Test Topic"):
    return {"name": name}


def test_create_topic():
    payload = create_topic_payload()
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["data"]["name"] == payload["name"]
    topic_id = data["data"]["id"]
    # Cleanup
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_get_topic_not_found():
    response = client.get(f"{API_PREFIX}/nonexistent-id")
    assert response.status_code == 404


def test_crud_topic():
    # Create
    payload = create_topic_payload("CRUD Topic")
    response = client.post(API_PREFIX + "/", json=payload)
    assert response.status_code == 200
    topic = response.json()["data"]
    topic_id = topic["id"]
    # Get
    response = client.get(f"{API_PREFIX}/{topic_id}")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "CRUD Topic"
    # Update
    update_payload = {"name": "Updated Topic"}
    response = client.put(f"{API_PREFIX}/{topic_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Topic"
    # Delete
    response = client.delete(f"{API_PREFIX}/{topic_id}")
    assert response.status_code == 200
    # Get after delete
    response = client.get(f"{API_PREFIX}/{topic_id}")
    assert response.status_code == 404


def test_list_topics():
    # Create a topic
    payload = create_topic_payload("List Topic")
    response = client.post(API_PREFIX + "/", json=payload)
    topic_id = response.json()["data"]["id"]
    # List
    response = client.get(API_PREFIX + "/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "items" in data
    assert any(t["id"] == topic_id for t in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_search_topics():
    # Create a topic
    payload = create_topic_payload("Searchable Topic")
    response = client.post(API_PREFIX + "/", json=payload)
    topic_id = response.json()["data"]["id"]
    # Search
    response = client.get(API_PREFIX + "/", params={"search": "Searchable"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(t["id"] == topic_id for t in data["items"])
    # Cleanup
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_link_and_unlink_person_to_topic():
    # Create topic
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("LinkTest"))
    topic_id = topic_resp.json()["data"]["id"]
    # Create person
    person_resp = client.post("/api/v1/people/", json={"name": "Topic Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link
    link_resp = client.post(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    assert link_resp.status_code == 200
    # Get people interested in topic
    resp = client.get(f"{API_PREFIX}/{topic_id}/people")
    assert resp.status_code == 200
    people = resp.json()["data"]
    assert any(p["id"] == person_id for p in people)
    # Unlink
    unlink_resp = client.delete(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    assert unlink_resp.status_code == 200
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_get_popular_topics():
    # Create topics and people
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("PopularTopic"))
    topic_id = topic_resp.json()["data"]["id"]
    person_resp = client.post("/api/v1/people/", json={"name": "Popular Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link
    client.post(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    # Get popular topics
    resp = client.get(f"{API_PREFIX}/popular")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(t["name"] == "PopularTopic" for t in data)
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_create_topic_missing_name():
    """Should fail to create a topic with missing name (422)."""
    response = client.post(API_PREFIX + "/", json={})
    assert response.status_code == 422


def test_create_topic_invalid_type():
    """Should fail to create a topic with invalid type for name (422)."""
    response = client.post(API_PREFIX + "/", json={"name": 123})
    assert response.status_code == 422


def test_duplicate_topic_creation():
    """Should allow duplicate topic names (if not unique), or return 409/400 if unique constraint enforced."""
    payload = create_topic_payload("Duplicate Topic")
    response1 = client.post(API_PREFIX + "/", json=payload)
    response2 = client.post(API_PREFIX + "/", json=payload)
    assert response1.status_code == 200
    # Accept either 200 (allowed) or 409/400 (unique constraint)
    assert response2.status_code in (200, 409, 400)
    topic_id1 = response1.json()["data"]["id"]
    if response2.status_code == 200:
        topic_id2 = response2.json()["data"]["id"]
        client.delete(f"{API_PREFIX}/{topic_id2}")
    client.delete(f"{API_PREFIX}/{topic_id1}")


def test_update_topic_invalid_data():
    """Should fail to update a topic with invalid data (422)."""
    payload = create_topic_payload("Update Invalid Topic")
    response = client.post(API_PREFIX + "/", json=payload)
    topic_id = response.json()["data"]["id"]
    response = client.put(f"{API_PREFIX}/{topic_id}", json={"name": 123})
    assert response.status_code == 422
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_search_topics_no_results():
    """Should return empty list if no topics match search."""
    response = client.get(API_PREFIX + "/", params={"search": "NoSuchTopicName"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["items"] == []


def test_pagination_topics():
    """Should paginate topics correctly."""
    # Create 3 topics
    ids = []
    for i in range(3):
        resp = client.post(API_PREFIX + "/", json=create_topic_payload(f"PaginateTopic{i}"))
        ids.append(resp.json()["data"]["id"])
    # Page size 2, page 1
    resp1 = client.get(API_PREFIX + "/", params={"page": 1, "page_size": 2})
    assert resp1.status_code == 200
    data1 = resp1.json()["data"]
    assert data1["page"] == 1
    assert data1["page_size"] == 2
    assert len(data1["items"]) <= 2
    # Page 2
    resp2 = client.get(API_PREFIX + "/", params={"page": 2, "page_size": 2})
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert data2["page"] == 2
    # Cleanup
    for tid in ids:
        client.delete(f"{API_PREFIX}/{tid}")


def test_link_person_to_topic_nonexistent():
    """Should fail to link nonexistent person or topic (404/400)."""
    # Create a topic
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("LinkFail"))
    topic_id = topic_resp.json()["data"]["id"]
    # Try to link nonexistent person
    resp = client.post(f"{API_PREFIX}/{topic_id}/people/nonexistent-person")
    assert resp.status_code in (400, 404)
    # Try to link to nonexistent topic
    person_resp = client.post("/api/v1/people/", json={"name": "Ghost"})
    person_id = person_resp.json()["data"]["id"]
    resp2 = client.post(f"{API_PREFIX}/nonexistent-topic/people/{person_id}")
    assert resp2.status_code in (400, 404)
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_unlink_person_from_topic_not_linked():
    """Should handle unlinking a person not linked to a topic gracefully (200 or 400)."""
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("UnlinkNotLinked"))
    topic_id = topic_resp.json()["data"]["id"]
    person_resp = client.post("/api/v1/people/", json={"name": "Unlinked Person"})
    person_id = person_resp.json()["data"]["id"]
    # Unlink (should not error fatally)
    resp = client.delete(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    assert resp.status_code in (200, 400)
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_link_person_to_topic_double_link():
    """Should handle double-linking a person to a topic gracefully (idempotent)."""
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("DoubleLink"))
    topic_id = topic_resp.json()["data"]["id"]
    person_resp = client.post("/api/v1/people/", json={"name": "DoubleLink Person"})
    person_id = person_resp.json()["data"]["id"]
    # Link twice
    resp1 = client.post(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    resp2 = client.post(f"{API_PREFIX}/{topic_id}/people/{person_id}")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # Cleanup
    client.delete(f"/api/v1/people/{person_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_get_people_interested_in_topic_empty():
    """Should return empty list if no people are linked to topic."""
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("NoPeople"))
    topic_id = topic_resp.json()["data"]["id"]
    resp = client.get(f"{API_PREFIX}/{topic_id}/people")
    assert resp.status_code == 200
    people = resp.json()["data"]
    assert people == []
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_link_and_unlink_interaction_to_topic():
    """Should link and unlink an interaction to a topic."""
    # Create topic
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("LinkInteraction"))
    topic_id = topic_resp.json()["data"]["id"]
    # Create interaction
    interaction_resp = client.post("/api/v1/interactions/", json={
        "date": "2025-01-01T00:00:00Z",
        "channel": "email",
        "summary": "Discussed topic"
    })
    interaction_id = interaction_resp.json()["data"]["id"]
    # Link
    link_resp = client.post(f"{API_PREFIX}/{topic_id}/interactions/{interaction_id}")
    assert link_resp.status_code == 200
    # Get interactions for topic
    resp = client.get(f"{API_PREFIX}/{topic_id}/interactions")
    assert resp.status_code == 200
    interactions = resp.json()["data"]
    assert any(i["id"] == interaction_id for i in interactions)
    # Cleanup
    client.delete(f"/api/v1/interactions/{interaction_id}")
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_get_interactions_for_topic_empty():
    """Should return empty list if no interactions are linked to topic."""
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("NoInteractions"))
    topic_id = topic_resp.json()["data"]["id"]
    resp = client.get(f"{API_PREFIX}/{topic_id}/interactions")
    assert resp.status_code == 200
    interactions = resp.json()["data"]
    assert interactions == []
    client.delete(f"{API_PREFIX}/{topic_id}")


def test_popular_topics_empty():
    """Should return topics with 0 interest_count when no new topics have links."""
    # Create a new topic that won't have any links
    topic_resp = client.post(API_PREFIX + "/", json=create_topic_payload("EmptyPopularTopic"))
    topic_id = topic_resp.json()["data"]["id"]
    
    resp = client.get(f"{API_PREFIX}/popular")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    
    # Find our specific topic in the results
    our_topic = next((t for t in data if t["id"] == topic_id), None)
    assert our_topic is not None, "Our topic should be in the popular topics list"
    assert our_topic.get("interest_count", 0) == 0, "Our topic should have 0 interest count"
    
    # Cleanup
    client.delete(f"{API_PREFIX}/{topic_id}") 