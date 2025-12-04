"""
Integration tests for Message Classifier with Gemini service.

Requirements: 2.1, 2.2, 2.3, 2.5
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.instant_answer.classifier import MessageClassifier, MessageType


class TestMessageClassifierIntegration:
    """Integration tests for message classifier."""
    
    @pytest.fixture
    def gemini_service(self):
        """Create a mock Gemini service that simulates real API responses."""
        service = MagicMock()
        
        async def mock_generate(prompt, operation=None):
            # Extract the message being classified from the prompt
            # The message is in quotes after "Message to classify:"
            import re
            match = re.search(r'Message to classify:\s*"([^"]*)"', prompt, re.DOTALL)
            if not match:
                return """TYPE: discussion
CONFIDENCE: 0.5
REASONING: Unable to parse message"""
            
            message = match.group(1).lower()
            
            # Simulate realistic Gemini API responses based on message content
            if any(word in message for word in ["how do", "what is", "why", "when", "where", "?"]):
                return """TYPE: question
CONFIDENCE: 0.92
REASONING: Contains interrogative pattern and seeks information"""
            elif any(phrase in message for phrase in ["try this", "you can", "here's how", "use the"]):
                return """TYPE: answer
CONFIDENCE: 0.88
REASONING: Provides solution with instructional language"""
            else:
                return """TYPE: discussion
CONFIDENCE: 0.85
REASONING: General conversational content"""
        
        service._generate_content = AsyncMock(side_effect=mock_generate)
        return service
    
    @pytest.mark.asyncio
    async def test_classify_real_question(self, gemini_service):
        """Test classification of a realistic question."""
        classifier = MessageClassifier(gemini_service)
        
        result = await classifier.classify("How do I implement JWT authentication in FastAPI?")
        
        assert result.message_type == MessageType.QUESTION
        assert result.confidence > 0.8
        assert result.contains_code is False
    
    @pytest.mark.asyncio
    async def test_classify_real_answer_with_code(self, gemini_service):
        """Test classification of a realistic answer with code."""
        classifier = MessageClassifier(gemini_service)
        
        message = """Try this approach:
```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```
This will set up the OAuth2 flow."""
        
        result = await classifier.classify(message)
        
        assert result.message_type == MessageType.ANSWER
        assert result.confidence > 0.8
        assert result.contains_code is True
    
    @pytest.mark.asyncio
    async def test_classify_real_discussion(self, gemini_service):
        """Test classification of a realistic discussion message."""
        classifier = MessageClassifier(gemini_service)
        
        result = await classifier.classify("That's a great point! I hadn't thought of it that way.")
        
        assert result.message_type == MessageType.DISCUSSION
        assert result.confidence > 0.8
        assert result.contains_code is False
    
    @pytest.mark.asyncio
    async def test_code_detection_various_formats(self, gemini_service):
        """Test code detection across various formats."""
        classifier = MessageClassifier(gemini_service)
        
        # Test fenced code
        result1 = await classifier.classify("```js\nconst x = 5;\n```")
        assert result1.contains_code is True
        
        # Test inline code
        result2 = await classifier.classify("Use the `print()` function")
        assert result2.contains_code is True
        
        # Test no code
        result3 = await classifier.classify("This is just text")
        assert result3.contains_code is False
    
    @pytest.mark.asyncio
    async def test_classifier_error_handling(self, gemini_service):
        """Test that classifier properly propagates errors."""
        classifier = MessageClassifier(gemini_service)
        
        # Make the service raise an error
        gemini_service._generate_content = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception) as exc_info:
            await classifier.classify("Test message")
        
        assert "API Error" in str(exc_info.value)
