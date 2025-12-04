"""
Integration tests for Support Bot.

Tests the complete flow of Support Bot functionality including
greeting generation, response generation, and crisis handling.

This ensures all components work together correctly.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.support.bot import SupportBot
from backend.support.sentiment import SentimentAnalyzer, EmotionType, CrisisType
from backend.vecna.user_profile import UserProfile
from backend.vecna.gemini_service import GeminiService


@pytest.fixture
def sentiment_analyzer():
    """Create a sentiment analyzer."""
    return SentimentAnalyzer(intensity_threshold=0.6)


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock(spec=GeminiService)
    service._generate_content = AsyncMock()
    return service


@pytest.fixture
def support_bot(mock_gemini_service):
    """Create a SupportBot instance."""
    return SupportBot(mock_gemini_service)


@pytest.fixture
def user_profile():
    """Create a user profile."""
    return UserProfile(
        user_id=1,
        interests=["coding", "gaming"],
        frequent_rooms={"Lobby": 5},
        recent_rooms=["Lobby"],
        command_history=[],
        unfinished_boards=[],
        activity_baseline={},
        behavioral_patterns={}
    )


class TestSupportBotIntegration:
    """Integration tests for complete Support Bot flow."""
    
    @pytest.mark.asyncio
    async def test_complete_support_flow_sadness(
        self,
        sentiment_analyzer,
        support_bot,
        mock_gemini_service,
        user_profile
    ):
        """Test complete flow for sadness detection and support."""
        # Step 1: Analyze sentiment
        message = "I'm feeling really sad and lonely today"
        sentiment = sentiment_analyzer.analyze(message)
        
        assert sentiment.emotion == EmotionType.SADNESS
        assert sentiment.requires_support
        assert sentiment.crisis_type == CrisisType.NONE
        
        # Step 2: Generate greeting
        mock_gemini_service._generate_content.return_value = (
            "I noticed you're feeling sad. I'm here to listen. What's been going on?"
        )
        
        greeting = await support_bot.generate_greeting(
            user_profile,
            message,
            sentiment
        )
        
        assert greeting
        assert "listen" in greeting.lower() or "here" in greeting.lower()
        
        # Step 3: Generate response to follow-up
        mock_gemini_service._generate_content.return_value = (
            "That sounds really difficult. Can you tell me more about what's making you feel this way?"
        )
        
        conversation_history = [
            {"role": "bot", "content": greeting},
            {"role": "user", "content": "Everything just feels overwhelming"}
        ]
        
        response = await support_bot.generate_response(
            "Everything just feels overwhelming",
            user_profile,
            conversation_history
        )
        
        assert response
        assert "?" in response  # Should include a question
    
    @pytest.mark.asyncio
    async def test_complete_crisis_flow(
        self,
        sentiment_analyzer,
        support_bot,
        user_profile
    ):
        """Test complete flow for crisis detection."""
        # Step 1: Analyze sentiment with crisis keywords
        message = "I want to hurt myself"
        sentiment = sentiment_analyzer.analyze(message)
        
        assert sentiment.crisis_type == CrisisType.SELF_HARM
        
        # Step 2: Generate crisis response (no conversational support)
        crisis_response = support_bot.generate_crisis_response(sentiment.crisis_type)
        
        assert crisis_response
        assert "AASRA" in crisis_response or "hotline" in crisis_response.lower()
        assert "91-9820466726" in crisis_response or "1860-2662-345" in crisis_response
        assert "professional" in crisis_response.lower()
    
    @pytest.mark.asyncio
    async def test_anxiety_support_flow(
        self,
        sentiment_analyzer,
        support_bot,
        mock_gemini_service,
        user_profile
    ):
        """Test support flow for anxiety."""
        # Analyze anxiety message
        message = "I'm so anxious and worried about everything"
        sentiment = sentiment_analyzer.analyze(message)
        
        assert sentiment.emotion == EmotionType.ANXIETY
        assert sentiment.requires_support
        
        # Generate greeting
        mock_gemini_service._generate_content.return_value = (
            "I can see you're feeling anxious. I'm here to support you. What's worrying you?"
        )
        
        greeting = await support_bot.generate_greeting(
            user_profile,
            message,
            sentiment
        )
        
        assert greeting
        assert "anxious" in greeting.lower() or "worried" in greeting.lower()
    
    @pytest.mark.asyncio
    async def test_anger_support_flow(
        self,
        sentiment_analyzer,
        support_bot,
        mock_gemini_service,
        user_profile
    ):
        """Test support flow for anger."""
        # Analyze anger message
        message = "I'm so angry and frustrated with everything"
        sentiment = sentiment_analyzer.analyze(message)
        
        assert sentiment.emotion == EmotionType.ANGER
        assert sentiment.requires_support
        
        # Generate greeting
        mock_gemini_service._generate_content.return_value = (
            "I can see you're feeling frustrated. I'm here to listen without judgment."
        )
        
        greeting = await support_bot.generate_greeting(
            user_profile,
            message,
            sentiment
        )
        
        assert greeting
    
    @pytest.mark.asyncio
    async def test_no_support_needed_flow(
        self,
        sentiment_analyzer,
        support_bot,
        user_profile
    ):
        """Test flow when no support is needed."""
        # Analyze neutral message
        message = "Hello, how are you?"
        sentiment = sentiment_analyzer.analyze(message)
        
        assert sentiment.emotion == EmotionType.NEUTRAL
        assert not sentiment.requires_support
        assert sentiment.crisis_type == CrisisType.NONE
        
        # No support bot activation should occur
    
    @pytest.mark.asyncio
    async def test_fallback_mechanisms(
        self,
        sentiment_analyzer,
        support_bot,
        mock_gemini_service,
        user_profile
    ):
        """Test that fallback mechanisms work when API fails."""
        # Analyze message
        message = "I'm feeling really down"
        sentiment = sentiment_analyzer.analyze(message)
        
        # Simulate API failure
        from backend.vecna.gemini_service import GeminiServiceError
        mock_gemini_service._generate_content.side_effect = GeminiServiceError("API Error")
        
        # Should still get a greeting (fallback)
        greeting = await support_bot.generate_greeting(
            user_profile,
            message,
            sentiment
        )
        
        assert greeting
        assert "listen" in greeting.lower() or "support" in greeting.lower()
        
        # Should still get a response (fallback)
        response = await support_bot.generate_response(
            "I need help",
            user_profile,
            []
        )
        
        assert response
        assert "?" in response
    
    def test_crisis_types_have_hotlines(self, support_bot):
        """Test that all crisis types have appropriate hotlines."""
        crisis_types = [
            CrisisType.SELF_HARM,
            CrisisType.SUICIDE,
            CrisisType.ABUSE
        ]
        
        for crisis_type in crisis_types:
            response = support_bot.generate_crisis_response(crisis_type)
            assert response
            assert len(response) > 0
            # Should contain phone numbers (various formats)
            import re
            # Match patterns like: 1091, 91-9820466726, 1860-2662-345, 7827-170-170
            # More flexible pattern to match numbers with optional dashes
            phone_pattern = r'\d+'
            matches = re.findall(phone_pattern, response)
            # Should have at least one number sequence (phone number)
            assert len(matches) > 0
            # At least one match should be 4+ digits (a phone number)
            assert any(len(match) >= 4 for match in matches)
