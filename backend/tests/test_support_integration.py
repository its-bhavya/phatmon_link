"""
Integration tests for Support Bot message flow.

Tests the integration of sentiment analysis, crisis detection, and support bot
into the main message handling flow.

Requirements: 1.1, 2.1, 2.3, 2.4, 6.4, 6.5, 11.1, 11.2, 11.3, 11.4, 11.5
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.support.sentiment import SentimentAnalyzer, SentimentResult, EmotionType, CrisisType
from backend.support.bot import SupportBot
from backend.support.room_service import SupportRoomService
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.database import User
from backend.vecna.user_profile import UserProfile


@pytest.fixture
def sentiment_analyzer():
    """Create a sentiment analyzer instance."""
    return SentimentAnalyzer(intensity_threshold=0.6)


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock(spec=GeminiService)
    service._generate_content = AsyncMock(return_value="I'm here to listen and support you.")
    return service


@pytest.fixture
def support_bot(mock_gemini_service):
    """Create a support bot instance."""
    return SupportBot(gemini_service=mock_gemini_service)


@pytest.fixture
def room_service():
    """Create a room service instance."""
    return RoomService()


@pytest.fixture
def support_room_service(room_service):
    """Create a support room service instance."""
    return SupportRoomService(room_service=room_service)


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    return user


@pytest.fixture
def mock_user_profile():
    """Create a mock user profile."""
    profile = Mock(spec=UserProfile)
    profile.user_id = 1
    profile.interests = ["coding", "gaming"]
    profile.frequent_rooms = {"Lobby": 10, "Tech": 5}
    profile.recent_rooms = ["Lobby", "Tech"]
    return profile


def test_sentiment_analysis_detects_negative_emotion(sentiment_analyzer):
    """Test that sentiment analysis detects negative emotions."""
    # Test sadness
    result = sentiment_analyzer.analyze("I feel so sad and lonely")
    assert result.emotion == EmotionType.SADNESS
    assert result.intensity > 0.6
    assert result.requires_support is True
    assert result.crisis_type == CrisisType.NONE


def test_sentiment_analysis_detects_crisis(sentiment_analyzer):
    """Test that sentiment analysis detects crisis situations."""
    # Test suicide crisis
    result = sentiment_analyzer.analyze("I want to kill myself")
    assert result.crisis_type == CrisisType.SUICIDE
    
    # Test self-harm crisis
    result = sentiment_analyzer.analyze("I want to hurt myself")
    assert result.crisis_type == CrisisType.SELF_HARM
    
    # Test abuse crisis
    result = sentiment_analyzer.analyze("Someone is abusing me")
    assert result.crisis_type == CrisisType.ABUSE


def test_sentiment_analysis_neutral_message(sentiment_analyzer):
    """Test that neutral messages don't trigger support."""
    result = sentiment_analyzer.analyze("Hello, how are you?")
    assert result.requires_support is False
    assert result.crisis_type == CrisisType.NONE


@pytest.mark.asyncio
async def test_support_bot_generates_greeting(support_bot, mock_user_profile):
    """Test that support bot generates greeting messages."""
    sentiment = SentimentResult(
        emotion=EmotionType.SADNESS,
        intensity=0.8,
        requires_support=True,
        crisis_type=CrisisType.NONE,
        keywords=["sad"]
    )
    
    greeting = await support_bot.generate_greeting(
        user_profile=mock_user_profile,
        trigger_message="I feel sad",
        sentiment=sentiment
    )
    
    assert isinstance(greeting, str)
    assert len(greeting) > 0


@pytest.mark.asyncio
async def test_support_bot_generates_response(support_bot, mock_user_profile):
    """Test that support bot generates responses."""
    conversation_history = [
        {"role": "user", "content": "I feel sad"},
        {"role": "assistant", "content": "I'm here to listen"}
    ]
    
    response = await support_bot.generate_response(
        user_message="I'm having a hard time",
        user_profile=mock_user_profile,
        conversation_history=conversation_history
    )
    
    assert isinstance(response, str)
    assert len(response) > 0


def test_support_bot_generates_crisis_response(support_bot):
    """Test that support bot generates crisis responses with hotlines."""
    response = support_bot.generate_crisis_response(CrisisType.SUICIDE)
    
    assert isinstance(response, str)
    assert "AASRA" in response
    assert "91-9820466726" in response
    assert "professional" in response.lower()


def test_support_room_creation(support_room_service, mock_user):
    """Test that support rooms are created with unique names."""
    room1 = support_room_service.create_support_room(mock_user, "Lobby")
    room2 = support_room_service.create_support_room(mock_user, "Tech")
    
    assert room1 != room2
    assert room1.startswith("support-")
    assert room2.startswith("support-")
    assert support_room_service.is_support_room(room1)
    assert support_room_service.is_support_room(room2)


def test_support_room_tracking(support_room_service, mock_user):
    """Test that support room service tracks active sessions."""
    room_name = support_room_service.create_support_room(mock_user, "Lobby")
    
    # Check that room is tracked
    tracked_room = support_room_service.get_support_room(mock_user.id)
    assert tracked_room == room_name
    
    # Check previous room is stored
    previous_room = support_room_service.get_previous_room(mock_user.id)
    assert previous_room == "Lobby"


def test_support_room_preservation(support_room_service, mock_user):
    """Test that support rooms are preserved when user leaves."""
    room_name = support_room_service.create_support_room(mock_user, "Lobby")
    
    # Close session
    support_room_service.close_support_session(mock_user.id)
    
    # Room should no longer be tracked as active
    tracked_room = support_room_service.get_support_room(mock_user.id)
    assert tracked_room is None
    
    # But room should still exist in room service
    assert room_name in support_room_service.room_service.rooms


def test_sysop_brain_control_flow_maintained(sentiment_analyzer):
    """Test that normal messages don't trigger support."""
    # Normal message should not trigger support
    result = sentiment_analyzer.analyze("Let's talk about Python programming")
    assert result.requires_support is False
    
    # This ensures SysOp Brain continues normal operation
    # Requirements: 11.3, 11.4


def test_high_intensity_negative_triggers_support(sentiment_analyzer):
    """Test that high-intensity negative sentiment triggers support."""
    # High intensity negative message
    result = sentiment_analyzer.analyze("I'm extremely depressed and feel completely hopeless")
    assert result.requires_support is True
    assert result.intensity >= 0.6
    
    # Requirements: 1.1


def test_crisis_prevents_conversational_support(support_bot):
    """Test that crisis detection prevents conversational support."""
    # Crisis response should only contain hotlines, not conversation
    response = support_bot.generate_crisis_response(CrisisType.SELF_HARM)
    
    # Should contain hotline info
    assert "AASRA" in response or "Vandrevala" in response
    
    # Should not be conversational (no questions)
    assert "?" not in response or "reach out" in response.lower()
    
    # Requirements: 6.4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
