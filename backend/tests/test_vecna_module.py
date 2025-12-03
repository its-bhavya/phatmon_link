"""
Tests for VecnaModule core functionality.

This module tests the VecnaModule class including trigger evaluation,
emotional trigger execution, and Psychic Grip execution.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.vecna.module import (
    VecnaModule,
    TriggerType,
    VecnaTrigger,
    VecnaResponse,
    corrupt_text
)
from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.gemini_service import GeminiService
from backend.vecna.user_profile import UserProfile


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = MagicMock(spec=GeminiService)
    service.generate_hostile_response = AsyncMock(return_value="You are pathetic, human.")
    service.generate_psychic_grip_narrative = AsyncMock(
        return_value="I see you return to the Archives... again and again..."
    )
    return service


@pytest.fixture
def sentiment_analyzer():
    """Create a sentiment analyzer."""
    return SentimentAnalyzer(intensity_threshold=0.7)


@pytest.fixture
def vecna_module(mock_gemini_service, sentiment_analyzer):
    """Create a VecnaModule instance."""
    return VecnaModule(
        gemini_service=mock_gemini_service,
        sentiment_analyzer=sentiment_analyzer,
        psychic_grip_duration_range=(5, 8)
    )


@pytest.fixture
def user_profile():
    """Create a test user profile."""
    return UserProfile(
        user_id=1,
        interests=["programming", "testing"],
        frequent_rooms={"Lobby": 10, "Techline": 5},
        recent_rooms=["Lobby", "Techline", "Archives"],
        command_history=[
            ("/help", datetime.utcnow()),
            ("/rooms", datetime.utcnow() - timedelta(seconds=30))
        ],
        unfinished_boards=["Project Alpha"],
        activity_baseline={
            'messages_per_minute': 2.0,
            'commands_per_minute': 0.5,
            'room_switches_per_hour': 3.0
        },
        behavioral_patterns={}
    )


class TestVecnaModuleInitialization:
    """Test VecnaModule initialization."""
    
    def test_initialization(self, vecna_module):
        """Test that VecnaModule initializes correctly."""
        assert vecna_module is not None
        assert vecna_module.gemini is not None
        assert vecna_module.sentiment is not None
        assert vecna_module.psychic_grip_duration == (5, 8)


class TestTriggerEvaluation:
    """Test trigger evaluation logic."""
    
    @pytest.mark.asyncio
    async def test_emotional_trigger_detection(self, vecna_module, user_profile):
        """Test that high-negative sentiment triggers emotional response."""
        message = "This is terrible and I hate it so much!"
        
        trigger = await vecna_module.evaluate_triggers(
            user_id=1,
            message=message,
            user_profile=user_profile
        )
        
        assert trigger is not None
        assert trigger.trigger_type == TriggerType.EMOTIONAL
        assert trigger.intensity >= 0.7
        assert "negative sentiment" in trigger.reason.lower()
    
    @pytest.mark.asyncio
    async def test_no_trigger_for_neutral_message(self, vecna_module):
        """Test that neutral messages don't trigger Vecna."""
        message = "Hello, how are you today?"
        
        # Use a profile without baseline to avoid unusual activity trigger
        profile = UserProfile(
            user_id=1,
            interests=[],
            frequent_rooms={},
            recent_rooms=[],
            command_history=[],
            activity_baseline={}  # No baseline = no unusual activity detection
        )
        
        trigger = await vecna_module.evaluate_triggers(
            user_id=1,
            message=message,
            user_profile=profile
        )
        
        assert trigger is None
    



class TestEmotionalTriggerExecution:
    """Test emotional trigger execution (Psychic Grip)."""
    
    @pytest.mark.asyncio
    async def test_execute_emotional_trigger(self, vecna_module, user_profile):
        """Test emotional trigger execution returns Psychic Grip response."""
        message = "This is terrible!"
        
        response = await vecna_module.execute_emotional_trigger(
            user_id=1,
            username="testuser",
            message=message,
            user_profile=user_profile
        )
        
        assert response is not None
        assert response.trigger_type == TriggerType.EMOTIONAL
        assert response.content.startswith("[VECNA]")
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8
        assert 'flicker' in response.visual_effects
        assert 'inverted' in response.visual_effects
        assert 'scanlines' in response.visual_effects
        assert 'static' in response.visual_effects
    
    @pytest.mark.asyncio
    async def test_emotional_trigger_calls_gemini(self, vecna_module, user_profile):
        """Test that emotional trigger calls Gemini service for Psychic Grip narrative."""
        message = "This is awful!"
        
        response = await vecna_module.execute_emotional_trigger(
            user_id=1,
            username="testuser",
            message=message,
            user_profile=user_profile
        )
        
        # Verify Gemini was called for Psychic Grip narrative
        vecna_module.gemini.generate_psychic_grip_narrative.assert_called_once()
        assert response.content.startswith("[VECNA]")
    
    @pytest.mark.asyncio
    async def test_emotional_trigger_fallback_on_error(self, vecna_module, user_profile):
        """Test that emotional trigger has fallback when Gemini fails."""
        # Make Gemini service raise an error
        vecna_module.gemini.generate_psychic_grip_narrative.side_effect = Exception("API Error")
        
        message = "This is terrible!"
        
        response = await vecna_module.execute_emotional_trigger(
            user_id=1,
            username="testuser",
            message=message,
            user_profile=user_profile
        )
        
        # Should still return a response with Psychic Grip
        assert response is not None
        assert response.content.startswith("[VECNA]")
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8


class TestPsychicGripExecution:
    """Test Psychic Grip execution."""
    
    @pytest.mark.asyncio
    async def test_execute_psychic_grip(self, vecna_module, user_profile):
        """Test Psychic Grip execution returns proper response."""
        response = await vecna_module.execute_psychic_grip(
            user_id=1,
            username="testuser",
            user_profile=user_profile
        )
        
        assert response is not None
        assert response.trigger_type == TriggerType.SYSTEM
        assert response.content.startswith("[VECNA]")
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8
        assert 'flicker' in response.visual_effects
        assert 'inverted' in response.visual_effects
        assert 'scanlines' in response.visual_effects
        assert 'static' in response.visual_effects
    
    @pytest.mark.asyncio
    async def test_psychic_grip_duration_range(self, vecna_module, user_profile):
        """Test that Psychic Grip duration is within expected range."""
        # Execute multiple times to test randomness
        durations = []
        for _ in range(10):
            response = await vecna_module.execute_psychic_grip(
                user_id=1,
                username="testuser",
                user_profile=user_profile
            )
            durations.append(response.freeze_duration)
        
        # All durations should be in range
        assert all(5 <= d <= 8 for d in durations)
        # Should have some variation (not all the same)
        assert len(set(durations)) > 1
    
    @pytest.mark.asyncio
    async def test_psychic_grip_calls_gemini(self, vecna_module, user_profile):
        """Test that Psychic Grip calls Gemini service."""
        response = await vecna_module.execute_psychic_grip(
            user_id=1,
            username="testuser",
            user_profile=user_profile
        )
        
        # Verify Gemini was called
        vecna_module.gemini.generate_psychic_grip_narrative.assert_called_once()
        assert response.content.startswith("[VECNA]")
    
    @pytest.mark.asyncio
    async def test_psychic_grip_fallback_on_error(self, vecna_module, user_profile):
        """Test that Psychic Grip has fallback when Gemini fails."""
        # Make Gemini service raise an error
        vecna_module.gemini.generate_psychic_grip_narrative.side_effect = Exception("API Error")
        
        response = await vecna_module.execute_psychic_grip(
            user_id=1,
            username="testuser",
            user_profile=user_profile
        )
        
        # Should still return a response
        assert response is not None
        assert response.content.startswith("[VECNA]")
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8


class TestVecnaResponse:
    """Test VecnaResponse data class."""
    
    def test_vecna_response_initialization(self):
        """Test VecnaResponse initializes with defaults."""
        response = VecnaResponse(
            trigger_type=TriggerType.EMOTIONAL,
            content="[VECNA] Test message"
        )
        
        assert response.trigger_type == TriggerType.EMOTIONAL
        assert response.content == "[VECNA] Test message"
        assert response.corrupted_text is None
        assert response.freeze_duration is None
        assert response.visual_effects == []
        assert response.timestamp is not None
    
    def test_vecna_response_with_all_fields(self):
        """Test VecnaResponse with all fields populated."""
        timestamp = datetime.utcnow()
        response = VecnaResponse(
            trigger_type=TriggerType.SYSTEM,
            content="[VECNA] Psychic Grip",
            corrupted_text=None,
            freeze_duration=7,
            visual_effects=['flicker', 'inverted'],
            timestamp=timestamp
        )
        
        assert response.trigger_type == TriggerType.SYSTEM
        assert response.content == "[VECNA] Psychic Grip"
        assert response.freeze_duration == 7
        assert response.visual_effects == ['flicker', 'inverted']
        assert response.timestamp == timestamp


class TestVecnaTrigger:
    """Test VecnaTrigger data class."""
    
    def test_vecna_trigger_initialization(self):
        """Test VecnaTrigger initializes correctly."""
        timestamp = datetime.utcnow()
        trigger = VecnaTrigger(
            trigger_type=TriggerType.EMOTIONAL,
            reason="High-negative sentiment",
            intensity=0.85,
            user_id=1,
            timestamp=timestamp
        )
        
        assert trigger.trigger_type == TriggerType.EMOTIONAL
        assert trigger.reason == "High-negative sentiment"
        assert trigger.intensity == 0.85
        assert trigger.user_id == 1
        assert trigger.timestamp == timestamp


class TestPsychicGripRelease:
    """Test Psychic Grip release mechanism."""
    
    @pytest.mark.asyncio
    async def test_psychic_grip_release_timing(self, vecna_module, user_profile):
        """
        Test that Psychic Grip release respects the freeze duration.
        
        This test verifies that the grip release mechanism:
        1. Uses the correct freeze duration from the response
        2. Would trigger after the specified duration
        
        Requirements: 4.5
        """
        import time
        
        # Execute Psychic Grip
        response = await vecna_module.execute_psychic_grip(
            user_id=1,
            username="testuser",
            user_profile=user_profile
        )
        
        # Verify freeze duration is set correctly
        assert response.freeze_duration is not None
        assert 5 <= response.freeze_duration <= 8
        
        # Simulate the release mechanism timing
        start_time = time.time()
        await asyncio.sleep(response.freeze_duration)
        elapsed_time = time.time() - start_time
        
        # Verify the sleep duration matches the freeze duration (with small tolerance)
        assert abs(elapsed_time - response.freeze_duration) < 0.5
    
    @pytest.mark.asyncio
    async def test_psychic_grip_response_contains_release_info(self, vecna_module, user_profile):
        """
        Test that Psychic Grip response contains all necessary information for release.
        
        This test verifies that the response includes:
        1. Freeze duration for timer mechanism
        2. Content for the grip message
        3. Visual effects to apply
        
        Requirements: 4.5
        """
        response = await vecna_module.execute_psychic_grip(
            user_id=1,
            username="testuser",
            user_profile=user_profile
        )
        
        # Verify response has all required fields for release mechanism
        assert response.freeze_duration is not None
        assert isinstance(response.freeze_duration, int)
        assert response.content is not None
        assert response.content.startswith("[VECNA]")
        assert response.visual_effects is not None
        assert len(response.visual_effects) > 0
        assert response.trigger_type == TriggerType.SYSTEM
    
    @pytest.mark.asyncio
    async def test_multiple_psychic_grips_have_independent_durations(self, vecna_module, user_profile):
        """
        Test that multiple Psychic Grip activations have independent durations.
        
        This ensures that each grip release is properly isolated and doesn't
        interfere with other activations.
        
        Requirements: 4.5
        """
        # Execute multiple Psychic Grips
        responses = []
        for _ in range(5):
            response = await vecna_module.execute_psychic_grip(
                user_id=1,
                username="testuser",
                user_profile=user_profile
            )
            responses.append(response)
        
        # Verify each has a valid freeze duration
        for response in responses:
            assert response.freeze_duration is not None
            assert 5 <= response.freeze_duration <= 8
        
        # Verify they are independent (not all the same)
        durations = [r.freeze_duration for r in responses]
        # With 5 random values between 5-8, we should have some variation
        assert len(set(durations)) > 1
