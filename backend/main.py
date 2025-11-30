"""
Phantom Link BBS - Main FastAPI Application

This module provides the main FastAPI application with:
- Authentication HTTP endpoints (register, login)
- Request/response models using Pydantic
- Error handling for validation and duplicate usernames
- Failed login attempt tracking
"""

from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session
import os

from backend.database import init_database, get_db, close_database
from backend.auth.service import AuthService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    database_url = os.getenv("DATABASE_URL", "sqlite:///./phantom_link.db")
    init_database(database_url)
    print(f"Database initialized: {database_url}")
    
    yield
    
    # Shutdown
    close_database()
    print("Database connection closed")


# Initialize FastAPI app
app = FastAPI(
    title="Phantom Link BBS",
    description="A modern reimagining of 1980s BBS with retro terminal aesthetics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track failed login attempts per connection
# Key: client IP address, Value: number of failed attempts
failed_login_attempts = {}


# Pydantic Models for Request/Response

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=20, description="Username (3-20 characters)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    
    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v):
        """Validate username format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username cannot be empty")
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_format(cls, v):
        """Validate password format."""
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Response model for user information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthResponse(BaseModel):
    """Response model for authentication (register/login)."""
    token: str
    user: UserResponse
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response model for errors."""
    detail: str


# Helper Functions

def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address as string
    """
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Fall back to direct client IP
    return request.client.host if request.client else "unknown"


def check_failed_attempts(client_ip: str) -> None:
    """
    Check if client has exceeded maximum failed login attempts.
    
    Args:
        client_ip: Client IP address
        
    Raises:
        HTTPException: If client has exceeded 3 failed attempts
    """
    attempts = failed_login_attempts.get(client_ip, 0)
    if attempts >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum login attempts exceeded. Please reconnect to try again."
        )


def record_failed_attempt(client_ip: str) -> None:
    """
    Record a failed login attempt for a client.
    
    Args:
        client_ip: Client IP address
    """
    failed_login_attempts[client_ip] = failed_login_attempts.get(client_ip, 0) + 1


def clear_failed_attempts(client_ip: str) -> None:
    """
    Clear failed login attempts for a client after successful login.
    
    Args:
        client_ip: Client IP address
    """
    if client_ip in failed_login_attempts:
        del failed_login_attempts[client_ip]


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "Phantom Link BBS",
        "status": "online",
        "version": "1.0.0"
    }


@app.post(
    "/api/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or username taken"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    This endpoint:
    1. Validates username (3-20 characters, unique)
    2. Validates password (minimum 8 characters)
    3. Creates user account with hashed password
    4. Automatically logs the user in
    5. Returns JWT token and user information
    
    Requirements: 1.4, 1.5, 1.6, 1.7
    """
    auth_service = AuthService(db)
    
    # Register user
    user, error = auth_service.register_user(
        username=register_data.username,
        password=register_data.password
    )
    
    if error:
        # Check if it's a duplicate username error
        if "already taken" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        # Other validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Create session and generate token
    token = auth_service.create_session(user)
    
    # Clear any failed login attempts for this client
    client_ip = get_client_ip(request)
    clear_failed_attempts(client_ip)
    
    return AuthResponse(
        token=token,
        user=UserResponse.from_orm(user),
        message=f"Welcome to Phantom Link BBS, {user.username}!"
    )


@app.post(
    "/api/auth/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Too many failed attempts"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and create a session.
    
    This endpoint:
    1. Validates credentials
    2. Tracks failed login attempts (max 3 per connection)
    3. Updates last login time on success
    4. Returns JWT token and user information with last login time
    
    Requirements: 2.2, 2.3, 2.4, 2.5
    """
    client_ip = get_client_ip(request)
    
    # Check if client has exceeded maximum failed attempts
    check_failed_attempts(client_ip)
    
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password
    )
    
    if not user:
        # Record failed attempt
        record_failed_attempt(client_ip)
        
        # Get current attempt count
        attempts = failed_login_attempts.get(client_ip, 0)
        remaining = 3 - attempts
        
        if remaining > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid credentials. {remaining} attempt(s) remaining."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum login attempts exceeded. Please reconnect to try again."
            )
    
    # Clear failed attempts on successful login
    clear_failed_attempts(client_ip)
    
    # Create session and generate token
    token = auth_service.create_session(user)
    
    # Format welcome message with last login time
    if user.last_login:
        last_login_str = user.last_login.strftime("%Y-%m-%d %H:%M:%S UTC")
        welcome_message = f"Welcome back, {user.username}! Last login: {last_login_str}"
    else:
        welcome_message = f"Welcome to Phantom Link BBS, {user.username}!"
    
    return AuthResponse(
        token=token,
        user=UserResponse.from_orm(user),
        message=welcome_message
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
