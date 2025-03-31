"""
Tests for the /me public endpoint.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi.testclient import TestClient


# --------------------------------------------------------------------------------
# TESTS

def test_get_current_user_payload(client: TestClient, user_token: str):
    """
    Test successful retrieval of current user payload using valid JWT.

    - Sends a GET request to /me with a valid Authorization header.
    - Expects a 200 OK response.
    - Asserts that the returned payload contains the correct role.
    """
    response = client.get("/api/v1/me", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["role"] == "user"


def test_get_current_user_no_token(client: TestClient):
    """
    Test error when accessing /me endpoint without Authorization header.

    - Sends a GET request to /me without any token.
    - Expects 401 Unauthorized response.
    - Verifies that the response includes 'Missing Authorization header'.
    """
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert "Missing Authorization header" == response.json()["detail"]
