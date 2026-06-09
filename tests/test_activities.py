import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def _quote(name: str) -> str:
    return quote(name, safe='')


import pytest


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "tester@mergington.edu"




    # signup
    res = client.post(f"/activities/{_quote(activity)}/signup", params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")

    data = client.get("/activities").json()
    assert email in data[activity]["participants"]

    # duplicate should fail
    res2 = client.post(f"/activities/{_quote(activity)}/signup", params={"email": email})
    assert res2.status_code == 400


def test_unregister():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # existing

    # unregister existing
    res = client.delete(f"/activities/{_quote(activity)}/participants", params={"email": email})
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]

    # deleting non-existent should return 404
    res2 = client.delete(f"/activities/{_quote(activity)}/participants", params={"email": "not@there.edu"})
    assert res2.status_code == 404
