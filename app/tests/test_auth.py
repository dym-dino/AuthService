"""
Tests for token generation and refresh endpoints.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi.testclient import TestClient

from app.config import settings
from app.utils.auth.hash import hash_str


# --------------------------------------------------------------------------------
# TESTS

def test_get_token_user(client: TestClient):
    """
    Test generating access and refresh tokens for a user.

    - Sends a POST request to /token with role 'user', login, password, and valid secret_hash.
    - Expects a 200 OK response.
    - Asserts that both access_token and refresh_token are present in the response.
    """
    login = "test_user"
    password = "test_pass"
    response = client.post("/api/v1/token", json={
        "role": "user",
        "login": login,
        "password": password,
        "secret_hash": hash_str(settings.SECRET_KEY)
    })
    assert response.status_code == 200
    tokens = response.json()["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_get_token_admin_create_and_login(client: TestClient):
    """
    Test token generation for an admin with user auto-creation and authentication.

    - Sends a POST request with admin role, login, password, and secret_hash.
    - Expects user creation on first call and authentication on the second.
    - Verifies both calls return valid tokens.
    """
    login = "admin_test"
    password = "secure123"
    response = client.post("/api/v1/token", json={
        "role": "admin",
        "login": login,
        "password": password,
        "secret_hash": hash_str(settings.SECRET_KEY)
    })
    assert response.status_code == 200
    tokens = response.json()["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Try again with same credentials (should authenticate, not create)
    response2 = client.post("/api/v1/token", json={
        "role": "admin",
        "login": login,
        "password": password,
        "secret_hash": hash_str(settings.SECRET_KEY)
    })
    assert response2.status_code == 200
    assert response2.json()["data"]["access_token"] != ""


def test_invalid_secret_key(client: TestClient):
    """
    Test access denial when an invalid secret_hash is used.

    - Sends a POST request to /token with an incorrect secret_hash.
    - Expects 403 Forbidden response.
    - Verifies the error message mentions invalid token secret.
    """
    response = client.post("/api/v1/token", json={
        "role": "user",
        "login": "user1",
        "password": "userpass",
        "secret_hash": hash_str("WRONG_SECRET")
    })
    assert response.status_code == 403
    assert "Invalid token secret" in response.json()["data"]


def test_refresh_token(client: TestClient):
    """
    Test refreshing an access token using a valid refresh token.

    - Sends a POST request to /token to obtain tokens.
    - Uses the refresh_token in a POST request to /refresh.
    - Expects 200 OK and a new access_token in the response.
    """
    token_response = client.post("/api/v1/token", json={
        "role": "user",
        "login": "admin",
        "password": "adminpass",
        "secret_hash": hash_str(settings.SECRET_KEY)
    })
    refresh_token = token_response.json()["data"]["refresh_token"]

    refresh_response = client.post("/api/v1/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()["data"]


def test_invalid_refresh_token_type(client: TestClient, user_token: str):
    """
    Test error when using an access token instead of a refresh token for refreshing.

    - Sends an access_token in a POST request to /refresh.
    - Expects 403 Forbidden response.
    - Checks for error message "Expected refresh token".
    """
    response = client.post("/api/v1/refresh", json={
        "refresh_token": user_token
    })
    assert response.status_code == 403
    assert "Expected refresh token" in response.json()["data"]
