"""
Demo script for testing the AI Summary Generator.

This script demonstrates the summary generation functionality by:
1. Creating mock search results
2. Generating summaries for different question types
3. Testing code snippet preservation
4. Testing source attribution
5. Testing novel question detection

Run with: python -m backend.instant_answer.demo_summary
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.vecna.gemini_service import GeminiService
from backend.instant_answer.summary_generator import SummaryGenerator
from backend.instant_answer.search_engine import SearchResult
from backend.instant_answer.tagger import MessageTags


def create_mock_search_results() -> list[SearchResult]:
    """Create mock search results for testing."""
    base_time = datetime.now() - timedelta(days=7)
    
    results = [
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
    
    return results


async def demo_summary_generation():
    """Demonstrate summary generation with various scenarios."""
    print("=" * 70)
    print("AI Summary Generator Demo")
    print("=" * 70)
    
    # Initialize services
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        return
    
    print("\n✓ Initializing Gemini service...")
    gemini_service = GeminiService(api_key=api_key)
    
    print("✓ Initializing Summary Generator...")
    generator = SummaryGenerator(gemini_service, max_summary_tokens=300)
    
    # Test 1: Generate summary from multiple results
    print("\n" + "=" * 70)
    print("Test 1: Generate Summary from Multiple Search Results")
    print("=" * 70)
    
    question = "How do I implement JWT authentication in FastAPI?"
    search_results = create_mock_search_results()
    
    print(f"\nQuestion: {question}")
    print(f"Search Results: {len(search_results)} messages found")
    print("\nGenerating summary...")
    
    try:
        answer = await generator.generate_summary(question, search_results)
        
        print("\n" + "-" * 70)
        print("INSTANT ANSWER:")
        print("-" * 70)
        print(answer.summary)
        print("-" * 70)
        print(f"\nConfidence: {answer.confidence:.2f}")
        print(f"Is Novel Question: {answer.is_novel_question}")
        print(f"Source Messages: {len(answer.source_messages)}")
        
        # Check if code snippets were preserved
        has_code = "```" in answer.summary
        print(f"Code Snippets Preserved: {'✓' if has_code else '✗'}")
        
        # Check if source attribution is present
        has_sources = "Sources:" in answer.summary
        print(f"Source Attribution: {'✓' if has_sources else '✗'}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Test 2: Novel question detection
    print("\n" + "=" * 70)
    print("Test 2: Novel Question Detection (No Search Results)")
    print("=" * 70)
    
    novel_question = "How do I implement quantum computing in my toaster?"
    print(f"\nQuestion: {novel_question}")
    print("Search Results: 0 messages found")
    print("\nGenerating summary...")
    
    try:
        answer = await generator.generate_summary(novel_question, [])
        
        print("\n" + "-" * 70)
        print("INSTANT ANSWER:")
        print("-" * 70)
        print(answer.summary)
        print("-" * 70)
        print(f"\nConfidence: {answer.confidence:.2f}")
        print(f"Is Novel Question: {answer.is_novel_question}")
        print(f"Novel Question Flag: {'✓' if answer.is_novel_question else '✗'}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Test 3: Single result summary
    print("\n" + "=" * 70)
    print("Test 3: Summary from Single Search Result")
    print("=" * 70)
    
    single_question = "What library should I use for JWT in Python?"
    single_result = [create_mock_search_results()[2]]  # Just the charlie message
    
    print(f"\nQuestion: {single_question}")
    print(f"Search Results: {len(single_result)} message found")
    print("\nGenerating summary...")
    
    try:
        answer = await generator.generate_summary(single_question, single_result)
        
        print("\n" + "-" * 70)
        print("INSTANT ANSWER:")
        print("-" * 70)
        print(answer.summary)
        print("-" * 70)
        print(f"\nConfidence: {answer.confidence:.2f}")
        print(f"Is Novel Question: {answer.is_novel_question}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_summary_generation())
