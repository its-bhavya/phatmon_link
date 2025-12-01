"""
Tests for main FastAPI application endpoints.

This module tests:
- Registration endpoint
- Login endpoint
- Error handling for duplicate usernames
- Error handling for validation failures
- Failed login attempt tracking
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

from backend.main import failed_login_attempts
from backend.database import Base, get_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import all the components from main
from backend.main import (
    RegisterRequest, LoginRequest, UserResponse, AuthResponse, ErrorResponse,
    get_client_ip, check_failed_attempts, record_failed_attempt, clear_failed_attempts,
    root, register, login
)


# Create test database with shared cache to ensure same database across connections
TEST_DATABASE_URL = "sqlite:///:memory:?cache=shared"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Use StaticPool to maintain single connection
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Create a test app with custom lifespan that uses test database
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """App lifespan - initializes services only (database managed by fixtures)."""
    # Initialize services
    from backend.rooms.service import RoomService
    from backend.websocket.manager import WebSocketManager
    from backend.commands.handler import CommandHandler
    
    app.state.room_service = RoomService()
    app.state.room_service.create_default_rooms()
    app.state.websocket_manager = WebSocketManager()
    app.state.command_handler = CommandHandler(
        app.state.room_service,
        app.state.websocket_manager
    )
    
    yield
    
    # No cleanup needed - handled by fixtures


# Create test app
app = FastAPI(
    title="Phantom Link BBS - Test",
    description="Test instance",
    version="1.0.0",
    lifespan=app_lifespan
)

# Add CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.get("/")(root)
app.post("/api/auth/register", response_model=AuthResponse, status_code=201)(register)
app.post("/api/auth/login", response_model=AuthResponse)(login)

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client for each test."""
    # Create tables in test database BEFORE creating the client
    Base.metadata.create_all(bind=engine)
    
    try:
        # Use raise_server_exceptions=True to see actual errors during development
        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client
    finally:
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)
        # Clear failed login attempts
        failed_login_attempts.clear()


def test_root_endpoint(client):
    """Test root endpoint serves index.html."""
    response = client.get("/")
    assert response.status_code == 200
    # Root now serves HTML file, not JSON
    assert response.headers["content-type"].startswith("text/html")


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    if response.status_code != 201:
        print(f"Error response: {response.json()}")
    
    assert response.status_code == 201
    data = response.json()
    
    # Check response structure
    assert "token" in data
    assert "user" in data
    assert "message" in data
    
    # Check user data
    assert data["user"]["username"] == "testuser"
    assert "id" in data["user"]
    assert "created_at" in data["user"]
    
    # Check welcome message
    assert "Welcome" in data["message"]
    assert "testuser" in data["message"]


def test_register_duplicate_username(client):
    """Test registration with duplicate username returns error."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "anotherpass123"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already taken" in data["detail"].lower()


def test_register_username_too_short(client):
    """Test registration with username too short."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "ab",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_register_username_too_long(client):
    """Test registration with username too long."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "a" * 21,
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_register_password_too_short(client):
    """Test registration with password too short."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "short"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_login_success(client):
    """Test successful login."""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Now login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "token" in data
    assert "user" in data
    assert "message" in data
    
    # Check user data
    assert data["user"]["username"] == "testuser"
    assert data["user"]["last_login"] is not None
    
    # Check welcome message includes last login
    assert "Welcome" in data["message"]


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    # Register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["detail"]
    assert "attempt" in data["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent username."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["detail"]


def test_login_failed_attempts_tracking(client):
    """Test that failed login attempts are tracked and limited to 3."""
    # Register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Attempt 1 - should fail with 2 remaining
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong1"
        }
    )
    assert response.status_code == 401
    assert "2 attempt(s) remaining" in response.json()["detail"]
    
    # Attempt 2 - should fail with 1 remaining
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong2"
        }
    )
    assert response.status_code == 401
    assert "1 attempt(s) remaining" in response.json()["detail"]
    
    # Attempt 3 - should fail with 0 remaining
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong3"
        }
    )
    assert response.status_code == 429
    assert "Maximum login attempts exceeded" in response.json()["detail"]
    
    # Attempt 4 - should be blocked immediately
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong4"
        }
    )
    assert response.status_code == 429


def test_login_clears_failed_attempts_on_success(client):
    """Test that successful login clears failed attempt counter."""
    # Register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Make 2 failed attempts
    client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong1"
        }
    )
    client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong2"
        }
    )
    
    # Now login successfully
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    
    # Make another failed attempt - should start from 3 attempts again
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
    assert "2 attempt(s) remaining" in response.json()["detail"]


def test_register_clears_failed_attempts(client):
    """Test that successful registration clears failed attempt counter."""
    # Make some failed login attempts
    for i in range(2):
        client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": f"wrong{i}"
            }
        )
    
    # Now register successfully
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    
    # Make a failed login attempt - should start from 3 attempts
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
    assert "2 attempt(s) remaining" in response.json()["detail"]
