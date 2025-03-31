"""
Test setup for FastAPI application using PostgreSQL.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.utils.auth.jwt_handler import create_access_token

# --------------------------------------------------------------------------------
# FIXTURE: Test Database

settings.TESTING = True

engine = create_engine(settings.POSTGRES_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def override_get_db(db):
    app.dependency_overrides[get_db] = lambda: db
    yield
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------------
# FIXTURE: Client

@pytest.fixture
def client(override_get_db):
    with TestClient(app) as c:
        yield c


# --------------------------------------------------------------------------------
# FIXTURE: Access Tokens

@pytest.fixture
def admin_token():
    return create_access_token({"sub": "testadmin", "role": "admin", "permissions": ["create_user", "view_users"]})


@pytest.fixture
def user_token():
    return create_access_token({"sub": "testuser", "role": "user", "permissions": []})
