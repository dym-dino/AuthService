"""
Swagger Auth

Module for protecting access to Swagger documentation using HTTP Basic authentication.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import secrets

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings

# --------------------------------------------------------------------------------
# CONFIGURATION

security = HTTPBasic()


# --------------------------------------------------------------------------------
# DEPENDENCIES

def get_swagger_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Dependency for HTTP Basic authentication to access Swagger documentation.

    Args:
        credentials (HTTPBasicCredentials): User-provided credentials.

    Returns:
        str: The authenticated username.

    Raises:
        HTTPException: If the provided credentials are invalid.
    """

    is_correct_username: bool = secrets.compare_digest(credentials.username, settings.ADMIN_SWAGGER_LOGIN)
    is_correct_password: bool = secrets.compare_digest(credentials.password, settings.ADMIN_SWAGGER_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials for documentation access"
        )
    return credentials.username
