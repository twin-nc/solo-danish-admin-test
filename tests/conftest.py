import os
import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import settings
# Load .env so DATABASE_URL is available via os.environ before any app import.
load_dotenv()

from app.db.session import get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models.base import Base  # noqa: E402

# Import models so SQLAlchemy registers them with Base.metadata
import app.models.party  # noqa: F401, E402
import app.models.party_role  # noqa: F401, E402
import app.models.user  # noqa: F401, E402
from app.repositories.user import UserRepository  # noqa: E402

# Derive URLs from the DATABASE_URL env var so no credentials are hardcoded.
# DATABASE_URL points at the main DB; swap the database name for the test DB.
_base_url = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = re.sub(r"/[^/]+$", "/vatri_test_db", _base_url)
ADMIN_URL = re.sub(r"/[^/]+$", "/postgres", _base_url)


@pytest.fixture(scope="session")
def test_engine():
    """Create the test database and all tables once per session."""
    # Create the database if it doesn't exist
    admin_engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'vatri_test_db'")
        ).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE vatri_test_db"))
    admin_engine.dispose()

    # Create tables
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(test_engine):
    """
    Wrap each test in a transaction that is rolled back afterwards.

    Uses join_transaction_mode="create_savepoint" so that db.commit() calls
    inside the repository only release a savepoint, leaving the outer
    transaction uncommitted and available for rollback.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """TestClient with get_db overridden to use the test session."""

    def override_get_db():
        yield db

    fastapi_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def admin_credentials(db):
    """Create an ADMIN user that can authenticate against protected routes."""
    email = f"admin-{uuid.uuid4()}@example.com"
    repo = UserRepository()
    user = repo.create_user(
        email=email,
        hashed_password="not-used-in-these-tests",
        role="ADMIN",
        party_id=None,
        db=db,
    )
    return user


@pytest.fixture
def authenticated_client(client, admin_credentials):
    """Return a logged-in client with auth cookies set."""
    access_payload = {
        "sub": str(admin_credentials.id),
        "role": admin_credentials.role,
        "token_type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    client.cookies.set("access_token", access_token)
    assert client.cookies.get("access_token")
    return client
