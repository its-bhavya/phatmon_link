"""
Tests for database models and initialization.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import (
    init_database, get_db, User, Session as SessionModel, Base,
    UserProfile, CommandHistory, BoardTracking, VecnaActivation
)
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


def test_vecna_tables_created():
    """Test that Vecna-related tables are created during initialization."""
    init_database("sqlite:///:memory:")
    
    from sqlalchemy import inspect
    inspector = inspect(backend.database.engine)
    tables = inspector.get_table_names()
    
    assert "user_profiles" in tables
    assert "command_history" in tables
    assert "board_tracking" in tables
    assert "vecna_activations" in tables


def test_user_profile_creation(test_db: Session):
    """Test creating a user profile."""
    # Create a user first
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create a profile for the user
    profile = UserProfile(
        user_id=user.id,
        interests='["coding", "gaming"]',
        frequent_rooms='{"general": 5, "tech": 3}',
        recent_rooms='["general", "tech", "random"]',
        activity_baseline='{"messages_per_hour": 10.5}'
    )
    
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    
    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.interests == '["coding", "gaming"]'
    assert profile.created_at is not None
    assert profile.updated_at is not None


def test_user_profile_unique_user_id(test_db: Session):
    """Test that each user can only have one profile."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    profile1 = UserProfile(user_id=user.id)
    test_db.add(profile1)
    test_db.commit()
    
    # Try to create another profile for the same user
    profile2 = UserProfile(user_id=user.id)
    test_db.add(profile2)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        test_db.commit()


def test_command_history_creation(test_db: Session):
    """Test creating command history entries."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    command = CommandHistory(
        user_id=user.id,
        command="/join tech"
    )
    
    test_db.add(command)
    test_db.commit()
    test_db.refresh(command)
    
    assert command.id is not None
    assert command.user_id == user.id
    assert command.command == "/join tech"
    assert command.executed_at is not None


def test_board_tracking_creation(test_db: Session):
    """Test creating board tracking entries."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    board = BoardTracking(
        user_id=user.id,
        board_name="my-project",
        completed=False
    )
    
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    
    assert board.id is not None
    assert board.user_id == user.id
    assert board.board_name == "my-project"
    assert board.completed is False
    assert board.created_at is not None
    assert board.completed_at is None


def test_vecna_activation_creation(test_db: Session):
    """Test creating Vecna activation log entries."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    activation = VecnaActivation(
        user_id=user.id,
        trigger_type="emotional",
        reason="high negative sentiment",
        intensity=0.85,
        response_content="[VECNA] Your frustration is noted..."
    )
    
    test_db.add(activation)
    test_db.commit()
    test_db.refresh(activation)
    
    assert activation.id is not None
    assert activation.user_id == user.id
    assert activation.trigger_type == "emotional"
    assert activation.reason == "high negative sentiment"
    assert activation.intensity == 0.85
    assert activation.activated_at is not None


def test_user_profile_relationship(test_db: Session):
    """Test the relationship between User and UserProfile."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    profile = UserProfile(user_id=user.id, interests='["test"]')
    test_db.add(profile)
    test_db.commit()
    
    test_db.refresh(user)
    
    assert user.profile is not None
    assert user.profile.user_id == user.id


def test_user_command_history_relationship(test_db: Session):
    """Test the relationship between User and CommandHistory."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    cmd1 = CommandHistory(user_id=user.id, command="/join tech")
    cmd2 = CommandHistory(user_id=user.id, command="/create board")
    test_db.add(cmd1)
    test_db.add(cmd2)
    test_db.commit()
    
    test_db.refresh(user)
    
    assert len(user.command_history) == 2


def test_user_board_tracking_relationship(test_db: Session):
    """Test the relationship between User and BoardTracking."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    board1 = BoardTracking(user_id=user.id, board_name="project1")
    board2 = BoardTracking(user_id=user.id, board_name="project2")
    test_db.add(board1)
    test_db.add(board2)
    test_db.commit()
    
    test_db.refresh(user)
    
    assert len(user.board_tracking) == 2


def test_user_vecna_activations_relationship(test_db: Session):
    """Test the relationship between User and VecnaActivation."""
    user = User(username="testuser", password_hash="hash")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    activation1 = VecnaActivation(user_id=user.id, trigger_type="emotional")
    activation2 = VecnaActivation(user_id=user.id, trigger_type="system")
    test_db.add(activation1)
    test_db.add(activation2)
    test_db.commit()
    
    test_db.refresh(user)
    
    assert len(user.vecna_activations) == 2


def test_vecna_indexes_exist():
    """Test that Vecna-related indexes exist for performance."""
    init_database("sqlite:///:memory:")
    
    from sqlalchemy import inspect
    inspector = inspect(backend.database.engine)
    
    # Check command_history indexes
    cmd_indexes = inspector.get_indexes("command_history")
    cmd_index_names = [idx['name'] for idx in cmd_indexes]
    assert 'idx_command_history_user_time' in cmd_index_names
    
    # Check vecna_activations indexes
    vecna_indexes = inspector.get_indexes("vecna_activations")
    vecna_index_names = [idx['name'] for idx in vecna_indexes]
    assert 'idx_vecna_activations_user' in vecna_index_names
    
    # Check board_tracking indexes
    board_indexes = inspector.get_indexes("board_tracking")
    board_index_names = [idx['name'] for idx in board_indexes]
    assert 'idx_board_tracking_user' in board_index_names
