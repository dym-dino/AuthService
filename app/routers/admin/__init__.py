"""
Admin Router

Configures the FastAPI router with admin token verification dependency and includes texts and users routes.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi import APIRouter, Depends

from . import users
from ...utils.auth.jwt_handler import verify_token

# --------------------------------------------------------------------------------
# ROUTER CONFIGURATION

router = APIRouter(
    dependencies=[Depends(verify_token)]
)

# --------------------------------------------------------------------------------
# INCLUDE SUB-ROUTERS

router.include_router(users.router)
