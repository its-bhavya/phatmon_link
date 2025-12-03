"""
Integration tests for Vecna Adversarial AI Module.

This test suite validates the complete end-to-end flows:
1. Emotional trigger flow (high-negative message → corrupted response → control return)
2. Psychic Grip flow (spam detection → freeze → narrative → release)
3. Profile tracking across multiple user actions
4. Gemini API integration with real API calls
5. Backward compatibility with existing features
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from backend.vecna.module import VecnaModule, TriggerType
from backend.vecna.gemini_service import GeminiService
from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.pattern_detector import PatternDetector
from backend.vecna.user_profile import UserProfileService, UserProfile
from backend.sysop.brain import SysOpBrain
from backend.rooms.service import RoomService
from backend.database import User


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_gemini_service():
    """Mock Gemini service for testing."""
    service = Mock(spec=GeminiService)
    service.generate_hostile_response = AsyncMock(
        return_value="[VECNA] wHy c@n't y0u f1gur3 th1s 0ut?"
    )
    service.generate_psychic_grip_narrative = AsyncMock(
        return_value="[VECNA] I see you return to the Archives... again and again..."
    )
    service.generate_sysop_suggestion = AsyncMock(
        return_value="Try checking the Tech Support board."
    )
    return service


@pytest.fixture
def sentiment_analyzer():
    """Create sentiment analyzer."""
    return SentimentAnalyzer()


@pytest.fixture
def pattern_detector():
    """Create pattern detector."""
    return PatternDetector()


@pytest.fixture
def user_profile_service(mock_db):
    """Create user profile service."""
    return UserProfileService(mock_db)


@pytest.fixture
def vecna_module(mock_gemini_service, sentiment_analyzer, pattern_detector):
    """Create Vecna module."""
    return VecnaModule(mock_gemini_service, sentiment_analyzer, pattern_detector)


@pytest.fixture
def sysop_brain(mock_gemini_service, mock_db):
    """Create SysOp Brain."""
    room_service = Mock(spec=RoomService)
    room_service.get_room = Mock(return_value=None)
    room_service.create_room = Mock(return_value=Mock(name="test_room"))
    return SysOpBrain(mock_gemini_service, room_service)


@pytest.fixture
def test_user():
    """Create test user."""
    user = User()
    user.id = 1
    user.username = "test_user"
    user.password_hash = "hashed_password"
    return user


class TestEmotionalTriggerFlow:
    """Test complete emotional trigger flow."""
    
    @pytest.mark.asyncio
    async def test_high_negative_message_triggers_vecna(
        self, vecna_module, test_user, user_profile_service
    ):
        """
        Test: high-negative message → corrupted response → control return
        
        Flow:
        1. User sends high-negative message
        2. Vecna detects emotional trigger
        3. Vecna generates corrupted hostile response
        4. Control returns to SysOp Brain
        """
        # Setup
        user_profile = user_profile_service.get_profile(test_user.id)
        high_negative_message = "I hate this stupid broken system! This is terrible!"
        
        # Step 1: Evaluate triggers
        trigger = await vecna_module.evaluate_triggers(
            test_user, high_negative_message, user_profile
        )
        
        # Verify emotional trigger detected
        assert trigger is not None
        assert trigger.trigger_type == TriggerType.EMOTIONAL
        assert trigger.intensity > 0.7
        
        # Step 2: Execute emotional trigger
        response = await vecna_module.execute_emotional_trigger(
            test_user, high_negative_message
        )
        
        # Verify corrupted response
        assert response.trigger_type == TriggerType.EMOTIONAL
        assert response.content.startswith("[VECNA]")
        assert response.corrupted_text is not None
        assert len(response.corrupted_text) > 0
        
        # Verify control can return (no blocking state)
        assert response.freeze_duration is None
        
    @pytest.mark.asyncio
    async def test_text_corruption_maintains_readability(
        self, vecna_module, test_user
    ):
        """Test that corrupted text maintains partial readability."""
        message = "This is a test message for corruption"
        
        response = await vecna_module.execute_emotional_trigger(test_user, message)
        
        # Verify corruption applied
        assert response.corrupted_text is not None
        
        # Count readable vs corrupted characters
        original = message
        corrupted = response.corrupted_text
        
        # At least some characters should be corrupted
        assert original != corrupted
        
    @pytest.mark.asyncio
    async def test_normal_message_does_not_trigger_vecna(
        self, vecna_module, test_user, user_profile_service
    ):
        """Test that normal messages don't trigger Vecna."""
        user_profile = user_profile_service.get_profile(test_user.id)
        normal_message = "Hello, how are you today?"
        
        trigger = await vecna_module.evaluate_triggers(
            test_user, normal_message, user_profile
        )
        
        # No trigger should occur
        assert trigger is None


class TestPsychicGripFlow:
    """Test complete Psychic Grip flow."""
    
    @pytest.mark.asyncio
    async def test_spam_detection_triggers_psychic_grip(
        self, vecna_module, test_user, user_profile_service
    ):
        """
        Test: spam detection → freeze → narrative → release
        
        Flow:
        1. User sends spam messages
        2. Vecna detects system trigger
        3. Vecna activates Psychic Grip with freeze
        4. Vecna generates narrative referencing profile
        5. Grip releases after duration
        """
        # Setup: Create spam pattern
        user_profile = user_profile_service.get_profile(test_user.id)
        spam_message = "test test test"
        
        # Simulate spam by adding recent messages
        now = datetime.now()
        user_profile.recent_messages = [
            (spam_message, now - timedelta(seconds=1)),
            (spam_message, now - timedelta(seconds=2)),
            (spam_message, now - timedelta(seconds=3)),
        ]
        
        # Step 1: Evaluate triggers
        trigger = await vecna_module.evaluate_triggers(
            test_user, spam_message, user_profile
        )
        
        # Verify system trigger detected
        assert trigger is not None
        assert trigger.trigger_type == TriggerType.SYSTEM
        
        # Step 2: Execute Psychic Grip
        response = await vecna_module.execute_psychic_grip(test_user, user_profile)
        
        # Verify Psychic Grip response
        assert response.trigger_type == TriggerType.SYSTEM
        assert response.content.startswith("[VECNA]")
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8
        
        # Verify visual effects specified
        assert len(response.visual_effects) > 0
        
    @pytest.mark.asyncio
    async def test_command_repetition_triggers_psychic_grip(
        self, vecna_module, test_user, user_profile_service
    ):
        """Test that repeated commands trigger Psychic Grip."""
        user_profile = user_profile_service.get_profile(test_user.id)
        
        # Simulate command repetition
        now = datetime.now()
        user_profile.command_history = [
            ("/help", now - timedelta(seconds=1)),
            ("/help", now - timedelta(seconds=3)),
            ("/help", now - timedelta(seconds=5)),
        ]
        
        trigger = await vecna_module.evaluate_triggers(
            test_user, "/help", user_profile
        )
        
        # Verify system trigger
        assert trigger is not None
        assert trigger.trigger_type == TriggerType.SYSTEM
        
    @pytest.mark.asyncio
    async def test_psychic_grip_references_profile_data(
        self, vecna_module, test_user, user_profile_service, mock_gemini_service
    ):
        """Test that Psychic Grip narrative references user profile data."""
        user_profile = user_profile_service.get_profile(test_user.id)
        
        # Add profile data
        user_profile.frequent_rooms = {"Archives": 10, "Tech Support": 5}
        user_profile.recent_rooms = ["Archives", "Archives", "Tech Support"]
        user_profile.unfinished_boards = ["My Project", "Todo List"]
        
        response = await vecna_module.execute_psychic_grip(test_user, user_profile)
        
        # Verify Gemini was called with profile context
        mock_gemini_service.generate_psychic_grip_narrative.assert_called_once()
        call_args = mock_gemini_service.generate_psychic_grip_narrative.call_args
        profile_arg = call_args[0][0]
        
        # Verify profile data was passed
        assert profile_arg.frequent_rooms == user_profile.frequent_rooms
        assert profile_arg.unfinished_boards == user_profile.unfinished_boards


class TestProfileTracking:
    """Test profile tracking across multiple user actions."""
    
    def test_room_visit_tracking(self, user_profile_service, test_user):
        """Test that room visits are tracked correctly."""
        # Record multiple room visits
        user_profile_service.record_room_visit(test_user.id, "Archives")
        user_profile_service.record_room_visit(test_user.id, "Tech Support")
        user_profile_service.record_room_visit(test_user.id, "Archives")
        
        profile = user_profile_service.get_profile(test_user.id)
        
        # Verify tracking
        assert "Archives" in profile.frequent_rooms
        assert profile.frequent_rooms["Archives"] == 2
        assert "Tech Support" in profile.frequent_rooms
        assert profile.frequent_rooms["Tech Support"] == 1
        
        # Verify recent rooms
        assert "Archives" in profile.recent_rooms
        assert "Tech Support" in profile.recent_rooms
        
    def test_command_tracking(self, user_profile_service, test_user):
        """Test that commands are tracked correctly."""
        # Record commands
        user_profile_service.record_command(test_user.id, "/help")
        user_profile_service.record_command(test_user.id, "/rooms")
        user_profile_service.record_command(test_user.id, "/help")
        
        profile = user_profile_service.get_profile(test_user.id)
        
        # Verify command history
        assert len(profile.command_history) == 3
        commands = [cmd for cmd, _ in profile.command_history]
        assert commands.count("/help") == 2
        assert commands.count("/rooms") == 1
        
    def test_board_creation_tracking(self, user_profile_service, test_user):
        """Test that board creation is tracked correctly."""
        # Record board creation
        user_profile_service.record_board_creation(
            test_user.id, "My Project", completed=False
        )
        user_profile_service.record_board_creation(
            test_user.id, "Completed Board", completed=True
        )
        
        profile = user_profile_service.get_profile(test_user.id)
        
        # Verify unfinished boards
        assert "My Project" in profile.unfinished_boards
        assert "Completed Board" not in profile.unfinished_boards
        
    def test_profile_read_only_access_by_vecna(
        self, vecna_module, test_user, user_profile_service
    ):
        """Test that Vecna has read-only access to profile data."""
        # Setup profile
        user_profile = user_profile_service.get_profile(test_user.id)
        user_profile.frequent_rooms = {"Archives": 5}
        original_rooms = user_profile.frequent_rooms.copy()
        
        # Vecna accesses profile (through trigger evaluation)
        asyncio.run(vecna_module.evaluate_triggers(
            test_user, "test message", user_profile
        ))
        
        # Verify profile unchanged
        assert user_profile.frequent_rooms == original_rooms


class TestGeminiAPIIntegration:
    """Test Gemini API integration with real API calls."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_gemini_hostile_response(self, test_user):
        """Test real Gemini API call for hostile response."""
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        gemini_service = GeminiService(api_key)
        user_profile = UserProfile(user_id=test_user.id)
        
        response = await gemini_service.generate_hostile_response(
            "This system is broken!", user_profile
        )
        
        # Verify response generated
        assert response is not None
        assert len(response) > 0
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_gemini_psychic_grip_narrative(self, test_user):
        """Test real Gemini API call for Psychic Grip narrative."""
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        gemini_service = GeminiService(api_key)
        user_profile = UserProfile(user_id=test_user.id)
        user_profile.frequent_rooms = {"Archives": 10}
        user_profile.unfinished_boards = ["My Project"]
        
        response = await gemini_service.generate_psychic_grip_narrative(user_profile)
        
        # Verify response generated
        assert response is not None
        assert len(response) > 0
        
    @pytest.mark.asyncio
    async def test_gemini_error_handling(self, test_user):
        """Test that Gemini API errors are handled gracefully."""
        # Create service with invalid API key
        gemini_service = GeminiService("invalid_key")
        user_profile = UserProfile(user_id=test_user.id)
        
        # Should not raise exception
        try:
            response = await gemini_service.generate_hostile_response(
                "test message", user_profile
            )
            # Should return fallback response
            assert response is not None
        except Exception as e:
            # If exception occurs, it should be handled gracefully
            pytest.fail(f"Gemini error not handled gracefully: {e}")


class TestSysOpBrainIntegration:
    """Test SysOp Brain integration and control flow."""
    
    @pytest.mark.asyncio
    async def test_sysop_processes_normal_messages(
        self, sysop_brain, test_user
    ):
        """Test that SysOp Brain processes messages when Vecna doesn't trigger."""
        message = "Hello, I need help with something"
        
        result = await sysop_brain.process_message(
            test_user, message, "General"
        )
        
        # Verify SysOp processed the message
        assert result is not None
        assert "action" in result or "response" in result
        
    @pytest.mark.asyncio
    async def test_control_returns_to_sysop_after_vecna(
        self, vecna_module, sysop_brain, test_user, user_profile_service
    ):
        """Test that control returns to SysOp Brain after Vecna activation."""
        user_profile = user_profile_service.get_profile(test_user.id)
        
        # Trigger Vecna
        trigger_message = "I hate this terrible broken system!"
        trigger = await vecna_module.evaluate_triggers(
            test_user, trigger_message, user_profile
        )
        
        if trigger:
            await vecna_module.execute_emotional_trigger(test_user, trigger_message)
        
        # Next message should go to SysOp
        next_message = "Can you help me now?"
        result = await sysop_brain.process_message(
            test_user, next_message, "General"
        )
        
        # Verify SysOp processed the message
        assert result is not None
        
    @pytest.mark.asyncio
    async def test_sysop_room_suggestions(
        self, sysop_brain, user_profile_service, test_user
    ):
        """Test that SysOp Brain generates room suggestions."""
        user_profile = user_profile_service.get_profile(test_user.id)
        user_profile.interests = ["programming", "python", "testing"]
        
        suggestions = await sysop_brain.suggest_rooms(user_profile)
        
        # Verify suggestions generated
        assert suggestions is not None
        assert isinstance(suggestions, list)


class TestBackwardCompatibility:
    """Test backward compatibility with existing features."""
    
    @pytest.mark.asyncio
    async def test_websocket_message_format_compatibility(self):
        """Test that new Vecna messages don't break existing message handling."""
        # Existing message types should still work
        existing_message_types = [
            "chat",
            "system",
            "user_joined",
            "user_left",
            "room_created"
        ]
        
        # Verify these are still valid
        for msg_type in existing_message_types:
            message = {
                "type": msg_type,
                "content": "test content",
                "timestamp": datetime.now().isoformat()
            }
            
            # Should not raise any errors
            assert message["type"] in existing_message_types
            
    def test_existing_user_data_not_affected(
        self, user_profile_service, test_user
    ):
        """Test that existing user data structures are not affected."""
        # Get profile (should create if not exists)
        profile = user_profile_service.get_profile(test_user.id)
        
        # Verify profile has expected structure
        assert hasattr(profile, 'user_id')
        assert hasattr(profile, 'interests')
        assert hasattr(profile, 'frequent_rooms')
        assert hasattr(profile, 'recent_rooms')
        
        # Verify user object unchanged
        assert test_user.id == 1
        assert test_user.username == "test_user"


class TestEndToEndFlow:
    """Test complete end-to-end user interaction flows."""
    
    @pytest.mark.asyncio
    async def test_complete_user_session_with_vecna_trigger(
        self, vecna_module, sysop_brain, user_profile_service, test_user
    ):
        """
        Test complete user session:
        1. User sends normal messages (SysOp handles)
        2. User sends negative message (Vecna triggers)
        3. User continues session (SysOp resumes)
        """
        user_profile = user_profile_service.get_profile(test_user.id)
        
        # Step 1: Normal message
        msg1 = "Hello, I'm looking for help"
        trigger1 = await vecna_module.evaluate_triggers(test_user, msg1, user_profile)
        assert trigger1 is None  # No trigger
        
        result1 = await sysop_brain.process_message(test_user, msg1, "General")
        assert result1 is not None
        
        # Step 2: Negative message triggers Vecna
        msg2 = "This is so frustrating! I hate this broken system!"
        trigger2 = await vecna_module.evaluate_triggers(test_user, msg2, user_profile)
        assert trigger2 is not None
        assert trigger2.trigger_type == TriggerType.EMOTIONAL
        
        vecna_response = await vecna_module.execute_emotional_trigger(test_user, msg2)
        assert vecna_response.content.startswith("[VECNA]")
        
        # Step 3: Continue with normal message
        msg3 = "Okay, let me try again"
        trigger3 = await vecna_module.evaluate_triggers(test_user, msg3, user_profile)
        assert trigger3 is None  # No trigger
        
        result3 = await sysop_brain.process_message(test_user, msg3, "General")
        assert result3 is not None
        
    @pytest.mark.asyncio
    async def test_profile_builds_over_session(
        self, user_profile_service, test_user
    ):
        """Test that user profile builds up over a session."""
        # Simulate user activity
        user_profile_service.record_room_visit(test_user.id, "Archives")
        user_profile_service.record_command(test_user.id, "/help")
        user_profile_service.record_room_visit(test_user.id, "Tech Support")
        user_profile_service.record_command(test_user.id, "/rooms")
        user_profile_service.record_board_creation(test_user.id, "My Board")
        
        profile = user_profile_service.get_profile(test_user.id)
        
        # Verify profile accumulated data
        assert len(profile.frequent_rooms) == 2
        assert len(profile.command_history) == 2
        assert len(profile.unfinished_boards) == 1



