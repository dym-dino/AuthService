"""
Token Request

Defines a Pydantic model for token authentication requests.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES


from typing import Optional

from pydantic import BaseModel


# --------------------------------------------------------------------------------
# DATA MODELS

class TokenRequest(BaseModel):
    """
    Model representing a token request for authentication.

    Attributes:
        secret_hash (str): A secret hash used for authentication.
        role (str): The user's role, e.g., "admin" or "operator".
        login (Optional[str]): The login identifier for the user, if applicable.
        password (Optional[str]): The user's password, if applicable.
    """
    secret_hash: str
    role: str
    login: Optional[str] = None
    password: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str
