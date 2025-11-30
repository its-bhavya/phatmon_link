"""
Database configuration and models for Phantom Link BBS.

This module provides SQLAlchemy setup for SQLite database with User and Session models.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Index
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


# Database engine and session configuration
engine = None
SessionLocal = None


def init_database(database_url: str = "sqlite:///./phantom_link.db") -> None:
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
