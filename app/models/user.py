"""
Users Models

Defines SQLAlchemy and Pydantic models for  users entities.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from typing import Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


# --------------------------------------------------------------------------------
# SQLALCHEMY MODEL

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    permissions = Column(ARRAY(String), default=list)


# --------------------------------------------------------------------------------
# PYDANTIC MODELS

class UsersBase(BaseModel):
    login: str
    password: str
    role: str
    permissions: List[str] = Field(default_factory=list)


class UserCreate(UsersBase):
    pass


class UserInDB(UsersBase):
    id: Optional[str] = Field(default=None)
