"""
Demo script for InstantAnswerService orchestrator.

This script demonstrates the end-to-end flow of the instant answer system,
showing how all components work together to process messages and generate
instant answers.

Usage:
    python -m backend.instant_answer.demo_service
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from backend.instant_answer.service import InstantAnswerService, User
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.chroma_client import get_chroma_client, get_or_create_collection
from backend.vecna.gemini_service import GeminiService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_instant_answer_service():
    """
    Demonstrate the InstantAnswerService orchestrator.
    
    This demo shows:
    1. Service initialization with all sub-components
    2. Processing different message types (question, answer, discussion)
    3. Generating instant answers for questions
    4. Handling novel questions with no history
    5. Graceful error handling
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        return
    
    logger.info("=== InstantAnswerService Demo ===\n")
    
    # Initialize services
    logger.info("Initializing services...")
    gemini_service = GeminiService(api_key=api_key)
    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client, "demo_instant_answer")
    
    # Create configuration
    config = InstantAnswerConfig(
        enabled=True,
        target_room="Techline",
        min_similarity_threshold=0.7,
        max_search_results=5,
        classification_confidence_threshold=0.6,
        max_summary_tokens=300
    )
    
    # Initialize InstantAnswerService
    service = InstantAnswerService(
        gemini_service=gemini_service,
        chroma_collection=collection,
        config=config
    )
    
    logger.info("Services initialized successfully\n")
    
    # Create test users
    alice = User(user_id=1, username="alice")
    bob = User(user_id=2, username="bob")
    charlie = User(user_id=3, username="charlie")
    
    # Demo 1: Process an answer message (builds knowledge base)
    logger.info("--- Demo 1: Processing an answer message ---")
    answer_message = """You can implement JWT authentication in FastAPI like this:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    # Verify token here
    return token
```

This creates a secure authentication system."""
    
    result = await service.process_message(
        message=answer_message,
        user=alice,
        room="Techline"
    )
    
    logger.info(f"Result: {result}")
    logger.info("Answer stored in knowledge base\n")
    
    # Demo 2: Process a discussion message
    logger.info("--- Demo 2: Processing a discussion message ---")
    discussion_message = "Thanks for the help! That's really useful."
    
    result = await service.process_message(
        message=discussion_message,
        user=bob,
        room="Techline"
    )
    
    logger.info(f"Result: {result}")
    logger.info("Discussion message stored\n")
    
    # Demo 3: Process a question (should trigger instant answer)
    logger.info("--- Demo 3: Processing a question ---")
    question_message = "How do I implement JWT authentication in FastAPI?"
    
    result = await service.process_message(
        message=question_message,
        user=charlie,
        room="Techline"
    )
    
    if result:
        logger.info("Instant answer generated!")
        logger.info(f"Summary: {result.summary[:200]}...")
        logger.info(f"Is novel question: {result.is_novel_question}")
        logger.info(f"Confidence: {result.confidence:.2f}")
        logger.info(f"Number of sources: {len(result.source_messages)}")
    else:
        logger.info("No instant answer generated")
    
    logger.info("")
    
    # Demo 4: Process a novel question (no similar history)
    logger.info("--- Demo 4: Processing a novel question ---")
    novel_question = "What is the best way to implement quantum computing in Python?"
    
    result = await service.process_message(
        message=novel_question,
        user=charlie,
        room="Techline"
    )
    
    if result:
        logger.info("Instant answer generated!")
        logger.info(f"Summary: {result.summary}")
        logger.info(f"Is novel question: {result.is_novel_question}")
        logger.info(f"Number of sources: {len(result.source_messages)}")
    else:
        logger.info("No instant answer generated")
    
    logger.info("")
    
    # Demo 5: Process message in wrong room (should be skipped)
    logger.info("--- Demo 5: Processing message in wrong room ---")
    lobby_message = "How do I use FastAPI?"
    
    result = await service.process_message(
        message=lobby_message,
        user=charlie,
        room="Lobby"  # Not Techline
    )
    
    logger.info(f"Result: {result}")
    logger.info("Message skipped (wrong room)\n")
    
    # Demo 6: Test graceful error handling
    logger.info("--- Demo 6: Testing graceful error handling ---")
    
    # Temporarily disable Gemini service to simulate failure
    original_generate = gemini_service._generate_content
    
    async def failing_generate(*args, **kwargs):
        raise Exception("Simulated API failure")
    
    gemini_service._generate_content = failing_generate
    
    result = await service.process_message(
        message="How do I use FastAPI?",
        user=charlie,
        room="Techline"
    )
    
    logger.info(f"Result with API failure: {result}")
    logger.info("System handled failure gracefully\n")
    
    # Restore original function
    gemini_service._generate_content = original_generate
    
    logger.info("=== Demo Complete ===")
    logger.info("\nKey takeaways:")
    logger.info("1. Service coordinates all sub-components seamlessly")
    logger.info("2. Questions trigger search and summary generation")
    logger.info("3. Novel questions are detected and handled appropriately")
    logger.info("4. Room filtering ensures system only activates in Techline")
    logger.info("5. Graceful error handling prevents system failures")


if __name__ == "__main__":
    asyncio.run(demo_instant_answer_service())
