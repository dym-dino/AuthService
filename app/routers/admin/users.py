"""
User Router

Handles creation, deletion, and listing of user accounts.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import user as models
from app.models.user import UserCreate
from app.models.user import UserInDB
from app.utils.auth.hash import hash_str
from app.utils.auth.jwt_handler import require_permission
from app.utils.base_handler import base_handler

# --------------------------------------------------------------------------------
# ROUTER CONFIGURATION

router = APIRouter(tags=["Users"])


# --------------------------------------------------------------------------------
# ENDPOINTS

@router.post(
    "/create_user",
    openapi_extra={
        "examples": {
            "create_example": {
                "summary": "Create a user",
                "description": "Registers a new user with a role and optional permissions.",
                "value": {
                    "login": "newuser",
                    "password": "securepassword",
                    "role": "user",
                    "permissions": ["read_docs"]
                }
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/admin/create_user'\n"
                        "headers = {'Authorization': f'Bearer <admin_token>'}\n"
                        "payload = {\n"
                        "    'login': 'newuser',\n"
                        "    'password': 'securepassword',\n"
                        "    'role': 'user',\n"
                        "    'permissions': ['read_docs']\n"
                        "}\n"
                        "response = requests.post(url, json=payload, headers=headers)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "User created successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": "77fa525c-7d8f-43da-af7a-a2550ff48e3c",
                            "login": "newuser",
                            "role": "user",
                            "password": "***",
                            "permissions": ["read_docs"]
                        }
                    }
                }
            }
        }
    }
)
@base_handler
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - Checks for login uniqueness.
    - Hashes the password.
    - Accepts custom roles and permissions.

    Returns a sanitized version of the created user object (without real password).
    """
    existing = db.query(models.User).filter(models.User.login == user_data.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="Login already exists")

    hashed_pass = hash_str(user_data.password)
    new_user = models.User(
        login=user_data.login,
        password=hashed_pass,
        role=user_data.role,
        permissions=user_data.permissions
    )
    db.add(new_user)
    db.commit()
    return UserInDB(id=str(new_user.id), login=new_user.login, role=new_user.role, password="***")


@router.put(
    "/update_permissions/{user_id}",
    openapi_extra={
        "examples": {
            "update_permissions_example": {
                "summary": "Update user permissions",
                "description": "Updates the list of permissions for a user by their UUID.",
                "value": {
                    "permissions": ["manage_users", "read_docs"]
                }
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/admin/update_permissions/77fa525c-7d8f-43da-af7a-a2550ff48e3c'\n"
                        "headers = {'Authorization': f'Bearer <admin_token>'}\n"
                        "payload = {'permissions': ['manage_users', 'read_docs']}\n"
                        "response = requests.put(url, json=payload, headers=headers)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "Permissions updated",
                "content": {
                    "application/json": {
                        "example": {
                            "id": "77fa525c-7d8f-43da-af7a-a2550ff48e3c",
                            "login": "someuser",
                            "role": "user",
                            "password": "***",
                            "permissions": ["manage_users", "read_docs"]
                        }
                    }
                }
            },
            "404": {
                "description": "User not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "User not found"}
                    }
                }
            }
        }
    }
)
@base_handler
async def update_permissions(
        user_id: str,
        payload: dict,
        db: Session = Depends(get_db)
):
    """
    Update permissions for an existing user.

    - Requires the user ID.
    - Expects a JSON body with a list of `permissions`.
    - Returns updated user info without real password.
    """
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.permissions = payload.get("permissions", [])
    db.commit()

    return UserInDB(
        id=str(user.id),
        login=user.login,
        role=user.role,
        password="***",
        permissions=user.permissions
    )


@router.delete(
    "/remove_user/{user_id}",
    openapi_extra={
        "examples": {
            "delete_example": {
                "summary": "Delete a user",
                "description": "Deletes a user account by UUID.",
                "value": "77fa525c-7d8f-43da-af7a-a2550ff48e3c"
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/admin/remove_user/77fa525c-7d8f-43da-af7a-a2550ff48e3c'\n"
                        "headers = {'Authorization': f'Bearer <admin_token>'}\n"
                        "response = requests.delete(url, headers=headers)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "User deleted successfully",
                "content": {
                    "application/json": {
                        "example": {"message": "User removed"}
                    }
                }
            },
            "404": {
                "description": "User not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "User not found"}
                    }
                }
            }
        }
    }
)
@base_handler
async def remove_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete an existing user by their unique ID.

    - Returns a 404 error if user doesn't exist.
    - Requires admin or operator rights.

    Returns success message on deletion.
    """
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User removed"}


@router.get(
    "/users",
    response_model=List[UserInDB],
    dependencies=[Depends(require_permission("view_users"))],
    openapi_extra={
        "examples": {
            "get_users_example": {
                "summary": "List users",
                "description": "Returns a paginated list of users, filtered by search or role.",
                "value": [
                    {
                        "id": "a1b2c3d4",
                        "login": "john_doe",
                        "role": "user",
                        "password": "***",
                        "permissions": ["read_docs"]
                    }
                ]
            }
        },
        "x-code-samples": [
            {
                "lang": "Python",
                "source": (
                        "import requests\n\n"
                        "url = 'http://localhost:8000/api/v1/admin/users'\n"
                        "params = {'limit': 5, 'offset': 0, 'search': 'john'}\n"
                        "headers = {'Authorization': f'Bearer <admin_token>'}\n"
                        "response = requests.get(url, params=params, headers=headers)\n"
                        "print(response.json())"
                )
            }
        ],
        "responses": {
            "200": {
                "description": "Successful user list retrieval",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": "a1b2c3d4",
                                "login": "john_doe",
                                "role": "user",
                                "password": "***",
                                "permissions": ["read_docs"]
                            }
                        ]
                    }
                }
            }
        }
    }
)
@base_handler
def get_users(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        search: Optional[str] = Query(None, description="Search substring in login"),
        role: Optional[str] = Query(None, description="Filter by user role")
):
    """
    Retrieve a paginated list of users.

    - Supports filtering by login (partial match) and user role.
    - Requires the "view_users" permission.
    - Returns up to 100 users per page.
    """
    query = db.query(models.User)

    if search:
        query = query.filter(models.User.login.ilike(f"%{search}%"))
    if role:
        query = query.filter(models.User.role == role)

    users = query.order_by(models.User.login).offset(offset).limit(limit).all()

    return [
        UserInDB(
            id=str(u.id),
            login=u.login,
            role=u.role,
            password="***",
            permissions=u.permissions if hasattr(u, "permissions") else []
        )
        for u in users
    ]
