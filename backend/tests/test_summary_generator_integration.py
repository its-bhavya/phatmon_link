"""
Integration tests for AI Summary Generator with real Gemini API.

These tests verify the summary generator works correctly with the actual
Gemini API, testing real-world scenarios.

Requirements: 4.2, 4.4, 4.5
"""

import pytest
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from backend.vecna.gemini_service import GeminiService
from backend.instant_answer.summary_generator import SummaryGenerator
from backend.instant_answer.search_engine import SearchResult
from backend.instant_answer.tagger import MessageTags

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def gemini_service():
    """Create a real Gemini service instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set in .env file")
    return GeminiService(api_key=api_key)


@pytest.fixture
def summary_generator(gemini_service):
    """Create a SummaryGenerator with real Gemini service."""
    return SummaryGenerator(gemini_service, max_summary_tokens=300)


@pytest.fixture
def jwt_search_results():
    """Create realistic search results about JWT authentication."""
    base_time = datetime.now() - timedelta(days=7)
    
    return [
        SearchResult(
            message_id="msg_001",
            message_text="You can use FastAPI's OAuth2PasswordBearer for JWT authentication. Here's an example:\n```python\nfrom fastapi.security import OAuth2PasswordBearer\noauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"token\")\n```",
            username="alice",
            timestamp=base_time,
            similarity_score=0.92,
            tags=MessageTags(
                topic_tags=["authentication", "security"],
                tech_keywords=["FastAPI", "JWT", "OAuth2"],
                contains_code=True,
                code_language="python"
            ),
            room="Techline"
        ),
        SearchResult(
            message_id="msg_002",
            message_text="Don't forget to verify the JWT token in your dependency. You'll need to decode it and check the signature.",
            username="bob",
            timestamp=base_time + timedelta(hours=2),
            similarity_score=0.88,
            tags=MessageTags(
                topic_tags=["authentication", "security"],
                tech_keywords=["JWT"],
                contains_code=False,
                code_language=None
            ),
            room="Techline"
        ),
        SearchResult(
            message_id="msg_003",
            message_text="I use python-jose for JWT handling. Works great with FastAPI:\n```python\nfrom jose import JWTError, jwt\ntoken_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\n```",
            username="charlie",
            timestamp=base_time + timedelta(hours=5),
            similarity_score=0.85,
            tags=MessageTags(
                topic_tags=["authentication", "jwt"],
                tech_keywords=["Python", "FastAPI", "JWT", "jose"],
                contains_code=True,
                code_language="python"
            ),
            room="Techline"
        )
    ]


@pytest.mark.asyncio
async def test_generate_summary_with_real_api(summary_generator, jwt_search_results):
    """Test summary generation with real Gemini API."""
    question = "How do I implement JWT authentication in FastAPI?"
    
    answer = await summary_generator.generate_summary(question, jwt_search_results)
    
    # Verify basic structure
    assert answer is not None
    assert len(answer.summary) > 0
    assert answer.is_novel_question is False
    assert len(answer.source_messages) == 3
    assert 0.0 <= answer.confidence <= 1.0
    
    # Verify summary quality
    summary_lower = answer.summary.lower()
    assert any(keyword in summary_lower for keyword in ["jwt", "fastapi", "authentication", "oauth2"])
    
    print(f"\n{'='*70}")
    print("Generated Summary:")
    print(f"{'='*70}")
    print(answer.summary)
    print(f"{'='*70}")
    print(f"Confidence: {answer.confidence:.2f}")


@pytest.mark.asyncio
async def test_code_snippet_preservation_real_api(summary_generator, jwt_search_results):
    """Test that code snippets are preserved in real API responses."""
    question = "Show me code for JWT authentication in FastAPI"
    
    answer = await summary_generator.generate_summary(question, jwt_search_results)
    
    # Verify code blocks are present
    assert "```" in answer.summary or "`" in answer.summary
    
    # Check for specific code elements
    summary_text = answer.summary
    code_indicators = ["python", "OAuth2PasswordBearer", "jwt", "decode", "import"]
    assert any(indicator in summary_text for indicator in code_indicators)


@pytest.mark.asyncio
async def test_source_attribution_real_api(summary_generator, jwt_search_results):
    """Test that source attribution is included in real API responses."""
    question = "How do I implement JWT authentication?"
    
    answer = await summary_generator.generate_summary(question, jwt_search_results)
    
    # Verify source attribution section
    assert "Sources:" in answer.summary or "sources:" in answer.summary.lower()
    
    # Verify usernames are present
    assert "alice" in answer.summary
    assert "bob" in answer.summary
    assert "charlie" in answer.summary
    
    # Verify timestamps are present (should have date format)
    import re
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    assert re.search(date_pattern, answer.summary)


@pytest.mark.asyncio
async def test_novel_question_detection_real_api(summary_generator):
    """Test novel question detection with real API."""
    question = "How do I implement quantum entanglement in my microwave?"
    
    answer = await summary_generator.generate_summary(question, [])
    
    # Verify novel question handling
    assert answer.is_novel_question is True
    assert "novel" in answer.summary.lower()
    assert len(answer.source_messages) == 0
    assert answer.confidence == 1.0


@pytest.mark.asyncio
async def test_single_result_summary_real_api(summary_generator, jwt_search_results):
    """Test summary generation from a single search result."""
    question = "What library should I use for JWT in Python?"
    single_result = [jwt_search_results[2]]  # Just the charlie message
    
    answer = await summary_generator.generate_summary(question, single_result)
    
    # Verify summary is generated
    assert len(answer.summary) > 0
    assert answer.is_novel_question is False
    assert len(answer.source_messages) == 1
    
    # Should mention python-jose
    assert "jose" in answer.summary.lower() or "python-jose" in answer.summary.lower()


@pytest.mark.asyncio
async def test_confidence_reflects_quality_real_api(summary_generator):
    """Test that confidence score reflects result quality."""
    base_time = datetime.now()
    
    # High quality results (high similarity, multiple sources, with code)
    high_quality_results = [
        SearchResult(
            message_id=f"msg_{i}",
            message_text=f"Answer {i} with code: ```python\ncode_here()\n```",
            username=f"user{i}",
            timestamp=base_time - timedelta(hours=i),
            similarity_score=0.95,
            tags=MessageTags([], [], True, "python"),
            room="Techline"
        )
        for i in range(5)
    ]
    
    # Low quality results (low similarity, single source, no code)
    low_quality_results = [
        SearchResult(
            message_id="msg_1",
            message_text="Maybe try something?",
            username="user",
            timestamp=base_time,
            similarity_score=0.65,
            tags=MessageTags([], [], False, None),
            room="Techline"
        )
    ]
    
    high_answer = await summary_generator.generate_summary("Question", high_quality_results)
    low_answer = await summary_generator.generate_summary("Question", low_quality_results)
    
    # High quality should have higher confidence
    assert high_answer.confidence > low_answer.confidence


@pytest.mark.asyncio
async def test_summary_coherence_real_api(summary_generator, jwt_search_results):
    """Test that generated summary is coherent and helpful."""
    question = "How do I implement JWT authentication in FastAPI?"
    
    answer = await summary_generator.generate_summary(question, jwt_search_results)
    
    # Verify summary has reasonable length
    assert len(answer.summary) > 100  # Should be substantial
    assert len(answer.summary) < 2000  # But not too long
    
    # Verify summary doesn't have obvious AI artifacts
    artifacts = [
        "based on the search results",
        "according to the messages",
        "the past discussions show",
        "from the previous messages"
    ]
    summary_lower = answer.summary.lower()
    assert not any(artifact in summary_lower for artifact in artifacts)
    
    # Verify summary is actionable (contains verbs)
    action_words = ["use", "implement", "create", "add", "install", "configure", "set"]
    assert any(word in summary_lower for word in action_words)
