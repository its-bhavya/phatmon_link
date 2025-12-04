"""
Unit tests for Support Bot.

Tests greeting generation, empathetic response generation, and crisis response
for the Empathetic Support Bot module.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.support.bot import SupportBot
from backend.support.sentiment import SentimentResult, EmotionType, CrisisType
from backend.vecna.user_profile import UserProfile
from backend.vecna.gemini_service import GeminiService, GeminiServiceError


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock(spec=GeminiService)
    service._generate_content = AsyncMock()
    return service


@pytest.fixture
def support_bot(mock_gemini_service):
    """Create a SupportBot instance with mocked Gemini service."""
    return SupportBot(mock_gemini_service)


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return UserProfile(
        user_id=1,
        interests=["programming", "music", "reading"],
        frequent_rooms={"Lobby": 10, "Techline": 5},
        recent_rooms=["Lobby", "Techline"],
        command_history=[],
        unfinished_boards=[],
        activity_baseline={},
        behavioral_patterns={}
    )


@pytest.fixture
def sample_sentiment():
    """Create a sample sentiment result."""
    return SentimentResult(
        emotion=EmotionType.SADNESS,
        intensity=0.8,
        requires_support=True,
        crisis_type=CrisisType.NONE,
        keywords=["sad", "lonely"]
    )


class TestSupportBotGreeting:
    """Test suite for greeting message generation."""
    
    @pytest.mark.asyncio
    async def test_generate_greeting_success(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile,
        sample_sentiment
    ):
        """Test successful greeting generation."""
        # Setup mock response
        mock_gemini_service._generate_content.return_value = (
            "I noticed you might be going through something difficult. "
            "I'm here to listen and support you. What's been happening?"
        )
        
        result = await support_bot.generate_greeting(
            sample_user_profile,
            "I'm feeling really sad today",
            sample_sentiment
        )
        
        assert "listen" in result.lower() or "support" in result.lower()
        assert mock_gemini_service._generate_content.called
    
    @pytest.mark.asyncio
    async def test_generate_greeting_with_anger(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile
    ):
        """Test greeting generation for anger emotion."""
        sentiment = SentimentResult(
            emotion=EmotionType.ANGER,
            intensity=0.9,
            requires_support=True,
            crisis_type=CrisisType.NONE,
            keywords=["angry", "furious"]
        )
        
        mock_gemini_service._generate_content.return_value = (
            "I can see you're feeling frustrated. I'm here to listen without judgment."
        )
        
        result = await support_bot.generate_greeting(
            sample_user_profile,
            "I'm so angry about this",
            sentiment
        )
        
        assert result
        assert mock_gemini_service._generate_content.called
    
    @pytest.mark.asyncio
    async def test_generate_greeting_fallback(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile,
        sample_sentiment
    ):
        """Test fallback greeting when API fails."""
        # Setup mock to raise exception
        mock_gemini_service._generate_content.side_effect = GeminiServiceError("API Error")
        
        result = await support_bot.generate_greeting(
            sample_user_profile,
            "I'm feeling sad",
            sample_sentiment
        )
        
        # Should return fallback greeting
        assert result
        assert "listen" in result.lower() or "support" in result.lower()
        assert "AI" in result or "therapist" in result.lower()


class TestSupportBotResponse:
    """Test suite for empathetic response generation."""
    
    @pytest.mark.asyncio
    async def test_generate_response_success(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile
    ):
        """Test successful response generation."""
        mock_gemini_service._generate_content.return_value = (
            "That sounds really difficult. What part feels most challenging right now?"
        )
        
        conversation_history = [
            {"role": "bot", "content": "How are you feeling?"},
            {"role": "user", "content": "Not great"}
        ]
        
        result = await support_bot.generate_response(
            "I'm struggling with everything",
            sample_user_profile,
            conversation_history
        )
        
        assert result
        assert mock_gemini_service._generate_content.called
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile
    ):
        """Test response generation includes user context."""
        mock_gemini_service._generate_content.return_value = (
            "I hear you. Have you tried taking a break with some music?"
        )
        
        result = await support_bot.generate_response(
            "I'm feeling overwhelmed",
            sample_user_profile,
            []
        )
        
        assert result
        # Verify the prompt included user context
        call_args = mock_gemini_service._generate_content.call_args
        prompt = call_args[0][0]
        assert "programming" in prompt or "music" in prompt or "reading" in prompt
    
    @pytest.mark.asyncio
    async def test_generate_response_fallback(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile
    ):
        """Test fallback response when API fails."""
        mock_gemini_service._generate_content.side_effect = GeminiServiceError("API Error")
        
        result = await support_bot.generate_response(
            "I need help",
            sample_user_profile,
            []
        )
        
        # Should return fallback response
        assert result
        assert "?" in result  # Fallback responses include questions
    
    @pytest.mark.asyncio
    async def test_generate_response_with_conversation_history(
        self,
        support_bot,
        mock_gemini_service,
        sample_user_profile
    ):
        """Test response generation with conversation history."""
        mock_gemini_service._generate_content.return_value = (
            "I understand. Can you tell me more about that?"
        )
        
        conversation_history = [
            {"role": "bot", "content": "What's on your mind?"},
            {"role": "user", "content": "I'm worried about work"},
            {"role": "bot", "content": "Tell me more about that"},
            {"role": "user", "content": "It's just too much"}
        ]
        
        result = await support_bot.generate_response(
            "I don't know what to do",
            sample_user_profile,
            conversation_history
        )
        
        assert result
        # Verify conversation history was included in prompt
        call_args = mock_gemini_service._generate_content.call_args
        prompt = call_args[0][0]
        assert "worried about work" in prompt or "Conversation History" in prompt


class TestSupportBotCrisisResponse:
    """Test suite for crisis response generation."""
    
    def test_generate_crisis_response_self_harm(self, support_bot):
        """Test crisis response for self-harm."""
        result = support_bot.generate_crisis_response(CrisisType.SELF_HARM)
        
        assert result
        assert "AASRA" in result or "hotline" in result.lower()
        assert "91-9820466726" in result or "1860-2662-345" in result
    
    def test_generate_crisis_response_suicide(self, support_bot):
        """Test crisis response for suicide."""
        result = support_bot.generate_crisis_response(CrisisType.SUICIDE)
        
        assert result
        assert "AASRA" in result or "Sneha" in result
        assert "91-9820466726" in result or "91-44-24640050" in result
    
    def test_generate_crisis_response_abuse(self, support_bot):
        """Test crisis response for abuse."""
        result = support_bot.generate_crisis_response(CrisisType.ABUSE)
        
        assert result
        assert "1091" in result or "1098" in result
        assert "Helpline" in result or "Childline" in result
    
    def test_generate_crisis_response_none(self, support_bot):
        """Test crisis response when no crisis detected."""
        result = support_bot.generate_crisis_response(CrisisType.NONE)
        
        assert result == ""


class TestSupportBotPromptGeneration:
    """Test suite for prompt generation methods."""
    
    def test_greeting_prompt_includes_context(
        self,
        support_bot,
        sample_user_profile,
        sample_sentiment
    ):
        """Test that greeting prompt includes user context."""
        prompt = support_bot._create_greeting_prompt(
            sample_user_profile,
            "I'm feeling really down",
            sample_sentiment
        )
        
        assert "programming" in prompt or "music" in prompt
        assert "Lobby" in prompt or "Techline" in prompt
        assert "feeling really down" in prompt
        assert "sadness" in prompt.lower() or "distress" in prompt.lower()
    
    def test_greeting_prompt_includes_boundaries(
        self,
        support_bot,
        sample_user_profile,
        sample_sentiment
    ):
        """Test that greeting prompt includes appropriate boundaries."""
        prompt = support_bot._create_greeting_prompt(
            sample_user_profile,
            "I need help",
            sample_sentiment
        )
        
        assert "NOT diagnose" in prompt or "not a therapist" in prompt.lower()
        assert "BOUNDARIES" in prompt or "boundaries" in prompt.lower()
    
    def test_empathetic_prompt_includes_context(
        self,
        support_bot,
        sample_user_profile
    ):
        """Test that empathetic prompt includes user context."""
        conversation_history = [
            {"role": "user", "content": "I'm struggling"}
        ]
        
        prompt = support_bot._create_empathetic_prompt(
            "Everything feels overwhelming",
            sample_user_profile,
            conversation_history
        )
        
        assert "programming" in prompt or "music" in prompt
        assert "struggling" in prompt
        assert "overwhelming" in prompt
    
    def test_empathetic_prompt_includes_boundaries(
        self,
        support_bot,
        sample_user_profile
    ):
        """Test that empathetic prompt includes critical boundaries."""
        prompt = support_bot._create_empathetic_prompt(
            "I need advice",
            sample_user_profile,
            []
        )
        
        assert "NEVER diagnose" in prompt or "never diagnose" in prompt.lower()
        assert "BOUNDARIES" in prompt or "boundaries" in prompt.lower()
        assert "depression" in prompt  # As an example of what NOT to say


class TestSupportBotFallbacks:
    """Test suite for fallback mechanisms."""
    
    def test_fallback_greeting_for_sadness(self, support_bot):
        """Test fallback greeting for sadness."""
        sentiment = SentimentResult(
            emotion=EmotionType.SADNESS,
            intensity=0.8,
            requires_support=True,
            crisis_type=CrisisType.NONE,
            keywords=["sad"]
        )
        
        result = support_bot._fallback_greeting(sentiment)
        
        assert result
        assert "listen" in result.lower() or "support" in result.lower()
        assert "AI" in result or "therapist" in result.lower()
    
    def test_fallback_greeting_for_anxiety(self, support_bot):
        """Test fallback greeting for anxiety."""
        sentiment = SentimentResult(
            emotion=EmotionType.ANXIETY,
            intensity=0.9,
            requires_support=True,
            crisis_type=CrisisType.NONE,
            keywords=["anxious"]
        )
        
        result = support_bot._fallback_greeting(sentiment)
        
        assert result
        assert "worried" in result.lower() or "anxious" in result.lower()
    
    def test_fallback_response_includes_question(self, support_bot):
        """Test that fallback response includes a question."""
        result = support_bot._fallback_response()
        
        assert result
        assert "?" in result
    
    def test_fallback_response_is_empathetic(self, support_bot):
        """Test that fallback response is empathetic."""
        result = support_bot._fallback_response()
        
        assert result
        # Should include empathetic language
        empathetic_words = ["hear", "understand", "listening", "help", "feel"]
        assert any(word in result.lower() for word in empathetic_words)
