"""
Tests for authentication service.

This module tests the AuthService functionality including:
- Password hashing and verification
- Username and password validation
- JWT token generation and validation
- User registration and authentication
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, User
from backend.auth.service import AuthService


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def auth_service(db_session):
    """Create an AuthService instance with test database."""
    return AuthService(db_session)


def test_password_hashing(auth_service):
    """Test that passwords are hashed and can be verified."""
    password = "testpass123"
    hashed = auth_service.hash_password(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Should verify correctly
    assert auth_service.verify_password(password, hashed)
    
    # Should not verify with wrong password
    assert not auth_service.verify_password("wrongpass", hashed)


def test_username_validation_length(auth_service):
    """Test username length validation."""
    # Valid usernames (3-20 characters)
    valid, error = auth_service.validate_username("abc")
    assert valid is True
    assert error is None
    
    valid, error = auth_service.validate_username("a" * 20)
    assert valid is True
    assert error is None
    
    # Invalid: too short
    valid, error = auth_service.validate_username("ab")
    assert valid is False
    assert "at least 3 characters" in error
    
    # Invalid: too long
    valid, error = auth_service.validate_username("a" * 21)
    assert valid is False
    assert "at most 20 characters" in error


def test_username_validation_uniqueness(auth_service, db_session):
    """Test username uniqueness validation."""
    # Create a user
    user = User(username="testuser", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Try to validate same username
    valid, error = auth_service.validate_username("testuser")
    assert valid is False
    assert "already taken" in error
    
    # Different username should be valid
    valid, error = auth_service.validate_username("newuser")
    assert valid is True
    assert error is None


def test_password_validation(auth_service):
    """Test password validation."""
    # Valid password (8+ characters)
    valid, error = auth_service.validate_password("12345678")
    assert valid is True
    assert error is None
    
    # Invalid: too short
    valid, error = auth_service.validate_password("1234567")
    assert valid is False
    assert "at least 8 characters" in error


def test_jwt_token_generation(auth_service, db_session):
    """Test JWT token generation."""
    # Create a user
    user = User(username="testuser", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Generate token
    token = auth_service.create_jwt_token(user)
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_validation(auth_service, db_session):
    """Test JWT token validation."""
    # Create a user
    user = User(username="testuser", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Generate and validate token
    token = auth_service.create_jwt_token(user)
    payload = auth_service.validate_jwt_token(token)
    
    assert payload is not None
    assert payload["user_id"] == user.id
    assert payload["username"] == user.username
    assert "exp" in payload
    
    # Invalid token should return None
    invalid_payload = auth_service.validate_jwt_token("invalid.token.here")
    assert invalid_payload is None


def test_user_registration_success(auth_service):
    """Test successful user registration."""
    user, error = auth_service.register_user("testuser", "password123")
    
    assert user is not None
    assert error is None
    assert user.username == "testuser"
    assert user.password_hash != "password123"  # Should be hashed
    assert user.created_at is not None


def test_user_registration_invalid_username(auth_service):
    """Test user registration with invalid username."""
    # Too short
    user, error = auth_service.register_user("ab", "password123")
    assert user is None
    assert "at least 3 characters" in error


def test_user_registration_invalid_password(auth_service):
    """Test user registration with invalid password."""
    # Too short
    user, error = auth_service.register_user("testuser", "pass")
    assert user is None
    assert "at least 8 characters" in error


def test_user_registration_duplicate_username(auth_service):
    """Test user registration with duplicate username."""
    # Register first user
    user1, error1 = auth_service.register_user("testuser", "password123")
    assert user1 is not None
    
    # Try to register with same username
    user2, error2 = auth_service.register_user("testuser", "password456")
    assert user2 is None
    assert "already taken" in error2


def test_user_authentication_success(auth_service):
    """Test successful user authentication."""
    # Register user
    user, _ = auth_service.register_user("testuser", "password123")
    assert user is not None
    
    # Authenticate
    auth_user = auth_service.authenticate_user("testuser", "password123")
    assert auth_user is not None
    assert auth_user.username == "testuser"
    assert auth_user.last_login is not None


def test_user_authentication_wrong_password(auth_service):
    """Test authentication with wrong password."""
    # Register user
    user, _ = auth_service.register_user("testuser", "password123")
    assert user is not None
    
    # Try to authenticate with wrong password
    auth_user = auth_service.authenticate_user("testuser", "wrongpassword")
    assert auth_user is None


def test_user_authentication_nonexistent_user(auth_service):
    """Test authentication with nonexistent user."""
    auth_user = auth_service.authenticate_user("nonexistent", "password123")
    assert auth_user is None


def test_create_session(auth_service, db_session):
    """Test session creation."""
    # Register user
    user, _ = auth_service.register_user("testuser", "password123")
    assert user is not None
    
    # Create session
    token = auth_service.create_session(user)
    assert token is not None
    assert isinstance(token, str)
    
    # Verify session was stored in database
    from backend.database import Session as SessionModel
    session = db_session.query(SessionModel).filter(SessionModel.token == token).first()
    assert session is not None
    assert session.user_id == user.id


def test_get_user_from_token(auth_service):
    """Test getting user from JWT token."""
    # Register user
    user, _ = auth_service.register_user("testuser", "password123")
    assert user is not None
    
    # Create session
    token = auth_service.create_session(user)
    
    # Get user from token
    retrieved_user = auth_service.get_user_from_token(token)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.username == user.username
    
    # Invalid token should return None
    invalid_user = auth_service.get_user_from_token("invalid.token.here")
    assert invalid_user is None
