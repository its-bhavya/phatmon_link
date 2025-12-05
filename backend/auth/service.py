"""
Authentication service for Obsidian BBS.

This module provides authentication functionality including:
- Password hashing and verification using bcrypt
- Username and password validation
- JWT token generation and validation
- User registration and login
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.database import User, Session as SessionModel
from backend.config import get_config


class AuthService:
    """
    Authentication service handling user registration, login, and session management.
    
    This service provides:
    - Password hashing and verification
    - Username and password validation
    - JWT token generation and validation
    - User registration and authentication
    """
    
    def __init__(self, db: Session):
        """
        Initialize the authentication service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.config = get_config()
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt with cost factor 12.
        
        Bcrypt has a 72-byte limit, so we truncate passwords if necessary.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash password with cost factor 12
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Bcrypt has a 72-byte limit, so we truncate passwords if necessary.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def validate_username(self, username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username according to requirements.
        
        Requirements:
        - Must be between 3 and 20 characters
        - Must be unique (not already taken)
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        # Check length
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        
        # Check uniqueness
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already taken"
        
        return True, None
    
    def validate_password(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password according to requirements.
        
        Requirements:
        - Must be at least 8 characters long
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        return True, None
    
    def create_jwt_token(self, user: User) -> str:
        """
        Generate a JWT token for a user.
        
        The token includes:
        - user_id: User's database ID
        - username: User's username
        - iat: Issued at timestamp (with microseconds for uniqueness)
        - exp: Expiration timestamp (1 hour from creation)
        
        Args:
            user: User object to create token for
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.config.JWT_EXPIRATION_HOURS)
        
        payload = {
            "user_id": user.id,
            "username": user.username,
            "iat": now.timestamp(),  # Include issued-at with microseconds for uniqueness
            "exp": expires_at
        }
        
        token = jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM)
        return token
    
    def validate_jwt_token(self, token: str) -> Optional[dict]:
        """
        Validate a JWT token and extract payload.
        
        Args:
            token: JWT token string to validate
            
        Returns:
            Token payload dict if valid, None if invalid or expired
            Payload contains: user_id, username, exp
        """
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=[self.config.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register_user(self, username: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        This method:
        1. Validates username and password
        2. Hashes the password
        3. Creates user in database
        4. Returns the created user
        
        Args:
            username: Desired username
            password: Plain text password
            
        Returns:
            Tuple of (user, error_message)
            - (User, None) if successful
            - (None, error_message) if failed
        """
        # Validate username
        is_valid, error = self.validate_username(username)
        if not is_valid:
            return None, error
        
        # Validate password
        is_valid, error = self.validate_password(password)
        if not is_valid:
            return None, error
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user = User(
            username=username,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user, None
        except Exception as e:
            self.db.rollback()
            return None, f"Failed to create user: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password to verify
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Find user by username
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return None
        
        # Update last login time
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_session(self, user: User) -> str:
        """
        Create a session for a user and return JWT token.
        
        This method:
        1. Generates a JWT token
        2. Stores session in database
        3. Returns the token
        
        Args:
            user: User to create session for
            
        Returns:
            JWT token string
        """
        # Generate JWT token
        token = self.create_jwt_token(user)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(hours=self.config.JWT_EXPIRATION_HOURS)
        
        # Store session in database
        session = SessionModel(
            user_id=user.id,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        self.db.add(session)
        self.db.commit()
        
        return token
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = self.validate_jwt_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
