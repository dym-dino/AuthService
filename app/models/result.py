"""
Uniform Response

Defines a Pydantic model for uniform requests response.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from typing import Any

from pydantic import BaseModel


# --------------------------------------------------------------------------------
# DATA MODELS


class UniformResponse(BaseModel):
    """
    Uniform API response structure.

    Attributes:
        status_code (int): HTTP status code of the response (default is 200).
        result (str): A message describing the outcome of the operation.
        data (Any): Additional data returned by the API.
    """
    status_code: int = 200
    result: str
    data: Any
