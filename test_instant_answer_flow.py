"""
Quick test to verify instant answer service is being called.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.config import get_config
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.chroma_client import init_chromadb_client, init_chromadb_collection
from backend.instant_answer.service import InstantAnswerService, User
from backend.vecna.gemini_service import GeminiService

async def test_instant_answer():
    """Test instant answer service initialization and basic call."""
    print("=" * 60)
    print("Testing Instant Answer Service")
    print("=" * 60)
    
    # Load config
    config = get_config()
    print(f"\n1. Config loaded:")
    print(f"   - INSTANT_ANSWER_ENABLED: {config.INSTANT_ANSWER_ENABLED}")
    print(f"   - INSTANT_ANSWER_TARGET_ROOM: {config.INSTANT_ANSWER_TARGET_ROOM}")
    print(f"   - CHROMADB_HOST: {config.CHROMADB_HOST}")
    print(f"   - CHROMADB_PORT: {config.CHROMADB_PORT}")
    
    # Initialize Gemini
    print(f"\n2. Initializing Gemini service...")
    gemini_service = GeminiService(
        api_key=config.GEMINI_API_KEY,
        model=config.GEMINI_MODEL,
        temperature=config.GEMINI_TEMPERATURE,
        max_tokens=config.GEMINI_MAX_TOKENS
    )
    print(f"   ✓ Gemini service initialized")
    
    # Initialize ChromaDB
    print(f"\n3. Initializing ChromaDB...")
    ia_config = InstantAnswerConfig.from_app_config(config)
    chromadb_client = init_chromadb_client(ia_config)
    if not chromadb_client:
        print("   ✗ ChromaDB client initialization failed!")
        return
    print(f"   ✓ ChromaDB client initialized")
    
    chromadb_collection = init_chromadb_collection(chromadb_client, ia_config)
    if not chromadb_collection:
        print("   ✗ ChromaDB collection initialization failed!")
        return
    print(f"   ✓ ChromaDB collection initialized")
    print(f"   - Messages in collection: {chromadb_collection.count()}")
    
    # Initialize InstantAnswerService
    print(f"\n4. Initializing InstantAnswerService...")
    instant_answer_service = InstantAnswerService(
        gemini_service=gemini_service,
        chroma_collection=chromadb_collection,
        config=ia_config
    )
    print(f"   ✓ InstantAnswerService initialized")
    
    # Test processing a message
    print(f"\n5. Testing message processing...")
    test_user = User(user_id=1, username="TestUser")
    test_message = "How do I configure FastAPI?"
    test_room = "Techline"
    
    print(f"   - User: {test_user.username}")
    print(f"   - Room: {test_room}")
    print(f"   - Message: {test_message}")
    
    print(f"\n6. Calling process_message()...")
    result = await instant_answer_service.process_message(
        message=test_message,
        user=test_user,
        room=test_room
    )
    
    print(f"\n7. Result:")
    if result:
        print(f"   ✓ Instant answer generated!")
        print(f"   - Is novel: {result.is_novel_question}")
        print(f"   - Confidence: {result.confidence}")
        print(f"   - Sources: {len(result.source_messages)}")
        print(f"   - Summary preview: {result.summary[:100]}...")
    else:
        print(f"   - No instant answer (message not classified as question)")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_instant_answer())
