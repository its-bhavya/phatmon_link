"""
Demo script for Semantic Search Engine.

This script demonstrates how to use the SemanticSearchEngine to search
for similar messages in the knowledge base.

Usage:
    python -m backend.instant_answer.demo_search
"""

import asyncio
import logging
from datetime import datetime
from backend.instant_answer.search_engine import SemanticSearchEngine
from backend.instant_answer.classifier import MessageType
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.chroma_client import init_chromadb_client, init_chromadb_collection
from backend.config import Config
from backend.vecna.gemini_service import GeminiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_search():
    """Demonstrate semantic search functionality."""
    
    print("=" * 70)
    print("Semantic Search Engine Demo")
    print("=" * 70)
    print()
    
    try:
        # Load configuration
        config = Config()
        instant_answer_config = InstantAnswerConfig.from_app_config(config)
        
        print(f"Configuration loaded:")
        print(f"  - Target room: {instant_answer_config.target_room}")
        print(f"  - Min similarity: {instant_answer_config.min_similarity_threshold}")
        print(f"  - Max results: {instant_answer_config.max_search_results}")
        print()
        
        # Initialize ChromaDB
        print("Initializing ChromaDB...")
        chroma_client = init_chromadb_client(instant_answer_config)
        if not chroma_client:
            print("❌ Failed to initialize ChromaDB client")
            return
        
        chroma_collection = init_chromadb_collection(chroma_client, instant_answer_config)
        if not chroma_collection:
            print("❌ Failed to initialize ChromaDB collection")
            return
        
        print(f"✓ ChromaDB initialized with {chroma_collection.count()} documents")
        print()
        
        # Initialize Gemini service
        print("Initializing Gemini service...")
        gemini_service = GeminiService(
            api_key=config.GEMINI_API_KEY,
            model=config.GEMINI_MODEL,
            temperature=0.7
        )
        print("✓ Gemini service initialized")
        print()
        
        # Initialize search engine
        search_engine = SemanticSearchEngine(
            gemini_service=gemini_service,
            chroma_collection=chroma_collection,
            embedding_model=instant_answer_config.embedding_model
        )
        print("✓ Search engine initialized")
        print()
        
        # Example queries
        queries = [
            "How do I implement JWT authentication in FastAPI?",
            "What's the best way to handle async operations?",
            "How can I optimize database queries?",
        ]
        
        for query in queries:
            print("-" * 70)
            print(f"Query: {query}")
            print("-" * 70)
            
            try:
                # Perform search
                results = await search_engine.search(
                    query=query,
                    room_filter=instant_answer_config.target_room,
                    message_type_filter=MessageType.ANSWER,
                    limit=instant_answer_config.max_search_results,
                    min_similarity=instant_answer_config.min_similarity_threshold
                )
                
                if results:
                    print(f"Found {len(results)} relevant answers:\n")
                    
                    for i, result in enumerate(results, 1):
                        print(f"{i}. [{result.username}] (similarity: {result.similarity_score:.2f})")
                        print(f"   {result.message_text[:100]}...")
                        print(f"   Tags: {', '.join(result.tags.topic_tags[:3])}")
                        print(f"   Tech: {', '.join(result.tags.tech_keywords[:3])}")
                        if result.tags.contains_code:
                            print(f"   Contains code: {result.tags.code_language}")
                        print()
                else:
                    print("No relevant answers found (this is expected if the database is empty)")
                    print()
            
            except Exception as e:
                print(f"❌ Search failed: {e}")
                print()
        
        print("=" * 70)
        print("Demo complete!")
        print("=" * 70)
    
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_search())
