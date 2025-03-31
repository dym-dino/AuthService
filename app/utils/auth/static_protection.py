"""
Static protections

Secured code docs route with login and password
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from app.utils.auth.swagger_auth import get_swagger_basic_auth

# --------------------------------------------------------------------------------
# CONFIGURATION

security = HTTPBasic()


# --------------------------------------------------------------------------------
# MAIN LOGIC

class ProtectedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        request = Request(scope)
        try:
            credentials: HTTPBasicCredentials = await security(request)
            _ = get_swagger_basic_auth(credentials)
        except HTTPException as exc:
            headers = exc.headers or {"WWW-Authenticate": "Basic"}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers=headers
            ) from exc
        return await super().get_response(path, scope)
