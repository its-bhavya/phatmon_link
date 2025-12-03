"""
Phantom Link BBS - Main FastAPI Application

This module provides the main FastAPI application with:
- Authentication HTTP endpoints (register, login)
- Request/response models using Pydantic
- Error handling for validation and duplicate usernames
- Failed login attempt tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session
import os
import asyncio

from backend.database import init_database, get_db, close_database
from backend.auth.service import AuthService
from backend.websocket.manager import WebSocketManager
from backend.rooms.service import RoomService
from backend.commands.handler import CommandHandler
from backend.rate_limiter import RateLimiter
from backend.config import get_config
from backend.vecna.auto_router import on_message_hook
from backend.vecna.gemini_service import GeminiService, GeminiServiceError
from backend.sysop.brain import SysOpBrain
from backend.vecna.module import VecnaModule, TriggerType
from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.user_profile import UserProfileService
from backend.vecna.rate_limiter import VecnaRateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    config = get_config()
    init_database(config.DATABASE_URL)
    print(f"Database initialized: {config.DATABASE_URL}")
    
    # Initialize room service and create default rooms
    app.state.room_service = RoomService()
    app.state.room_service.create_default_rooms()
    print("Default rooms created")
    
    # Initialize WebSocket manager
    app.state.websocket_manager = WebSocketManager()
    print("WebSocket manager initialized")
    
    # Initialize command handler
    app.state.command_handler = CommandHandler(
        app.state.room_service,
        app.state.websocket_manager
    )
    print("Command handler initialized")
    
    # Initialize rate limiter
    app.state.rate_limiter = RateLimiter(
        message_limit=10,
        message_window=10,
        command_limit=5,
        command_window=5,
        mute_duration=30
    )
    print("Rate limiter initialized")
    
    # Initialize Gemini service for auto-routing (if enabled)
    if config.VECNA_ENABLED and config.GEMINI_API_KEY:
        try:
            app.state.gemini_service = GeminiService(
                api_key=config.GEMINI_API_KEY,
                model=config.GEMINI_MODEL,
                temperature=config.GEMINI_TEMPERATURE,
                max_tokens=config.GEMINI_MAX_TOKENS
            )
            print("Gemini service initialized for auto-routing")
            
            # Initialize SysOp Brain
            app.state.sysop_brain = SysOpBrain(
                gemini_service=app.state.gemini_service,
                room_service=app.state.room_service
            )
            print("SysOp Brain initialized")
            
            # Initialize Vecna Module components
            app.state.sentiment_analyzer = SentimentAnalyzer()
            
            # Note: VecnaRateLimiter will be initialized per-request with database session
            # Store configuration for later use
            app.state.vecna_rate_limiter_config = {
                'max_activations_per_hour': config.VECNA_MAX_ACTIVATIONS_PER_HOUR,
                'cooldown_seconds': config.VECNA_COOLDOWN_SECONDS,
                'enabled': config.VECNA_ENABLED
            }
            
            app.state.vecna_module = VecnaModule(
                gemini_service=app.state.gemini_service,
                sentiment_analyzer=app.state.sentiment_analyzer,
                rate_limiter=None  # Will be set per-request
            )
            print("Vecna Module initialized")
            
        except GeminiServiceError as e:
            print(f"Warning: Gemini service initialization failed: {e}")
            app.state.gemini_service = None
            app.state.sysop_brain = None
            app.state.vecna_module = None
    else:
        app.state.gemini_service = None
        app.state.sysop_brain = None
        app.state.vecna_module = None
        print("Gemini service disabled (VECNA_ENABLED=false or no API key)")
    
    # Start session cleanup task
    cleanup_task = asyncio.create_task(cleanup_expired_sessions(app))
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    close_database()
    print("Database connection closed")


# Initialize FastAPI app
app = FastAPI(
    title="Gatekeeper BBS",
    description="A modern reimagining of 1980s BBS with retro terminal aesthetics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
config = get_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
# Mount individual directories for direct access
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

# Mount /static route for general static file serving
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Track failed login attempts per connection
# Key: client IP address, Value: number of failed attempts
failed_login_attempts = {}

# Track disconnected user sessions for reconnection
# Key: username, Value: dict with room, disconnected_at timestamp
disconnected_sessions: Dict[str, dict] = {}

# Session preservation timeout (30 seconds)
SESSION_PRESERVATION_TIMEOUT = 30


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
    """
    Serve the main terminal interface as the entry point.
    
    Requirements: All (infrastructure)
    """
    return FileResponse("frontend/index.html")


@app.get("/auth")
async def auth():
    """
    Serve the authentication page at /auth path.
    
    Requirements: All (infrastructure)
    """
    return FileResponse("frontend/auth.html")


@app.get("/auth.html")
async def auth_html():
    """
    Serve the authentication page at /auth.html path.
    
    Requirements: All (infrastructure)
    """
    return FileResponse("frontend/auth.html")


@app.get("/index.html")
async def index():
    """
    Serve the main terminal interface.
    
    Requirements: All (infrastructure)
    """
    return FileResponse("frontend/index.html")


@app.get("/index.html")
async def index():
    """
    Serve the main chat interface page.
    
    Requirements: All (infrastructure)
    """
    return FileResponse("frontend/index.html")


@app.get("/api")
async def api_root():
    """API health check endpoint."""
    return {
        "service": "Gatekeeper",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/api/admin/vecna/status")
async def get_vecna_status():
    """
    Get Vecna system status (admin endpoint).
    
    Returns:
        Dictionary with Vecna enabled status and configuration
    """
    config = get_config()
    
    return {
        "enabled": config.VECNA_ENABLED,
        "max_activations_per_hour": config.VECNA_MAX_ACTIVATIONS_PER_HOUR,
        "cooldown_seconds": config.VECNA_COOLDOWN_SECONDS,
        "emotional_threshold": config.VECNA_EMOTIONAL_THRESHOLD
    }


class VecnaControlRequest(BaseModel):
    """Request model for Vecna control."""
    enabled: bool = Field(..., description="Whether Vecna should be enabled")


@app.post("/api/admin/vecna/control")
async def control_vecna(
    control_data: VecnaControlRequest,
    db: Session = Depends(get_db)
):
    """
    Control Vecna global enabled status (admin endpoint).
    
    This endpoint allows administrators to enable or disable Vecna globally.
    
    Args:
        control_data: Request with enabled status
        db: Database session
    
    Returns:
        Dictionary with updated status
    
    Requirements: Security considerations
    """
    # Update global configuration
    config = get_config()
    config.VECNA_ENABLED = control_data.enabled
    
    # Update rate limiter config if it exists
    if hasattr(app.state, 'vecna_rate_limiter_config'):
        app.state.vecna_rate_limiter_config['enabled'] = control_data.enabled
    
    status_message = "enabled" if control_data.enabled else "disabled"
    logger.info(f"Vecna globally {status_message} by admin")
    
    return {
        "success": True,
        "enabled": control_data.enabled,
        "message": f"Vecna has been {status_message} globally"
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
        message=f"Welcome to Gatekeeper, {user.username}!"
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
        welcome_message = f"Welcome to Gatekeeper, {user.username}!"
    
    return AuthResponse(
        token=token,
        user=UserResponse.from_orm(user),
        message=welcome_message
    )


async def cleanup_expired_sessions(app: FastAPI):
    """
    Background task to clean up expired disconnected sessions.
    
    This task runs every 10 seconds and removes sessions that have been
    disconnected for more than SESSION_PRESERVATION_TIMEOUT seconds.
    
    Requirements: 8.5
    """
    while True:
        try:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            current_time = datetime.utcnow()
            expired_users = []
            
            # Find expired sessions
            for username, session_data in disconnected_sessions.items():
                disconnected_at = session_data.get("disconnected_at")
                if disconnected_at:
                    elapsed = (current_time - disconnected_at).total_seconds()
                    if elapsed > SESSION_PRESERVATION_TIMEOUT:
                        expired_users.append(username)
            
            # Remove expired sessions
            for username in expired_users:
                session_data = disconnected_sessions.pop(username, None)
                if session_data:
                    room = session_data.get("room")
                    print(f"Session expired for user {username} (was in {room})")
                    
                    # Remove from room service
                    if room:
                        # Create a temporary user object for cleanup
                        from backend.database import User
                        temp_user = User(username=username)
                        app.state.room_service.leave_room(temp_user, room)
                    
                    # Broadcast updated user list
                    active_users = app.state.websocket_manager.get_active_users()
                    await app.state.websocket_manager.broadcast_to_all({
                        "type": "user_list",
                        "users": active_users
                    })
                    
                    # Broadcast updated room list
                    rooms = app.state.room_service.get_rooms()
                    await app.state.websocket_manager.broadcast_to_all({
                        "type": "room_list",
                        "rooms": [
                            {
                                "name": room.name,
                                "count": app.state.room_service.get_room_count(room.name),
                                "description": room.description
                            }
                            for room in rooms
                        ]
                    })
        
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in session cleanup: {e}")


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat communication.
    
    This endpoint:
    1. Validates JWT token on connection
    2. Accepts WebSocket connection
    3. Places user in Lobby (or restores previous room if reconnecting)
    4. Sends welcome message
    5. Handles incoming messages (chat_message, command, join_room)
    6. Broadcasts messages to appropriate rooms
    7. Handles disconnection and session preservation
    8. Integrates Vecna and SysOp Brain for message processing
    
    Requirements: 4.2, 5.1, 5.2, 6.1, 6.2, 8.1, 8.3, 8.4, 8.5, 1.3, 6.1, 6.2, 6.3, 6.4, 6.5
    """
    auth_service = AuthService(db)
    user_profile_service = UserProfileService(db)
    user = None
    recent_messages = []  # Track recent messages for spam detection
    
    # Initialize Vecna rate limiter for this connection (if Vecna is enabled)
    vecna_rate_limiter = None
    if hasattr(app.state, 'vecna_rate_limiter_config'):
        vecna_rate_limiter = VecnaRateLimiter(
            db=db,
            **app.state.vecna_rate_limiter_config
        )
    
    try:
        # Validate token
        user = auth_service.get_user_from_token(token)
        if not user:
            print(f"WebSocket authentication failed for token: {token[:20]}...")
            # Accept connection first, then close with error
            await websocket.accept()
            await websocket.close(code=4001, reason="Invalid or expired token")
            return
        
        print(f"WebSocket authenticated user: {user.username}")
        
        # Check if user is reconnecting
        initial_room = "Lobby"
        is_reconnecting = False
        
        if user.username in disconnected_sessions:
            session_data = disconnected_sessions.pop(user.username)
            previous_room = session_data.get("room")
            disconnected_at = session_data.get("disconnected_at")
            
            # Check if within timeout period
            if disconnected_at:
                elapsed = (datetime.utcnow() - disconnected_at).total_seconds()
                if elapsed <= SESSION_PRESERVATION_TIMEOUT:
                    initial_room = previous_room
                    is_reconnecting = True
                    print(f"User {user.username} reconnecting to {initial_room}")
        
        # Connect user via WebSocket manager
        await app.state.websocket_manager.connect(websocket, user, initial_room)
        
        # Add user to room service
        app.state.room_service.join_room(user, initial_room)
        
        # Send welcome message
        if is_reconnecting:
            welcome_message = f"Welcome back, {user.username}! Reconnected to {initial_room}."
        else:
            if user.last_login:
                last_login_str = user.last_login.strftime("%Y-%m-%d %H:%M:%S UTC")
                welcome_message = f"Welcome to Gatekeeper, {user.username}! Last login: {last_login_str}"
            else:
                welcome_message = f"Welcome to Gatekeeper, {user.username}!"
        
        await app.state.websocket_manager.send_to_user(websocket, {
            "type": "system",
            "content": welcome_message
        })
        
        # Send room entry message
        room = app.state.room_service.get_room(initial_room)
        if room:
            await app.state.websocket_manager.send_to_user(websocket, {
                "type": "system",
                "content": f"\n=== {room.name} ===\n{room.description}\n"
            })
            
            # Send recent message history
            recent_messages = room.get_recent_messages(limit=20)
            if recent_messages:
                await app.state.websocket_manager.send_to_user(websocket, {
                    "type": "system",
                    "content": "--- Recent messages ---"
                })
                for msg in recent_messages:
                    await app.state.websocket_manager.send_to_user(websocket, msg)
        
        # Broadcast user join to room
        await app.state.websocket_manager.broadcast_to_room(
            initial_room,
            {
                "type": "system",
                "content": f"* {user.username} has entered the room"
            },
            exclude_websocket=websocket
        )
        
        # Broadcast updated active users list to all
        active_users = app.state.websocket_manager.get_active_users()
        await app.state.websocket_manager.broadcast_to_all({
            "type": "user_list",
            "users": active_users
        })
        
        # Send room list to the connected user (for side panel)
        rooms = app.state.room_service.get_rooms()
        await app.state.websocket_manager.send_to_user(websocket, {
            "type": "room_list",
            "rooms": [
                {
                    "name": room.name,
                    "count": app.state.room_service.get_room_count(room.name),
                    "description": room.description
                }
                for room in rooms
            ]
        })
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "chat_message":
                # Handle chat message
                content = data.get("content", "").strip()
                if not content:
                    continue
                
                # Check rate limit
                allowed, error_message, should_disconnect = app.state.rate_limiter.check_message_limit(user.username)
                
                if not allowed:
                    # Send error message to user
                    await app.state.websocket_manager.send_to_user(websocket, {
                        "type": "error",
                        "content": error_message
                    })
                    
                    # Disconnect if persistent abuse
                    if should_disconnect:
                        await websocket.close(code=1008, reason="Rate limit violation")
                        break
                    
                    continue
                
                # Get user's current room
                current_room = app.state.websocket_manager.get_user_room(user.username)
                if not current_room:
                    continue
                
                # Track recent messages for spam detection
                recent_messages.append((content, datetime.utcnow()))
                # Keep only last 10 messages
                recent_messages = recent_messages[-10:]
                
                # Update user profile with room visit and interests
                user_profile_service.record_room_visit(user.id, current_room)
                user_profile_service.update_interests(user.id, content)
                
                # Get user profile for Vecna and SysOp Brain
                user_profile = user_profile_service.get_profile(user.id)
                
                # Message Processing Pipeline: Vecna Check → Conditional Activation → SysOp Brain Routing
                vecna_activated = False
                
                # Step 1: Vecna trigger evaluation (if available)
                vecna_module = getattr(app.state, 'vecna_module', None)
                if vecna_module:
                    try:
                        # Attach rate limiter to vecna module for this request
                        vecna_module.rate_limiter = vecna_rate_limiter
                        
                        vecna_trigger = await vecna_module.evaluate_triggers(
                            user_id=user.id,
                            message=content,
                            user_profile=user_profile
                        )
                        
                        # Step 2: Conditional Vecna activation
                        if vecna_trigger:
                            vecna_activated = True
                            
                            if vecna_trigger.trigger_type == TriggerType.EMOTIONAL:
                                # Execute emotional trigger (Psychic Grip with cryptic narrative)
                                vecna_response = await vecna_module.execute_emotional_trigger(
                                    user_id=user.id,
                                    username=user.username,
                                    message=content,
                                    user_profile=user_profile
                                )
                                
                                # Send Vecna Psychic Grip message (emotional trigger)
                                await app.state.websocket_manager.send_to_user(websocket, {
                                    "type": "vecna_psychic_grip",
                                    "content": vecna_response.content,
                                    "freeze_duration": vecna_response.freeze_duration,
                                    "visual_effects": vecna_response.visual_effects,
                                    "timestamp": vecna_response.timestamp.isoformat()
                                })
                                
                            elif vecna_trigger.trigger_type == TriggerType.SYSTEM:
                                # Execute Psychic Grip (thread freeze + narrative)
                                vecna_response = await vecna_module.execute_psychic_grip(
                                    user_id=user.id,
                                    username=user.username,
                                    user_profile=user_profile
                                )
                                
                                # Send Vecna Psychic Grip message
                                await app.state.websocket_manager.send_to_user(websocket, {
                                    "type": "vecna_psychic_grip",
                                    "content": vecna_response.content,
                                    "freeze_duration": vecna_response.freeze_duration,
                                    "visual_effects": vecna_response.visual_effects,
                                    "timestamp": vecna_response.timestamp.isoformat()
                                })
                                
                                # Schedule grip release message
                                async def send_grip_release():
                                    await asyncio.sleep(vecna_response.freeze_duration)
                                    await app.state.websocket_manager.send_to_user(websocket, {
                                        "type": "vecna_release",
                                        "content": "[SYSTEM] Control returned to SysOp. Continue your session."
                                    })
                                
                                # Start grip release task
                                asyncio.create_task(send_grip_release())
                            
                            # Log Vecna activation
                            print(f"Vecna activated for user {user.username}: {vecna_trigger.trigger_type.value} - {vecna_trigger.reason}")
                    
                    except Exception as e:
                        print(f"Vecna evaluation error: {e}")
                
                # Step 3: SysOp Brain routing (if Vecna was not activated)
                # If Vecna was not activated, use SysOp Brain for intelligent routing
                if not vecna_activated:
                    # Use SysOp Brain for intelligent routing
                    sysop_brain = getattr(app.state, 'sysop_brain', None)
                    if sysop_brain:
                        try:
                            sysop_result = await sysop_brain.process_message(
                                user=user,
                                message=content,
                                current_room=current_room,
                                user_profile=user_profile
                            )
                            
                            # Handle different actions
                            action = sysop_result.get("action")
                            
                            if action == "suggest_room":
                                # Room suggestion - only move if high confidence and different room
                                suggested_room = sysop_result.get("room")
                                
                                if suggested_room and suggested_room != current_room:
                                    # Leave current room
                                    app.state.room_service.leave_room(user, current_room)
                                    
                                    # Notify old room
                                    await app.state.websocket_manager.broadcast_to_room(
                                        current_room,
                                        {
                                            "type": "system",
                                            "content": f"* {user.username} has left the room"
                                        }
                                    )
                                    
                                    # Join new room
                                    app.state.room_service.join_room(user, suggested_room)
                                    app.state.websocket_manager.update_user_room(websocket, suggested_room)
                                    current_room = suggested_room
                                    
                                    # Send room_change message FIRST to update side panel
                                    await app.state.websocket_manager.send_to_user(websocket, {
                                        "type": "room_change",
                                        "room": suggested_room,
                                        "content": f"You are now in: {suggested_room}"
                                    })
                                    
                                    # Send room entry message to user
                                    room = app.state.room_service.get_room(suggested_room)
                                    if room:
                                        await app.state.websocket_manager.send_to_user(websocket, {
                                            "type": "system",
                                            "content": f"\n[SYSOP] Moving you to {suggested_room} - better fit for your message."
                                        })
                                        
                                        await app.state.websocket_manager.send_to_user(websocket, {
                                            "type": "system",
                                            "content": f"\n=== {room.name} ===\n{room.description}\n"
                                        })
                                        
                                        # Send recent message history
                                        recent_messages = room.get_recent_messages(limit=20)
                                        if recent_messages:
                                            await app.state.websocket_manager.send_to_user(websocket, {
                                                "type": "system",
                                                "content": "--- Recent messages ---"
                                            })
                                            for msg in recent_messages:
                                                await app.state.websocket_manager.send_to_user(websocket, msg)
                                        
                                        # Notify new room of user entry
                                        await app.state.websocket_manager.broadcast_to_room(
                                            suggested_room,
                                            {
                                                "type": "system",
                                                "content": f"* {user.username} has entered the room"
                                            },
                                            exclude_websocket=websocket
                                        )
                                    
                                    # Broadcast updated room list
                                    rooms = app.state.room_service.get_rooms()
                                    await app.state.websocket_manager.broadcast_to_all({
                                        "type": "room_list",
                                        "rooms": [
                                            {
                                                "name": room.name,
                                                "count": app.state.room_service.get_room_count(room.name),
                                                "description": room.description
                                            }
                                            for room in rooms
                                        ]
                                    })
                            
                            elif action == "create_board":
                                # Dynamic board creation - move user to new board
                                new_board = sysop_result.get("board")
                                if new_board:
                                    # Leave current room
                                    app.state.room_service.leave_room(user, current_room)
                                    
                                    # Join new board
                                    app.state.room_service.join_room(user, new_board.name)
                                    app.state.websocket_manager.update_user_room(websocket, new_board.name)
                                    current_room = new_board.name
                                    
                                    # Notify user
                                    await app.state.websocket_manager.send_to_user(websocket, {
                                        "type": "system",
                                        "content": sysop_result.get("message", f"Created new board: {new_board.name}")
                                    })
                                    
                                    # Send room entry message
                                    await app.state.websocket_manager.send_to_user(websocket, {
                                        "type": "system",
                                        "content": f"\n=== {new_board.name} ===\n{new_board.description}\n"
                                    })
                                    
                                    # Broadcast updated room list
                                    rooms = app.state.room_service.get_rooms()
                                    await app.state.websocket_manager.broadcast_to_all({
                                        "type": "room_list",
                                        "rooms": [
                                            {
                                                "name": room.name,
                                                "count": app.state.room_service.get_room_count(room.name),
                                                "description": room.description
                                            }
                                            for room in rooms
                                        ]
                                    })
                        
                        except Exception as e:
                            # Log error but don't break message flow
                            print(f"SysOp Brain error: {e}")
                    
                    # Create message with timestamp
                    message = {
                        "type": "chat_message",
                        "username": user.username,
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "room": current_room
                    }
                    
                    # Store message in room history
                    room = app.state.room_service.get_room(current_room)
                    if room:
                        room.add_message(message)
                    
                    # Broadcast to room (including sender)
                    await app.state.websocket_manager.broadcast_to_room(current_room, message)
            
            elif message_type == "command":
                # Handle command
                command = data.get("command", "").strip()
                if not command:
                    continue
                
                # Check rate limit
                allowed, error_message, should_disconnect = app.state.rate_limiter.check_command_limit(user.username)
                
                if not allowed:
                    # Send error message to user
                    await app.state.websocket_manager.send_to_user(websocket, {
                        "type": "error",
                        "content": error_message
                    })
                    
                    # Disconnect if persistent abuse
                    if should_disconnect:
                        await websocket.close(code=1008, reason="Rate limit violation")
                        break
                    
                    continue
                
                # Remove leading "/" if present
                if command.startswith("/"):
                    command = command[1:]
                
                # Parse command and arguments
                parts = command.split(maxsplit=1)
                cmd_name = parts[0] if parts else ""
                cmd_args = parts[1] if len(parts) > 1 else None
                
                # Track command in user profile
                user_profile_service.record_command(user.id, cmd_name)
                
                # Execute command
                response = app.state.command_handler.handle_command(cmd_name, user, cmd_args)
                
                # Send response to user
                await app.state.websocket_manager.send_to_user(websocket, response)
                
                # If it's a users command, send updated list
                if cmd_name == "users":
                    # Response already contains the user list
                    pass
            
            elif message_type == "join_room":
                # Handle room change
                new_room = data.get("room", "").strip()
                if not new_room:
                    continue
                
                # Check if room exists
                room = app.state.room_service.get_room(new_room)
                if not room:
                    await app.state.websocket_manager.send_to_user(websocket, {
                        "type": "error",
                        "content": f"Room '{new_room}' not found."
                    })
                    continue
                
                # Get current room
                current_room = app.state.websocket_manager.get_user_room(user.username)
                
                # Check if already in that room
                if current_room == new_room:
                    await app.state.websocket_manager.send_to_user(websocket, {
                        "type": "error",
                        "content": f"You are already in {new_room}."
                    })
                    continue
                
                # Leave current room
                if current_room:
                    app.state.room_service.leave_room(user, current_room)
                    
                    # Notify old room
                    await app.state.websocket_manager.broadcast_to_room(
                        current_room,
                        {
                            "type": "system",
                            "content": f"* {user.username} has left the room"
                        }
                    )
                
                # Join new room
                app.state.room_service.join_room(user, new_room)
                app.state.websocket_manager.update_user_room(websocket, new_room)
                
                # Send room entry message to user
                await app.state.websocket_manager.send_to_user(websocket, {
                    "type": "system",
                    "content": f"\n=== {room.name} ===\n{room.description}\n"
                })
                
                # Send recent message history
                recent_messages = room.get_recent_messages(limit=20)
                if recent_messages:
                    await app.state.websocket_manager.send_to_user(websocket, {
                        "type": "system",
                        "content": "--- Recent messages ---"
                    })
                    for msg in recent_messages:
                        await app.state.websocket_manager.send_to_user(websocket, msg)
                
                # Notify new room
                await app.state.websocket_manager.broadcast_to_room(
                    new_room,
                    {
                        "type": "system",
                        "content": f"* {user.username} has entered the room"
                    },
                    exclude_websocket=websocket
                )
                
                # Broadcast updated active users list
                active_users = app.state.websocket_manager.get_active_users()
                await app.state.websocket_manager.broadcast_to_all({
                    "type": "user_list",
                    "users": active_users
                })
                
                # Broadcast updated room list (for side panel room counts)
                rooms = app.state.room_service.get_rooms()
                await app.state.websocket_manager.broadcast_to_all({
                    "type": "room_list",
                    "rooms": [
                        {
                            "name": room.name,
                            "count": app.state.room_service.get_room_count(room.name),
                            "description": room.description
                        }
                        for room in rooms
                    ]
                })
                
                # Send room_change message to user
                await app.state.websocket_manager.send_to_user(websocket, {
                    "type": "room_change",
                    "room": new_room,
                    "content": f"You are now in: {new_room}"
                })
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user.username if user else 'unknown'}")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        # Handle disconnection
        if user:
            # Get user's current room before disconnect
            current_room = app.state.websocket_manager.get_user_room(user.username)
            
            # Disconnect from WebSocket manager
            await app.state.websocket_manager.disconnect(websocket)
            
            # Reset rate limiter state for this user
            app.state.rate_limiter.reset_user(user.username)
            
            # Store session for potential reconnection
            if current_room:
                disconnected_sessions[user.username] = {
                    "room": current_room,
                    "disconnected_at": datetime.utcnow()
                }
                print(f"Session preserved for {user.username} in {current_room}")
            
            # Notify room of user leaving
            if current_room:
                await app.state.websocket_manager.broadcast_to_room(
                    current_room,
                    {
                        "type": "system",
                        "content": f"* {user.username} has left the room"
                    }
                )
            
            # Broadcast updated active users list
            active_users = app.state.websocket_manager.get_active_users()
            await app.state.websocket_manager.broadcast_to_all({
                "type": "user_list",
                "users": active_users
            })
            
            # Broadcast updated room list
            rooms = app.state.room_service.get_rooms()
            await app.state.websocket_manager.broadcast_to_all({
                "type": "room_list",
                "rooms": [
                    {
                        "name": room.name,
                        "count": app.state.room_service.get_room_count(room.name),
                        "description": room.description
                    }
                    for room in rooms
                ]
            })


if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )
