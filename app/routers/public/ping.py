"""
Public Auth

Provides user-accessible endpoints such as profile check.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi import APIRouter, Depends

from app.utils.auth.jwt_handler import verify_token
from app.utils.base_handler import base_handler

# --------------------------------------------------------------------------------
# ROUTER CONFIGURATION

router = APIRouter(tags=["Profile Check"])


# --------------------------------------------------------------------------------
# ENDPOINTS

@router.get(
    "/me",
    openapi_extra={
        "examples": {
            "get_current_user": {
                "summary": "Get current user info",
                "description": "Returns the decoded token payload including role, permissions, and expiration.",
                "value": {
                    "sub": "testuser",
                    "role": "user",
                    "permissions": ["read_docs"],
                    "exp": 1743401472,
                    "type": "access"
                }
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                    "import requests\n\n"
                    "url = 'http://localhost:8000/api/v1/public/auth/me'\n"
                    "headers = {'Authorization': 'Bearer <access_token>'}\n"
                    "response = requests.get(url, headers=headers)\n"
                    "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "Decoded JWT token payload",
                "content": {
                    "application/json": {
                        "example": {
                            "sub": "testuser",
                            "role": "user",
                            "permissions": ["read_docs"],
                            "exp": 1743401472,
                            "type": "access"
                        }
                    }
                }
            },
            "401": {
                "description": "Unauthorized - Missing or invalid token",
                "content": {
                    "application/json": {
                        "example": {"detail": "Missing Authorization header"}
                    }
                }
            }
        }
    }
)
@base_handler
async def get_current_user(payload=Depends(verify_token)):
    """
    Retrieve the current authenticated user's payload.

    - Requires a valid Bearer access token in the Authorization header.
    - Returns the decoded JWT token payload containing:
        - `sub`: subject (typically username)
        - `role`: user role
        - `permissions`: list of permissions
        - `exp`: expiration timestamp
        - `type`: token type (should be 'access')

    Useful for user-facing applications to confirm identity and role.
    """
    return payload