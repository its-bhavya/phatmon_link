"""
Tests for User Profile Service.

This module tests the UserProfileService functionality including:
- Profile creation and retrieval
- Room visit recording
- Command history tracking
- Board creation tracking
- Deviation calculation
- Pattern detection
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, User, UserProfile as UserProfileModel, CommandHistory, BoardTracking
from backend.vecna.user_profile import UserProfile, UserProfileService


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
def test_user(db_session):
    """Create a test user."""
    user = User(username="testuser", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def profile_service(db_session):
    """Create a UserProfileService instance with test database."""
    return UserProfileService(db_session)


def test_get_profile_creates_new(profile_service, test_user):
    """Test that get_profile creates a new profile if none exists."""
    profile = profile_service.get_profile(test_user.id)
    
    assert profile is not None
    assert profile.user_id == test_user.id
    assert profile.interests == []
    assert profile.frequent_rooms == {}
    assert profile.recent_rooms == []
    assert profile.command_history == []
    assert profile.unfinished_boards == []


def test_get_profile_caches(profile_service, test_user):
    """Test that get_profile caches profiles."""
    profile1 = profile_service.get_profile(test_user.id)
    profile2 = profile_service.get_profile(test_user.id)
    
    # Should return same object from cache
    assert profile1 is profile2


def test_record_room_visit(profile_service, test_user):
    """Test recording room visits."""
    profile_service.record_room_visit(test_user.id, "Archives")
    profile = profile_service.get_profile(test_user.id)
    
    # Check recent rooms
    assert "Archives" in profile.recent_rooms
    assert profile.recent_rooms[0] == "Archives"
    
    # Check frequent rooms
    assert profile.frequent_rooms["Archives"] == 1
    
    # Visit again
    profile_service.record_room_visit(test_user.id, "Archives")
    profile = profile_service.get_profile(test_user.id)
    
    # Count should increment
    assert profile.frequent_rooms["Archives"] == 2


def test_record_room_visit_recent_limit(profile_service, test_user):
    """Test that recent rooms are limited to 10."""
    # Visit 15 different rooms
    for i in range(15):
        profile_service.record_room_visit(test_user.id, f"Room{i}")
    
    profile = profile_service.get_profile(test_user.id)
    
    # Should only keep last 10
    assert len(profile.recent_rooms) == 10
    # Most recent should be Room14
    assert profile.recent_rooms[0] == "Room14"
    # Oldest in list should be Room5
    assert profile.recent_rooms[9] == "Room5"


def test_record_room_visit_moves_to_front(profile_service, test_user):
    """Test that revisiting a room moves it to front of recent list."""
    profile_service.record_room_visit(test_user.id, "Room1")
    profile_service.record_room_visit(test_user.id, "Room2")
    profile_service.record_room_visit(test_user.id, "Room3")
    
    # Revisit Room1
    profile_service.record_room_visit(test_user.id, "Room1")
    
    profile = profile_service.get_profile(test_user.id)
    
    # Room1 should be at front
    assert profile.recent_rooms[0] == "Room1"
    # Should not have duplicates
    assert profile.recent_rooms.count("Room1") == 1


def test_record_command(profile_service, test_user, db_session):
    """Test recording command execution."""
    profile_service.record_command(test_user.id, "/join Archives")
    
    profile = profile_service.get_profile(test_user.id)
    
    # Check command history in profile
    assert len(profile.command_history) == 1
    assert profile.command_history[0][0] == "/join Archives"
    assert isinstance(profile.command_history[0][1], datetime)
    
    # Check database
    command_record = db_session.query(CommandHistory).filter(
        CommandHistory.user_id == test_user.id
    ).first()
    assert command_record is not None
    assert command_record.command == "/join Archives"


def test_record_command_history_limit(profile_service, test_user):
    """Test that command history is limited to 50."""
    # Record 60 commands
    for i in range(60):
        profile_service.record_command(test_user.id, f"/command{i}")
    
    profile = profile_service.get_profile(test_user.id)
    
    # Should only keep last 50 in memory
    assert len(profile.command_history) <= 50
    # Most recent should be command59
    assert profile.command_history[0][0] == "/command59"


def test_record_board_creation(profile_service, test_user, db_session):
    """Test recording board creation."""
    profile_service.record_board_creation(test_user.id, "MyBoard", completed=False)
    
    profile = profile_service.get_profile(test_user.id)
    
    # Check unfinished boards
    assert "MyBoard" in profile.unfinished_boards
    
    # Check database
    board_record = db_session.query(BoardTracking).filter(
        BoardTracking.user_id == test_user.id,
        BoardTracking.board_name == "MyBoard"
    ).first()
    assert board_record is not None
    assert board_record.completed is False


def test_record_board_completion(profile_service, test_user, db_session):
    """Test marking board as completed."""
    # Create unfinished board
    profile_service.record_board_creation(test_user.id, "MyBoard", completed=False)
    profile = profile_service.get_profile(test_user.id)
    assert "MyBoard" in profile.unfinished_boards
    
    # Mark as completed
    profile_service.record_board_creation(test_user.id, "MyBoard", completed=True)
    
    # Reload profile to get fresh data
    profile_service.profiles.clear()
    profile = profile_service.get_profile(test_user.id)
    
    # Should be removed from unfinished boards
    assert "MyBoard" not in profile.unfinished_boards
    
    # Check database
    board_record = db_session.query(BoardTracking).filter(
        BoardTracking.user_id == test_user.id,
        BoardTracking.board_name == "MyBoard"
    ).first()
    assert board_record.completed is True
    assert board_record.completed_at is not None


def test_update_interests(profile_service, test_user):
    """Test extracting and updating interests from messages."""
    profile_service.update_interests(test_user.id, "I love programming and artificial intelligence")
    
    profile = profile_service.get_profile(test_user.id)
    
    # Should extract words longer than 5 characters
    assert "programming" in profile.interests or "artificial" in profile.interests or "intelligence" in profile.interests


def test_update_interests_limit(profile_service, test_user):
    """Test that interests are limited to 20."""
    # Add 25 different interests
    for i in range(25):
        profile_service.update_interests(test_user.id, f"interest{i:02d} " * 5)
    
    profile = profile_service.get_profile(test_user.id)
    
    # Should only keep last 20
    assert len(profile.interests) <= 20


def test_calculate_deviation_no_baseline(profile_service, test_user):
    """Test deviation calculation with no baseline."""
    profile = profile_service.get_profile(test_user.id)
    
    current_activity = {
        'messages_per_minute': 5.0,
        'commands_per_minute': 2.0
    }
    
    deviation = profile.calculate_deviation(current_activity)
    
    # Should return 0 when no baseline exists
    assert deviation == 0.0


def test_calculate_deviation_with_baseline(profile_service, test_user):
    """Test deviation calculation with baseline."""
    profile = profile_service.get_profile(test_user.id)
    
    # Set baseline
    profile.activity_baseline = {
        'messages_per_minute': 2.0,
        'commands_per_minute': 1.0
    }
    
    # Normal activity (close to baseline)
    current_activity = {
        'messages_per_minute': 2.1,
        'commands_per_minute': 1.0
    }
    deviation = profile.calculate_deviation(current_activity)
    assert deviation < 0.1  # Low deviation
    
    # Abnormal activity (far from baseline)
    current_activity = {
        'messages_per_minute': 10.0,
        'commands_per_minute': 5.0
    }
    deviation = profile.calculate_deviation(current_activity)
    assert deviation > 1.0  # High deviation


def test_detect_spam_pattern_no_spam(profile_service, test_user):
    """Test spam detection with normal messages."""
    profile = profile_service.get_profile(test_user.id)
    
    messages = ["Hello", "How are you?", "What's up?", "Nice weather"]
    is_spam = profile.detect_spam_pattern(messages)
    
    assert is_spam is False


def test_detect_spam_pattern_identical_messages(profile_service, test_user):
    """Test spam detection with identical messages."""
    profile = profile_service.get_profile(test_user.id)
    
    messages = ["spam", "spam", "spam", "spam", "spam"]
    is_spam = profile.detect_spam_pattern(messages)
    
    assert is_spam is True


def test_detect_spam_pattern_similar_messages(profile_service, test_user):
    """Test spam detection with fuzzy similar messages."""
    profile = profile_service.get_profile(test_user.id)
    
    # Messages with high similarity (>0.8) - last message similar to 2+ previous
    messages = ["different", "hello world", "hello world!", "hello world?"]
    is_spam = profile.detect_spam_pattern(messages)
    
    assert is_spam is True


def test_detect_spam_pattern_high_frequency(profile_service, test_user):
    """Test spam detection with high frequency messages."""
    profile = profile_service.get_profile(test_user.id)
    
    now = datetime.utcnow()
    messages = ["msg1", "msg2", "msg3"]
    timestamps = [
        now - timedelta(seconds=3),
        now - timedelta(seconds=2),
        now
    ]
    
    is_spam = profile.detect_spam_pattern(messages, timestamps)
    
    assert is_spam is True


def test_detect_spam_pattern_template_spam(profile_service, test_user):
    """Test spam detection with template spam (similar length)."""
    profile = profile_service.get_profile(test_user.id)
    
    # Messages with similar length (±3 chars)
    messages = ["hello", "world", "tests", "check", "spam!"]
    is_spam = profile.detect_spam_pattern(messages)
    
    assert is_spam is True


def test_detect_command_repetition_no_repetition(profile_service, test_user):
    """Test command repetition detection with varied commands."""
    profile = profile_service.get_profile(test_user.id)
    
    now = datetime.utcnow()
    profile.command_history = [
        ("/join Archives", now),
        ("/list", now - timedelta(seconds=10)),
        ("/help", now - timedelta(seconds=20))
    ]
    
    is_repetition = profile.detect_command_repetition(window_seconds=60)
    
    assert is_repetition is False


def test_detect_command_repetition_with_repetition(profile_service, test_user):
    """Test command repetition detection with repeated commands."""
    profile = profile_service.get_profile(test_user.id)
    
    now = datetime.utcnow()
    profile.command_history = [
        ("/list", now),
        ("/list", now - timedelta(seconds=10)),
        ("/list", now - timedelta(seconds=20))
    ]
    
    is_repetition = profile.detect_command_repetition(window_seconds=60)
    
    assert is_repetition is True


def test_detect_command_repetition_outside_window(profile_service, test_user):
    """Test that command repetition only considers time window."""
    profile = profile_service.get_profile(test_user.id)
    
    now = datetime.utcnow()
    profile.command_history = [
        ("/list", now),
        ("/list", now - timedelta(seconds=70)),  # Outside 60s window
        ("/list", now - timedelta(seconds=80))   # Outside 60s window
    ]
    
    is_repetition = profile.detect_command_repetition(window_seconds=60)
    
    # Should not detect repetition since only 1 command in window
    assert is_repetition is False


def test_update_activity_baseline(profile_service, test_user):
    """Test updating activity baseline."""
    # Record some commands to build history
    now = datetime.utcnow()
    for i in range(20):
        profile_service.record_command(test_user.id, f"/command{i}")
    
    # Record some room visits
    for i in range(5):
        profile_service.record_room_visit(test_user.id, f"Room{i}")
    
    # Update baseline
    profile_service.update_activity_baseline(test_user.id)
    
    profile = profile_service.get_profile(test_user.id)
    
    # Should have calculated baseline metrics
    assert 'commands_per_minute' in profile.activity_baseline or 'room_switches_per_hour' in profile.activity_baseline


def test_profile_persistence(profile_service, test_user, db_session):
    """Test that profile changes are persisted to database."""
    # Make changes to profile
    profile_service.record_room_visit(test_user.id, "Archives")
    profile_service.update_interests(test_user.id, "testing database persistence")
    
    # Clear cache
    profile_service.profiles.clear()
    
    # Reload profile from database
    profile = profile_service.get_profile(test_user.id)
    
    # Changes should be persisted
    assert "Archives" in profile.recent_rooms
    assert profile.frequent_rooms["Archives"] == 1
