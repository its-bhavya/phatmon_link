"""
Tests for Gemini AI Service.

This module tests the GeminiService class to ensure:
- Service initialization with API key
- Error handling for missing API key
- Fallback mechanisms when API fails
- Prompt generation for different use cases
"""

import pytest
from unittest.mock import Mock, patch
from backend.vecna.gemini_service import GeminiService, GeminiServiceError


def test_initialization_without_api_key():
    """Test that initialization fails without API key."""
    with pytest.raises(GeminiServiceError) as exc_info:
        GeminiService(api_key="")
    
    assert "GEMINI_API_KEY is required" in str(exc_info.value)


@patch('backend.vecna.gemini_service.genai')
def test_initialization_with_api_key(mock_genai):
    """Test successful initialization with API key."""
    service = GeminiService(
        api_key="test-api-key",
        model="gemini-2.0-flash-exp",
        temperature=0.9,
        max_tokens=500
    )
    
    assert service.api_key == "test-api-key"
    assert service.model_name == "gemini-2.0-flash-exp"
    assert service.temperature == 0.9
    assert service.max_tokens == 500
    
    # Verify API was configured
    mock_genai.configure.assert_called_once_with(api_key="test-api-key")


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_sysop_suggestion_success(mock_genai):
    """Test successful SysOp suggestion generation."""
    # Setup mock
    mock_response = Mock()
    mock_response.text = "You might enjoy the Techline board!"
    
    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "interests": ["programming", "technology"],
        "frequent_rooms": {"Lobby": 5, "Techline": 3}
    }
    
    result = await service.generate_sysop_suggestion(user_profile, "Looking for tech discussions")
    
    assert result == "You might enjoy the Techline board!"
    assert mock_model.generate_content.called


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_sysop_suggestion_fallback(mock_genai):
    """Test fallback when SysOp suggestion fails."""
    # Setup mock to raise exception
    mock_model = Mock()
    mock_model.generate_content = Mock(side_effect=Exception("API Error"))
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "interests": ["programming"],
        "frequent_rooms": {"Techline": 5}
    }
    
    result = await service.generate_sysop_suggestion(user_profile, "test context")
    
    # Should return fallback response
    assert "Techline" in result


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_hostile_response_success(mock_genai):
    """Test successful hostile response generation."""
    mock_response = Mock()
    mock_response.text = "wHy c@n't y0u f1gur3 th1s 0ut?"
    
    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "frequent_rooms": {"Lobby": 10},
        "behavioral_patterns": {}
    }
    
    result = await service.generate_hostile_response(
        "This is frustrating!",
        user_profile
    )
    
    assert result == "wHy c@n't y0u f1gur3 th1s 0ut?"


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_hostile_response_fallback(mock_genai):
    """Test fallback when hostile response fails."""
    mock_model = Mock()
    mock_model.generate_content = Mock(side_effect=Exception("API Error"))
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {"frequent_rooms": {}}
    
    result = await service.generate_hostile_response("test message", user_profile)
    
    # Should return one of the fallback templates
    assert any(char in result for char in ['@', '1', '3', '0'])


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_psychic_grip_narrative_success(mock_genai):
    """Test successful Psychic Grip narrative generation."""
    mock_response = Mock()
    mock_response.text = "...I see you return to the Archives... again and again..."
    
    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "frequent_rooms": {"Archives": 15},
        "recent_rooms": ["Archives", "Lobby", "Archives"],
        "unfinished_boards": ["Project X"],
        "command_history": [("help", "2024-01-01"), ("list", "2024-01-01")]
    }
    
    result = await service.generate_psychic_grip_narrative(user_profile)
    
    assert "Archives" in result or "..." in result


@patch('backend.vecna.gemini_service.genai')
@pytest.mark.asyncio
async def test_generate_psychic_grip_narrative_fallback(mock_genai):
    """Test fallback when Psychic Grip narrative fails."""
    mock_model = Mock()
    mock_model.generate_content = Mock(side_effect=Exception("API Error"))
    mock_genai.GenerativeModel.return_value = mock_model
    
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "frequent_rooms": {"Lobby": 5},
        "recent_rooms": [],
        "unfinished_boards": [],
        "command_history": []
    }
    
    result = await service.generate_psychic_grip_narrative(user_profile)
    
    # Should return fallback with corrupted text
    assert "..." in result
    assert "Lobby" in result or "w@nd3r" in result


@patch('backend.vecna.gemini_service.genai')
def test_fallback_sysop_response_with_frequent_rooms(mock_genai):
    """Test fallback SysOp response with frequent rooms."""
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "frequent_rooms": {"Techline": 10, "Lobby": 5}
    }
    
    result = service._fallback_sysop_response(user_profile)
    
    assert "Techline" in result


@patch('backend.vecna.gemini_service.genai')
def test_fallback_sysop_response_without_frequent_rooms(mock_genai):
    """Test fallback SysOp response without frequent rooms."""
    service = GeminiService(api_key="test-key")
    
    user_profile = {"frequent_rooms": {}}
    
    result = service._fallback_sysop_response(user_profile)
    
    assert "General" in result or "exploring" in result


@patch('backend.vecna.gemini_service.genai')
def test_fallback_hostile_response(mock_genai):
    """Test fallback hostile response generation."""
    service = GeminiService(api_key="test-key")
    
    result = service._fallback_hostile_response("test message")
    
    # Should contain corrupted text characters
    assert any(char in result for char in ['@', '1', '3', '0'])


@patch('backend.vecna.gemini_service.genai')
def test_fallback_psychic_grip_with_rooms(mock_genai):
    """Test fallback Psychic Grip narrative with rooms."""
    service = GeminiService(api_key="test-key")
    
    user_profile = {
        "frequent_rooms": {"Archives": 20}
    }
    
    result = service._fallback_psychic_grip_narrative(user_profile)
    
    assert "Archives" in result
    assert "..." in result


@patch('backend.vecna.gemini_service.genai')
def test_fallback_psychic_grip_without_rooms(mock_genai):
    """Test fallback Psychic Grip narrative without rooms."""
    service = GeminiService(api_key="test-key")
    
    user_profile = {"frequent_rooms": {}}
    
    result = service._fallback_psychic_grip_narrative(user_profile)
    
    assert "..." in result
    assert any(char in result for char in ['@', '1', '3', '0'])
