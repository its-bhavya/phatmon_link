"""
Tests for Auto-Tagger.

Requirements: 5.1, 5.2, 5.4
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.instant_answer.tagger import (
    AutoTagger,
    MessageTags
)


class TestAutoTagger:
    """Test suite for auto-tagging."""
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock Gemini service."""
        service = MagicMock()
        service._generate_content = AsyncMock()
        return service
    
    @pytest.fixture
    def tagger(self, mock_gemini_service):
        """Create an auto-tagger with mock service."""
        return AutoTagger(mock_gemini_service)
    
    def test_code_detection_fenced_blocks(self, tagger):
        """Test detection of markdown fenced code blocks."""
        message = """
        Here's how to do it:
        ```python
        def hello():
            print("world")
        ```
        """
        assert tagger._detect_code_blocks(message) is True
    
    def test_code_detection_inline_code(self, tagger):
        """Test detection of inline code."""
        message = "You can use `print('hello')` to output text"
        assert tagger._detect_code_blocks(message) is True
    
    def test_code_detection_no_code(self, tagger):
        """Test that regular text is not detected as code."""
        message = "This is just a regular message without any code"
        assert tagger._detect_code_blocks(message) is False
    
    def test_detect_code_language_python(self, tagger):
        """Test detection of Python code."""
        message = """
        ```python
        def hello():
            print("world")
        ```
        """
        assert tagger._detect_code_language(message) == "python"
    
    def test_detect_code_language_javascript(self, tagger):
        """Test detection of JavaScript code."""
        message = """
        ```javascript
        function hello() {
            console.log("world");
        }
        ```
        """
        assert tagger._detect_code_language(message) == "javascript"
    
    def test_detect_code_language_from_patterns(self, tagger):
        """Test language detection from code patterns."""
        # Python pattern
        python_msg = "def my_function():\n    return True"
        assert tagger._detect_code_language(python_msg) == "python"
        
        # JavaScript pattern
        js_msg = "const myFunc = () => { return true; }"
        assert tagger._detect_code_language(js_msg) == "javascript"
    
    def test_detect_code_language_none(self, tagger):
        """Test that no language is detected for non-code."""
        message = "This is just regular text"
        assert tagger._detect_code_language(message) is None
    
    @pytest.mark.asyncio
    async def test_tag_message_with_topics_and_tech(self, tagger, mock_gemini_service):
        """Test tagging a message with topics and tech keywords."""
        mock_gemini_service._generate_content.return_value = """
TOPICS: authentication, security, api
TECH: jwt, fastapi, python
"""
        
        message = "How do I implement JWT authentication in FastAPI?"
        result = await tagger.tag_message(message)
        
        assert result.topic_tags == ["authentication", "security", "api"]
        assert result.tech_keywords == ["jwt", "fastapi", "python"]
        assert result.contains_code is False
        assert result.code_language is None
    
    @pytest.mark.asyncio
    async def test_tag_message_with_code(self, tagger, mock_gemini_service):
        """Test tagging a message with code."""
        mock_gemini_service._generate_content.return_value = """
TOPICS: debugging, performance
TECH: react, javascript
"""
        
        message = """
        My React component is slow:
        ```javascript
        const MyComponent = () => {
            return <div>Hello</div>;
        }
        ```
        """
        
        result = await tagger.tag_message(message)
        
        assert result.topic_tags == ["debugging", "performance"]
        assert result.tech_keywords == ["react", "javascript"]
        assert result.contains_code is True
        assert result.code_language == "javascript"
    
    @pytest.mark.asyncio
    async def test_tag_message_empty_tags(self, tagger, mock_gemini_service):
        """Test tagging a message with no clear topics or tech."""
        mock_gemini_service._generate_content.return_value = """
TOPICS: 
TECH: 
"""
        
        message = "Thanks for the help!"
        result = await tagger.tag_message(message)
        
        assert result.topic_tags == []
        assert result.tech_keywords == []
        assert result.contains_code is False
        assert result.code_language is None
    
    def test_parse_tagging_response(self, tagger):
        """Test parsing of tagging response."""
        response = """
TOPICS: authentication, security, api
TECH: jwt, fastapi, python
"""
        
        topics, tech = tagger._parse_tagging_response(response)
        
        assert topics == ["authentication", "security", "api"]
        assert tech == ["jwt", "fastapi", "python"]
    
    def test_parse_tagging_response_with_whitespace(self, tagger):
        """Test parsing handles extra whitespace."""
        response = """
TOPICS:  authentication ,  security  , api  
TECH:  jwt,  fastapi,  python  
"""
        
        topics, tech = tagger._parse_tagging_response(response)
        
        assert topics == ["authentication", "security", "api"]
        assert tech == ["jwt", "fastapi", "python"]
    
    def test_parse_tagging_response_deduplicates(self, tagger):
        """Test parsing removes duplicates."""
        response = """
TOPICS: authentication, security, authentication
TECH: python, fastapi, python
"""
        
        topics, tech = tagger._parse_tagging_response(response)
        
        assert topics == ["authentication", "security"]
        assert tech == ["python", "fastapi"]
    
    def test_parse_tagging_response_empty(self, tagger):
        """Test parsing handles empty tags."""
        response = """
TOPICS: 
TECH: 
"""
        
        topics, tech = tagger._parse_tagging_response(response)
        
        assert topics == []
        assert tech == []
    
    def test_parse_tagging_response_malformed(self, tagger):
        """Test parsing handles malformed response."""
        response = "Invalid format"
        
        topics, tech = tagger._parse_tagging_response(response)
        
        assert topics == []
        assert tech == []
