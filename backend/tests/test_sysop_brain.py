"""
Tests for SysOp Brain Service.

This module tests the SysOpBrain class to ensure:
- Message processing and routing
- Room suggestions based on user profiles
- Dynamic board creation
- Integration with GeminiService and RoomService
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.sysop.brain import SysOpBrain
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.rooms.models import Room
from backend.database import User
from backend.vecna.user_profile import UserProfile


@pytest.fixture
def mock_gemini_service():
    """Create a mock GeminiService."""
    service = Mock(spec=GeminiService)
    service.analyze_message_relevance = AsyncMock()
    service.suggest_best_room = AsyncMock()
    service.generate_sysop_suggestion = AsyncMock()
    return service


@pytest.fixture
def mock_room_service():
    """Create a mock RoomService with default rooms."""
    service = Mock(spec=RoomService)
    
    # Create default rooms
    lobby = Room("Lobby", "Main gathering space")
    techline = Room("Techline", "Technology discussions")
    archives = Room("Archives", "Historical content")
    
    service.rooms = {
        "Lobby": lobby,
        "Techline": techline,
        "Archives": archives
    }
    
    service.get_rooms = Mock(return_value=[lobby, techline, archives])
    service.get_room = Mock(side_effect=lambda name: service.rooms.get(name))
    
    return service


@pytest.fixture
def mock_user():
    """Create a mock User."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    return user


@pytest.fixture
def mock_user_profile():
    """Create a mock UserProfile."""
    profile = UserProfile(
        user_id=1,
        interests=["programming", "technology"],
        frequent_rooms={"Lobby": 10, "Techline": 5},
        recent_rooms=["Lobby", "Techline", "Archives"],
        command_history=[],
        unfinished_boards=[],
        activity_baseline={},
        behavioral_patterns={}
    )
    return profile


@pytest.fixture
def sysop_brain(mock_gemini_service, mock_room_service):
    """Create a SysOpBrain instance with mocked dependencies."""
    return SysOpBrain(mock_gemini_service, mock_room_service)


@pytest.mark.asyncio
async def test_process_message_relevant_to_current_room(
    sysop_brain,
    mock_user,
    mock_user_profile,
    mock_gemini_service
):
    """Test message processing when message is relevant to current room."""
    # Setup: message is relevant to current room (suggested room is same as current)
    mock_gemini_service.suggest_best_room = AsyncMock(return_value={
        "suggested_room": "Techline",
        "reason": "Technical discussion fits Techline",
        "confidence": 0.9,
        "should_create_new": False,
        "new_room_topic": None
    })
    
    result = await sysop_brain.process_message(
        user=mock_user,
        message="How do I fix this Python bug?",
        current_room="Techline",
        user_profile=mock_user_profile
    )
    
    assert result["action"] == "route"
    assert result["room"] == "Techline"
    assert result["message"] is None


@pytest.mark.asyncio
async def test_process_message_not_relevant_suggests_room(
    sysop_brain,
    mock_user,
    mock_user_profile,
    mock_gemini_service
):
    """Test message processing when message is not relevant to current room."""
    # Setup: message is not relevant
    mock_gemini_service.analyze_message_relevance.return_value = {
        "is_relevant": False,
        "confidence": 0.85,
        "reason": "Technical question doesn't fit Lobby"
    }
    
    mock_gemini_service.suggest_best_room.return_value = {
        "suggested_room": "Techline",
        "confidence": 0.9,
        "reason": "Technical programming question",
        "should_create_new": False,
        "new_room_topic": ""
    }
    
    result = await sysop_brain.process_message(
        user=mock_user,
        message="How do I fix this Python bug?",
        current_room="Lobby",
        user_profile=mock_user_profile
    )
    
    assert result["action"] == "suggest_room"
    assert result["room"] == "Techline"
    assert "Techline" in result["message"]


@pytest.mark.asyncio
async def test_process_message_creates_new_board(
    sysop_brain,
    mock_user,
    mock_user_profile,
    mock_gemini_service,
    mock_room_service
):
    """Test message processing creates new board when needed."""
    # Setup: message needs new board
    mock_gemini_service.analyze_message_relevance.return_value = {
        "is_relevant": False,
        "confidence": 0.9,
        "reason": "Specific topic not covered"
    }
    
    mock_gemini_service.suggest_best_room.return_value = {
        "suggested_room": "CREATE_NEW",
        "confidence": 0.85,
        "reason": "Topic needs dedicated board",
        "should_create_new": True,
        "new_room_topic": "React Development"
    }
    
    mock_gemini_service.generate_sysop_suggestion.return_value = "Discussion board for React Development"
    
    result = await sysop_brain.process_message(
        user=mock_user,
        message="Anyone know about React hooks?",
        current_room="Lobby",
        user_profile=mock_user_profile
    )
    
    assert result["action"] == "create_board"
    assert result["board"] is not None
    assert "React Development" in result["board"].name
    assert "Created new board" in result["message"]


@pytest.mark.asyncio
async def test_suggest_rooms_with_interests(
    sysop_brain,
    mock_user_profile,
    mock_gemini_service
):
    """Test room suggestions based on user interests."""
    mock_gemini_service.generate_sysop_suggestion.return_value = (
        "You might enjoy Techline for technology discussions!"
    )
    
    suggestions = await sysop_brain.suggest_rooms(mock_user_profile)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert "Techline" in suggestions


@pytest.mark.asyncio
async def test_suggest_rooms_without_profile_data(
    sysop_brain,
    mock_gemini_service
):
    """Test room suggestions with minimal profile data."""
    empty_profile = UserProfile(
        user_id=1,
        interests=[],
        frequent_rooms={},
        recent_rooms=[]
    )
    
    mock_gemini_service.generate_sysop_suggestion.return_value = "Try exploring the Lobby!"
    
    suggestions = await sysop_brain.suggest_rooms(empty_profile)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0


@pytest.mark.asyncio
async def test_suggest_rooms_suggests_unvisited(
    sysop_brain,
    mock_gemini_service
):
    """Test that room suggestions prefer unvisited rooms."""
    profile = UserProfile(
        user_id=1,
        interests=["gaming"],
        frequent_rooms={"Lobby": 20},
        recent_rooms=["Lobby", "Lobby", "Lobby"]
    )
    
    mock_gemini_service.generate_sysop_suggestion.return_value = "Check out some new areas!"
    
    suggestions = await sysop_brain.suggest_rooms(profile)
    
    # Should suggest rooms other than Lobby
    assert isinstance(suggestions, list)
    # At least one suggestion should not be Lobby
    assert any(room != "Lobby" for room in suggestions)


@pytest.mark.asyncio
async def test_create_dynamic_board_success(
    sysop_brain,
    mock_user,
    mock_gemini_service,
    mock_room_service
):
    """Test successful dynamic board creation."""
    mock_gemini_service.generate_sysop_suggestion.return_value = (
        "A board for discussing React development and best practices"
    )
    
    board = await sysop_brain.create_dynamic_board(
        topic="React Development",
        user=mock_user
    )
    
    assert board is not None
    assert "React Development" in board.name
    assert board.description is not None


@pytest.mark.asyncio
async def test_create_dynamic_board_already_exists(
    sysop_brain,
    mock_user,
    mock_room_service
):
    """Test board creation when board already exists."""
    # Create existing board
    existing_board = Room("Techline", "Tech discussions")
    mock_room_service.rooms["Techline"] = existing_board
    
    board = await sysop_brain.create_dynamic_board(
        topic="Techline",
        user=mock_user
    )
    
    # Should return existing board
    assert board is not None
    assert board.name == "Techline"


@pytest.mark.asyncio
async def test_create_dynamic_board_sanitizes_name(
    sysop_brain,
    mock_user,
    mock_gemini_service
):
    """Test that board names are sanitized."""
    mock_gemini_service.generate_sysop_suggestion.return_value = "Test board"
    
    board = await sysop_brain.create_dynamic_board(
        topic="React!@#$%^&*() Development!!!",
        user=mock_user
    )
    
    assert board is not None
    # Name should not contain special characters
    assert not any(char in board.name for char in "!@#$%^&*()")


@pytest.mark.asyncio
async def test_create_dynamic_board_fallback_description(
    sysop_brain,
    mock_user,
    mock_gemini_service
):
    """Test board creation with fallback description when AI fails."""
    mock_gemini_service.generate_sysop_suggestion.side_effect = Exception("API Error")
    
    board = await sysop_brain.create_dynamic_board(
        topic="Test Topic",
        user=mock_user
    )
    
    assert board is not None
    assert "Test Topic" in board.description or "Discussion board" in board.description


@pytest.mark.asyncio
async def test_process_message_error_handling(
    sysop_brain,
    mock_user,
    mock_user_profile,
    mock_gemini_service
):
    """Test error handling in message processing."""
    # Setup: Gemini service raises exception
    mock_gemini_service.suggest_best_room = AsyncMock(side_effect=Exception("API Error"))
    
    result = await sysop_brain.process_message(
        user=mock_user,
        message="Test message",
        current_room="Lobby",
        user_profile=mock_user_profile
    )
    
    # Should fallback to simple routing
    assert result["action"] == "route"
    assert result["room"] == "Lobby"


def test_extract_profile_data(sysop_brain, mock_user_profile):
    """Test profile data extraction."""
    data = sysop_brain._extract_profile_data(mock_user_profile)
    
    assert "interests" in data
    assert "frequent_rooms" in data
    assert "recent_rooms" in data
    assert "behavioral_patterns" in data
    assert data["interests"] == ["programming", "technology"]


def test_sanitize_board_name(sysop_brain):
    """Test board name sanitization."""
    # Test with special characters
    name1 = sysop_brain._sanitize_board_name("React!@#$ Development")
    assert "React" in name1
    assert "Development" in name1
    assert not any(char in name1 for char in "!@#$")
    
    # Test with long name
    long_name = "This is a very long board name that exceeds the maximum length"
    name2 = sysop_brain._sanitize_board_name(long_name)
    assert len(name2) <= 30
    
    # Test with empty string
    name3 = sysop_brain._sanitize_board_name("")
    assert name3 == "New Board"
    
    # Test with only special characters
    name4 = sysop_brain._sanitize_board_name("!@#$%^&*()")
    assert name4 == "New Board"
