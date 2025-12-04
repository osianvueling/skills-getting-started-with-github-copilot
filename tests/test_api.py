import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # A known activity from the seeded data
    assert "Chess Club" in data


def test_signup_and_reflects_in_activities():
    activity = "Chess Club"
    email = "test.student@example.com"
    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    before = len(activities[activity]["participants"])
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    json_ = resp.json()
    assert "Signed up" in json_["message"]

    # Check in-memory state was updated
    assert email in activities[activity]["participants"]
    after = len(activities[activity]["participants"])
    assert after == before + 1

    # Cleanup
    activities[activity]["participants"].remove(email)


def test_signup_duplicate_fails():
    activity = "Chess Club"
    email = "duplicate@example.com"
    # Ensure the email is present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_signup_unknown_activity():
    resp = client.post("/activities/NonExistent/signup?email=a@b.com")
    assert resp.status_code == 404
