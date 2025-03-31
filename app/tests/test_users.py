"""
Tests for user creation, deletion, listing, and access control.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import uuid
from fastapi.testclient import TestClient


# --------------------------------------------------------------------------------
# TESTS

def test_create_user(client: TestClient, admin_token: str):
    """
    Test user creation via /create_user endpoint.

    - Sends a POST request with login, password, role, and permissions.
    - Expects a 200 OK response and correct user data in response body.
    """
    payload = {"login": "newuser", "password": "pass123", "role": "user", "permissions": ["read"]}
    response = client.post(
        "/api/v1/admin/create_user",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["login"] == "newuser"
    assert data["role"] == "user"
    assert data["id"] is not None


def test_create_user_duplicate(client: TestClient, admin_token: str):
    """
    Test duplicate user creation.

    - Creates a user with a specific login.
    - Attempts to create the same user again.
    - Expects a 400 Bad Request with a message about duplicate login.
    """
    payload = {"login": "dupuser", "password": "123", "role": "user", "permissions": []}
    client.post("/api/v1/admin/create_user", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    response = client.post("/api/v1/admin/create_user", json=payload,
                           headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "already exists" in response.json()["data"]


def test_get_users_list(client: TestClient, admin_token: str):
    """
    Test retrieving a paginated list of users.

    - Creates 15 users.
    - Sends a GET request with limit and offset parameters.
    - Expects a list of users with length <= limit.
    """
    for i in range(15):
        client.post(
            "/api/v1/admin/create_user",
            json={"login": f"user{i}", "password": "123", "role": "user", "permissions": []},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    response = client.get("/api/v1/admin/users?skip=0&limit=10", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) <= 10


def test_remove_user(client: TestClient, admin_token: str):
    """
    Test user deletion by ID.

    - Creates a user.
    - Deletes the user using their ID.
    - Expects a 200 OK response with confirmation message.
    """
    response = client.post(
        "/api/v1/admin/create_user",
        json={"login": "todelete", "password": "delete", "role": "user", "permissions": []},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    user_id = response.json()["data"]["id"]

    response = client.delete(
        f"/api/v1/admin/remove_user/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "removed" in response.json()["data"]["message"]


def test_remove_nonexistent_user(client: TestClient, admin_token: str):
    """
    Test deletion of a non-existent user.

    - Sends a DELETE request with a random UUID.
    - Expects a 404 Not Found response.
    """
    response = client.delete(f"/api/v1/admin/remove_user/{str(uuid.uuid4())}",
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
    assert "not found" in response.json()["data"]


def test_update_user_permissions(client: TestClient, admin_token: str):
    """
    Test updating user permissions.

    - Creates a user with initial permissions.
    - Sends a PUT request to update their permissions.
    - Expects a 200 OK response and updated permission list in the result.
    """
    payload = {"login": "created_user", "password": "pass123", "role": "user", "permissions": ["read"]}
    response = client.post(
        "/api/v1/admin/create_user",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.json()["data"]
    created_user_id = data["id"]

    response = client.put(
        f"/api/v1/admin/update_permissions/{created_user_id}",
        json={"permissions": ["new_permission"]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == created_user_id
    assert "new_permission" in data["permissions"]
