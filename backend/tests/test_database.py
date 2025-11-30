"""
Tests for database models and initialization.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import init_database, get_db, User, Session as SessionModel, Base
import backend.database


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Use in-memory SQLite for testing
    init_database("sqlite:///:memory:")
    
    # Get a database session
    db = next(get_db())
    
    yield db
    
    # Cleanup
    db.close()
    if backend.database.engine:
        Base.metadata.drop_all(bind=backend.database.engine)


def test_database_initialization():
    """Test that database initializes correctly."""
    init_database("sqlite:///:memory:")
    assert backend.database.engine is not None
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(backend.database.engine)
    tables = inspector.get_table_names()
    
    assert "users" in tables
    assert "sessions" in tables


def test_user_model_creation(test_db: Session):
    """Test creating a user in the database."""
    user = User(
        username="testuser",
        password_hash="hashed_password_here",
        created_at=datetime.utcnow()
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.password_hash == "hashed_password_here"
    assert user.created_at is not None
    assert user.last_login is None


def test_user_unique_username(test_db: Session):
    """Test that usernames must be unique."""
    user1 = User(username="testuser", password_hash="hash1")
    test_db.add(user1)
    test_db.commit()
    
    # Try to create another user with same username
    user2 = User(username="testuser", password_hash="hash2")
    test_db.add(user2)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        test_db.commit()


def test_session_model_creation(test_db: Session):
    """Test creating a session in the database."""
    # First create a user
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create a session for the user
    session = SessionModel(
        user_id=user.id,
        token="test_jwt_token_here",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    
    assert session.id is not None
    assert session.user_id == user.id
    assert session.token == "test_jwt_token_here"
    assert session.created_at is not None
    assert session.expires_at is not None


def test_session_unique_token(test_db: Session):
    """Test that session tokens must be unique."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    session1 = SessionModel(
        user_id=user.id,
        token="same_token",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db.add(session1)
    test_db.commit()
    
    # Try to create another session with same token
    session2 = SessionModel(
        user_id=user.id,
        token="same_token",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db.add(session2)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        test_db.commit()


def test_user_session_relationship(test_db: Session):
    """Test the relationship between User and Session models."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create multiple sessions for the user
    session1 = SessionModel(
        user_id=user.id,
        token="token1",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    session2 = SessionModel(
        user_id=user.id,
        token="token2",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    test_db.add(session1)
    test_db.add(session2)
    test_db.commit()
    
    # Refresh user to load relationships
    test_db.refresh(user)
    
    # Verify relationship
    assert len(user.sessions) == 2
    assert session1 in user.sessions
    assert session2 in user.sessions


def test_username_index_exists():
    """Test that username index exists for fast lookups."""
    init_database("sqlite:///:memory:")
    
    from sqlalchemy import inspect
    inspector = inspect(backend.database.engine)
    indexes = inspector.get_indexes("users")
    
    # Check if username index exists
    index_names = [idx['name'] for idx in indexes]
    assert 'idx_username' in index_names


def test_token_index_exists():
    """Test that token index exists for fast lookups."""
    init_database("sqlite:///:memory:")
    
    from sqlalchemy import inspect
    inspector = inspect(backend.database.engine)
    indexes = inspector.get_indexes("sessions")
    
    # Check if token index exists
    index_names = [idx['name'] for idx in indexes]
    assert 'idx_token' in index_names
