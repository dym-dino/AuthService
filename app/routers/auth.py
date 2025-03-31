"""
Auth Token

Provides endpoints for token generation and refresh.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import user as models
from app.models.token import TokenRequest, RefreshRequest
from app.utils.auth.hash import hash_str
from app.utils.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.utils.base_handler import base_handler
from app.utils.rate_limit import limiter

# --------------------------------------------------------------------------------
# ROUTER CONFIGURATION

router = APIRouter(tags=["Authorization"])


# --------------------------------------------------------------------------------
# ENDPOINTS

@router.post(
    "/token",
    openapi_extra={
        "examples": {
            "get_token_user": {
                "summary": "Get token for user",
                "description": "Generates access and refresh tokens using user role and secret key.",
                "value": {
                    "role": "user",
                    "secret_hash": "<hashed_secret>"
                }
            },
            "get_token_admin": {
                "summary": "Get token for admin",
                "description": "Generates tokens using login, password, role, and secret hash.",
                "value": {
                    "role": "admin",
                    "login": "admin1",
                    "password": "securepass",
                    "secret_hash": "<hashed_secret>"
                }
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/token'\n"
                        "payload = {\"role\": \"user\", \"secret_hash\": \"<hashed_secret>\"}\n"
                        "response = requests.post(url, json=payload)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "JWT tokens returned",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "<access_token>",
                            "refresh_token": "<refresh_token>"
                        }
                    }
                }
            },
            "403": {
                "description": "Forbidden - Invalid credentials or secret",
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid token secret"}
                    }
                }
            }
        }
    }
)
@limiter.limit("5/minute")
@base_handler
async def get_token(request: Request, payload: TokenRequest, db: Session = Depends(get_db)):
    """
    Generates access and refresh tokens based on role and credentials.

    - If role is `user`, only the secret hash is required.
    - If role is `admin` or `operator`, login and password are also required.
    - Automatically creates the user if they don't exist.
    - Returns access and refresh tokens.
    """
    if payload.secret_hash != hash_str(settings.SECRET_KEY):
        raise HTTPException(status_code=403, detail="Invalid token secret")

    if not payload.login or not payload.password:
        raise HTTPException(status_code=400, detail="Missing login/password")

    user = db.query(models.User).filter(models.User.login == payload.login).first()
    hashed_pass = hash_str(payload.password)

    if not user:
        user = models.User(login=payload.login, password=hashed_pass, role=payload.role)
        db.add(user)
        db.commit()
    elif user.password != hashed_pass:
        raise HTTPException(status_code=403, detail="Invalid password")

    access = create_access_token({"role": payload.role})
    refresh = create_refresh_token({"role": payload.role})
    return {"access_token": access, "refresh_token": refresh}


@router.post(
    "/refresh",
    openapi_extra={
        "examples": {
            "refresh_token": {
                "summary": "Refresh token",
                "description": "Issues a new access token using a valid refresh token.",
                "value": {
                    "refresh_token": "<your_refresh_token>"
                }
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/refresh'\n"
                        "payload = {\"refresh_token\": \"<your_refresh_token>\"}\n"
                        "response = requests.post(url, json=payload)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "Access token refreshed",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "<new_access_token>"
                        }
                    }
                }
            },
            "403": {
                "description": "Forbidden - Invalid or wrong token type",
                "content": {
                    "application/json": {
                        "example": {"detail": "Expected refresh token"}
                    }
                }
            }
        }
    }
)
@limiter.limit("5/minute")
@base_handler
async def refresh_token(request: Request, payload: RefreshRequest):
    """
    Issues a new access token using a valid refresh token.

    - Requires a valid JWT refresh token in the request body.
    - Verifies that the token is of type 'refresh'.
    - Returns a new access token.
    """
    decoded = verify_token(token=payload.refresh_token, expected_type="refresh")

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    access = create_access_token({"role": decoded.get("role")})
    return {"access_token": access}
