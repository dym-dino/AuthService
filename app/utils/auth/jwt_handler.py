"""
JWT Handler

Provides functions for creating and verifying JWT tokens for authentication,
role validation, and permission-based access control.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader

from app.config import settings

# --------------------------------------------------------------------------------
# CONFIGURATION

oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)


# --------------------------------------------------------------------------------
# TOKEN HELPERS

def get_token(authorization: str = Depends(oauth2_scheme)) -> str:
    """
    Extracts token from Authorization header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer":
        return token
    elif scheme:
        return scheme
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Incorrect authorization scheme",
    )


def create_access_token(data: Dict[str, Any], expires_delta: timedelta = timedelta(minutes=15)) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(data: Dict[str, Any], expires_delta: timedelta = timedelta(days=7)) -> str:
    """
    Creates a JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


# --------------------------------------------------------------------------------
# VERIFY AND DEPENDENCIES

def verify_token(token: str = Depends(get_token), expected_type: str = "access") -> Dict[str, Any]:
    """
    Verifies a JWT token (access or refresh) and returns its payload.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise HTTPException(status_code=403, detail=f"Expected {expected_type} token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_refresh_token(token: str = Depends(get_token)) -> Dict[str, Any]:
    """
    Verifies a JWT refresh token and returns its payload.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=403, detail="Expected refresh token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --------------------------------------------------------------------------------
# PERMISSION DECORATOR

def require_permission(permission: str):
    """
    Dependency that checks if the user has a specific permission in token payload.
    Usage:
        @router.get("/secure", dependencies=[Depends(require_permission("read_users"))])
    """

    def wrapper(payload: Dict[str, Any] = Depends(verify_token)):
        permissions: List[str] = payload.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return payload

    return wrapper
