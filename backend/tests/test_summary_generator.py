"""
Unit tests for AI Summary Generator.

Tests cover:
- Summary generation from multiple results
- Code snippet preservation
- Source attribution
- Novel question detection
- Confidence calculation

Requirements: 4.2, 4.4, 4.5
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from backend.instant_answer.summary_generator import (
    SummaryGenerator,
    InstantAnswer
)
from backend.instant_answer.search_engine import SearchResult
from backend.instant_answer.tagger import MessageTags


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = MagicMock()
    service._generate_content = AsyncMock()
    return service


@pytest.fixture
def summary_generator(mock_gemini_service):
    """Create a SummaryGenerator instance with mock service."""
    return SummaryGenerator(mock_gemini_service, max_summary_tokens=300)


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    base_time = datetime.now() - timedelta(days=7)
    
    return [
        SearchResult(
            message_id="msg_001",
            message_text="You can use FastAPI's OAuth2PasswordBearer. Here's code:\n```python\noauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"token\")\n```",
            username="alice",
            timestamp=base_time,
            similarity_score=0.92,
            tags=MessageTags(
                topic_tags=["authentication"],
                tech_keywords=["FastAPI", "OAuth2"],
                contains_code=True,
                code_language="python"
            ),
            room="Techline"
        ),
        SearchResult(
            message_id="msg_002",
            message_text="Don't forget to verify the JWT token signature.",
            username="bob",
            timestamp=base_time + timedelta(hours=2),
            similarity_score=0.88,
            tags=MessageTags(
                topic_tags=["authentication"],
                tech_keywords=["JWT"],
                contains_code=False,
                code_language=None
            ),
            room="Techline"
        )
    ]


@pytest.mark.asyncio
async def test_generate_summary_with_results(summary_generator, mock_gemini_service, sample_search_results):
    """Test summary generation with valid search results."""
    # Mock Gemini response
    mock_gemini_service._generate_content.return_value = (
        "To implement JWT authentication in FastAPI, use OAuth2PasswordBearer. "
        "Make sure to verify the token signature."
    )
    
    question = "How do I implement JWT authentication?"
    answer = await summary_generator.generate_summary(question, sample_search_results)
    
    # Verify InstantAnswer structure
    assert isinstance(answer, InstantAnswer)
    assert answer.summary is not None
    assert len(answer.summary) > 0
    assert answer.source_messages == sample_search_results
    assert 0.0 <= answer.confidence <= 1.0
    assert answer.is_novel_question is False
    
    # Verify Gemini was called
    mock_gemini_service._generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_novel_question_detection(summary_generator):
    """Test detection of novel questions with no search results."""
    question = "How do I implement quantum computing in my toaster?"
    answer = await summary_generator.generate_summary(question, [])
    
    # Verify novel question handling
    assert answer.is_novel_question is True
    assert "novel question" in answer.summary.lower()
    assert len(answer.source_messages) == 0
    assert answer.confidence == 1.0


@pytest.mark.asyncio
async def test_code_snippet_extraction(summary_generator, sample_search_results):
    """Test extraction of code snippets from search results."""
    code_snippets = summary_generator._extract_code_snippets(sample_search_results)
    
    # Verify code extraction
    assert len(code_snippets) > 0
    assert any("```" in snippet for snippet in code_snippets)
    assert any("OAuth2PasswordBearer" in snippet for snippet in code_snippets)


@pytest.mark.asyncio
async def test_code_snippet_preservation(summary_generator, mock_gemini_service, sample_search_results):
    """Test that code snippets are preserved in the summary."""
    # Mock Gemini response with code
    mock_gemini_service._generate_content.return_value = (
        "Use this code:\n```python\noauth2_scheme = OAuth2PasswordBearer()\n```"
    )
    
    question = "Show me JWT code"
    answer = await summary_generator.generate_summary(question, sample_search_results)
    
    # Verify code is in summary
    assert "```" in answer.summary


@pytest.mark.asyncio
async def test_source_attribution(summary_generator, mock_gemini_service, sample_search_results):
    """Test that source attribution is added to summaries."""
    mock_gemini_service._generate_content.return_value = "Here's the answer."
    
    question = "Test question"
    answer = await summary_generator.generate_summary(question, sample_search_results)
    
    # Verify source attribution
    assert "Sources:" in answer.summary
    assert "alice" in answer.summary
    assert "bob" in answer.summary
    # Check for timestamps (format: YYYY-MM-DD HH:MM)
    assert any(char.isdigit() for char in answer.summary)


@pytest.mark.asyncio
async def test_confidence_calculation_multiple_results(summary_generator):
    """Test confidence calculation with multiple high-similarity results."""
    high_similarity_results = [
        SearchResult(
            message_id=f"msg_{i}",
            message_text="Test message",
            username="user",
            timestamp=datetime.now(),
            similarity_score=0.9,
            tags=MessageTags([], [], True, None),
            room="Techline"
        )
        for i in range(5)
    ]
    
    confidence = summary_generator._calculate_confidence(high_similarity_results)
    
    # High similarity + multiple results + code = high confidence
    assert confidence > 0.7


@pytest.mark.asyncio
async def test_confidence_calculation_single_result(summary_generator):
    """Test confidence calculation with single result."""
    single_result = [
        SearchResult(
            message_id="msg_1",
            message_text="Test",
            username="user",
            timestamp=datetime.now(),
            similarity_score=0.8,
            tags=MessageTags([], [], False, None),
            room="Techline"
        )
    ]
    
    confidence = summary_generator._calculate_confidence(single_result)
    
    # Single result = lower confidence
    assert 0.5 < confidence < 0.8


@pytest.mark.asyncio
async def test_confidence_calculation_empty_results(summary_generator):
    """Test confidence calculation with no results."""
    confidence = summary_generator._calculate_confidence([])
    assert confidence == 0.0


@pytest.mark.asyncio
async def test_summary_prompt_creation(summary_generator, sample_search_results):
    """Test that summary prompt is properly formatted."""
    question = "Test question"
    code_snippets = ["```python\ntest_code()\n```"]
    
    prompt = summary_generator._create_summary_prompt(
        question,
        sample_search_results,
        code_snippets
    )
    
    # Verify prompt contains key elements
    assert question in prompt
    assert "alice" in prompt
    assert "bob" in prompt
    assert "similarity" in prompt.lower()
    assert "code" in prompt.lower()


@pytest.mark.asyncio
async def test_source_attribution_limits_to_five(summary_generator, mock_gemini_service):
    """Test that source attribution limits to top 5 sources."""
    # Create 10 search results
    many_results = [
        SearchResult(
            message_id=f"msg_{i}",
            message_text=f"Message {i}",
            username=f"user{i}",
            timestamp=datetime.now() - timedelta(hours=i),
            similarity_score=0.9 - (i * 0.05),
            tags=MessageTags([], [], False, None),
            room="Techline"
        )
        for i in range(10)
    ]
    
    mock_gemini_service._generate_content.return_value = "Answer"
    
    answer = await summary_generator.generate_summary("Question", many_results)
    
    # Count source attributions
    source_count = answer.summary.count("user")
    assert source_count <= 5


@pytest.mark.asyncio
async def test_error_handling_propagates(summary_generator, mock_gemini_service, sample_search_results):
    """Test that errors from Gemini service are propagated."""
    # Mock Gemini to raise an error
    mock_gemini_service._generate_content.side_effect = Exception("API Error")
    
    question = "Test question"
    
    with pytest.raises(Exception) as exc_info:
        await summary_generator.generate_summary(question, sample_search_results)
    
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_max_summary_tokens_configuration(mock_gemini_service):
    """Test that max_summary_tokens is configurable."""
    generator = SummaryGenerator(mock_gemini_service, max_summary_tokens=500)
    assert generator.max_summary_tokens == 500


@pytest.mark.asyncio
async def test_inline_code_extraction(summary_generator):
    """Test extraction of inline code snippets."""
    results = [
        SearchResult(
            message_id="msg_1",
            message_text="Use the `OAuth2PasswordBearer` class for authentication.",
            username="user",
            timestamp=datetime.now(),
            similarity_score=0.9,
            tags=MessageTags([], [], True, None),
            room="Techline"
        )
    ]
    
    code_snippets = summary_generator._extract_code_snippets(results)
    
    # Should extract inline code (at least 10 chars)
    assert len(code_snippets) > 0
    assert any("OAuth2PasswordBearer" in snippet for snippet in code_snippets)
