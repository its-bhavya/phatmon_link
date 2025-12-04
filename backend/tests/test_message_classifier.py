"""
Tests for Message Classifier.

Requirements: 2.1, 2.2, 2.3, 2.5
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.instant_answer.classifier import (
    MessageClassifier,
    MessageClassification,
    MessageType
)


class TestMessageClassifier:
    """Test suite for message classification."""
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock Gemini service."""
        service = MagicMock()
        service._generate_content = AsyncMock()
        return service
    
    @pytest.fixture
    def classifier(self, mock_gemini_service):
        """Create a message classifier with mock service."""
        return MessageClassifier(mock_gemini_service)
    
    def test_code_detection_fenced_blocks(self, classifier):
        """Test detection of markdown fenced code blocks."""
        message = """
        Here's how to do it:
        ```python
        def hello():
            print("world")
        ```
        """
        assert classifier._detect_code_blocks(message) is True
    
    def test_code_detection_inline_code(self, classifier):
        """Test detection of inline code."""
        message = "You can use `print('hello')` to output text"
        assert classifier._detect_code_blocks(message) is True
    
    def test_code_detection_indented_blocks(self, classifier):
        """Test detection of indented code blocks."""
        message = """
        Try this:
        
            def hello():
                print("world")
        """
        assert classifier._detect_code_blocks(message) is True
    
    def test_code_detection_function_patterns(self, classifier):
        """Test detection of function definition patterns."""
        message = "You need to define function myFunction() { return true; }"
        assert classifier._detect_code_blocks(message) is True
    
    def test_code_detection_no_code(self, classifier):
        """Test that regular text is not detected as code."""
        message = "This is just a regular message without any code"
        assert classifier._detect_code_blocks(message) is False
    
    @pytest.mark.asyncio
    async def test_classify_question(self, classifier, mock_gemini_service):
        """Test classification of a question message."""
        mock_gemini_service._generate_content.return_value = """
TYPE: question
CONFIDENCE: 0.95
REASONING: Contains interrogative word and seeks help
"""
        
        result = await classifier.classify("How do I fix this error?")
        
        assert result.message_type == MessageType.QUESTION
        assert result.confidence == 0.95
        assert result.contains_code is False
        assert "interrogative" in result.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_classify_answer_with_code(self, classifier, mock_gemini_service):
        """Test classification of an answer with code."""
        mock_gemini_service._generate_content.return_value = """
TYPE: answer
CONFIDENCE: 0.88
REASONING: Provides code example and solution
"""
        
        message = """
        Try this:
        ```python
        print("hello")
        ```
        """
        
        result = await classifier.classify(message)
        
        assert result.message_type == MessageType.ANSWER
        assert result.confidence == 0.88
        assert result.contains_code is True
        assert "solution" in result.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_classify_discussion(self, classifier, mock_gemini_service):
        """Test classification of a discussion message."""
        mock_gemini_service._generate_content.return_value = """
TYPE: discussion
CONFIDENCE: 0.92
REASONING: General comment without question or solution
"""
        
        result = await classifier.classify("That's interesting!")
        
        assert result.message_type == MessageType.DISCUSSION
        assert result.confidence == 0.92
        assert result.contains_code is False
    
    @pytest.mark.asyncio
    async def test_classify_handles_malformed_response(self, classifier, mock_gemini_service):
        """Test that classifier handles malformed API responses gracefully."""
        mock_gemini_service._generate_content.return_value = "Invalid response format"
        
        result = await classifier.classify("Some message")
        
        # Should default to DISCUSSION with 0.5 confidence
        assert result.message_type == MessageType.DISCUSSION
        assert result.confidence == 0.5
    
    @pytest.mark.asyncio
    async def test_classify_clamps_confidence(self, classifier, mock_gemini_service):
        """Test that confidence values are clamped to valid range."""
        mock_gemini_service._generate_content.return_value = """
TYPE: question
CONFIDENCE: 1.5
REASONING: Test
"""
        
        result = await classifier.classify("Test message")
        
        # Confidence should be clamped to 1.0
        assert result.confidence == 1.0
    
    def test_parse_classification_response(self, classifier):
        """Test parsing of classification response."""
        response = """
TYPE: answer
CONFIDENCE: 0.85
REASONING: Provides technical solution
"""
        
        message_type, confidence, reasoning = classifier._parse_classification_response(response)
        
        assert message_type == MessageType.ANSWER
        assert confidence == 0.85
        assert reasoning == "Provides technical solution"
    
    def test_parse_classification_response_defaults(self, classifier):
        """Test that parsing uses defaults for missing fields."""
        response = "Invalid format"
        
        message_type, confidence, reasoning = classifier._parse_classification_response(response)
        
        assert message_type == MessageType.DISCUSSION
        assert confidence == 0.5
        assert "Unable to parse" in reasoning
