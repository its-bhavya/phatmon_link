"""
Database configuration and models for Obsidian BBS.

This module provides SQLAlchemy setup for SQLite database with User and Session models.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Index, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

# Base class for all models
Base = declarative_base()


class User(Base):
    """
    User model representing a registered user in the system.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        username: Unique username (3-20 characters)
        password_hash: Bcrypt hashed password
        created_at: Timestamp when user was created
        last_login: Timestamp of last successful login
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship to sessions
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    # Relationship to user profile
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Relationship to command history
    command_history = relationship("CommandHistory", back_populates="user", cascade="all, delete-orphan")
    
    # Relationship to board tracking
    board_tracking = relationship("BoardTracking", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# Index for fast username lookups
Index('idx_username', User.username)


class Session(Base):
    """
    Session model representing an authenticated user session.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        token: JWT token string (unique)
        created_at: Timestamp when session was created
        expires_at: Timestamp when session expires
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"


# Index for fast token lookups
Index('idx_token', Session.token)


class UserProfile(Base):
    """
    User profile model for behavioral tracking and analysis.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table (unique)
        interests: JSON array of detected user interests
        frequent_rooms: JSON object mapping room names to visit counts
        recent_rooms: JSON array of recently visited rooms (last 10)
        activity_baseline: JSON object with statistical baseline for normal activity
        created_at: Timestamp when profile was created
        updated_at: Timestamp when profile was last updated
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    interests = Column(Text, nullable=True)  # JSON array
    frequent_rooms = Column(Text, nullable=True)  # JSON object
    recent_rooms = Column(Text, nullable=True)  # JSON array
    activity_baseline = Column(Text, nullable=True)  # JSON object
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


class CommandHistory(Base):
    """
    Command history model for tracking user command patterns.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        command: Command text executed by user
        executed_at: Timestamp when command was executed
    """
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    command = Column(Text, nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="command_history")
    
    def __repr__(self):
        return f"<CommandHistory(id={self.id}, user_id={self.user_id}, command='{self.command}')>"


class BoardTracking(Base):
    """
    Board tracking model for monitoring board creation and completion.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        board_name: Name of the board created
        created_at: Timestamp when board was created
        completed: Boolean indicating if board tasks are completed
        completed_at: Timestamp when board was marked complete (nullable)
    """
    __tablename__ = "board_tracking"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    board_name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="board_tracking")
    
    def __repr__(self):
        return f"<BoardTracking(id={self.id}, user_id={self.user_id}, board_name='{self.board_name}', completed={self.completed})>"


class SupportActivation(Base):
    """
    Support activation model for logging support bot triggers.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        emotion_type: Type of emotion detected (sadness, anger, etc.)
        intensity: Intensity score (0.0-1.0)
        trigger_message_hash: Hashed trigger message for privacy
        activated_at: Timestamp when support was activated
    """
    __tablename__ = "support_activations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    emotion_type = Column(String(50), nullable=False)
    intensity = Column(Float, nullable=False)
    trigger_message_hash = Column(String(64), nullable=True)
    activated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SupportActivation(id={self.id}, user_id={self.user_id}, emotion_type='{self.emotion_type}')>"


class CrisisDetection(Base):
    """
    Crisis detection model for logging crisis situations.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        crisis_type: Type of crisis (self_harm, suicide, abuse)
        message_hash: Hashed message for privacy
        hotlines_provided: JSON array of hotline names provided
        detected_at: Timestamp when crisis was detected
    """
    __tablename__ = "crisis_detections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    crisis_type = Column(String(50), nullable=False)
    message_hash = Column(String(64), nullable=True)
    hotlines_provided = Column(Text, nullable=True)  # JSON array
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CrisisDetection(id={self.id}, user_id={self.user_id}, crisis_type='{self.crisis_type}')>"


class SupportInteraction(Base):
    """
    Support interaction model for logging bot conversations.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        user_message_hash: Hashed user message for privacy
        bot_response_hash: Hashed bot response for privacy
        interaction_at: Timestamp of interaction
    """
    __tablename__ = "support_interactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_message_hash = Column(String(64), nullable=True)
    bot_response_hash = Column(String(64), nullable=True)
    interaction_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SupportInteraction(id={self.id}, user_id={self.user_id})>"


# Indexes for performance optimization
Index('idx_command_history_user_time', CommandHistory.user_id, CommandHistory.executed_at)
Index('idx_board_tracking_user', BoardTracking.user_id)
Index('idx_support_activations_user', SupportActivation.user_id)
Index('idx_crisis_detections_user', CrisisDetection.user_id)
Index('idx_support_interactions_user', SupportInteraction.user_id)


# Database engine and session configuration
engine = None
SessionLocal = None


def init_database(database_url: str = "sqlite:///./obsidian_bbs.db") -> None:
    """
    Initialize the database connection and create all tables.
    
    Args:
        database_url: SQLAlchemy database URL (default: SQLite file)
    
    This function:
    - Creates the database engine
    - Configures the session factory
    - Creates all tables if they don't exist
    - Sets up indexes for optimized queries
    """
    global engine, SessionLocal
    
    # Create engine with appropriate settings for SQLite
    # StaticPool is used for SQLite to handle threading properly
    # check_same_thread=False allows SQLite to be used across threads (needed for FastAPI)
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        poolclass=StaticPool if database_url.startswith("sqlite") else None,
        echo=False  # Set to True for SQL query logging during development
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency function to get database session.
    
    Yields:
        Database session that automatically closes after use
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_database() -> None:
    """
    Close the database connection and clean up resources.
    
    Should be called when shutting down the application.
    """
    global engine
    if engine is not None:
        engine.dispose()
        engine = None
