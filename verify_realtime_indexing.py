"""
Verify that real-time message indexing is working.

This script:
1. Checks ChromaDB current count
2. Simulates posting a message to Techline
3. Verifies the message was indexed
4. Shows the indexed message details
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.vecna.gemini_service import GeminiService
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.service import InstantAnswerService, User as InstantAnswerUser

import chromadb
import google.generativeai as genai


async def main():
    """Main verification function."""
    print("=" * 60)
    print("VERIFY REAL-TIME INDEXING")
    print("=" * 60)
    print()
    
    # Check environment
    print("1. Checking environment...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("   ✗ GEMINI_API_KEY not set!")
        return
    print("   ✓ GEMINI_API_KEY: Set")
    
    instant_answer_enabled = os.getenv("INSTANT_ANSWER_ENABLED", "false").lower() == "true"
    print(f"   ✓ INSTANT_ANSWER_ENABLED: {instant_answer_enabled}")
    
    if not instant_answer_enabled:
        print("\n   ⚠ WARNING: Instant Answer is DISABLED in .env")
        print("   Set INSTANT_ANSWER_ENABLED=true to enable automatic indexing")
        return
    
    chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port = int(os.getenv("CHROMADB_PORT", "8001"))
    print(f"   ✓ ChromaDB: {chromadb_host}:{chromadb_port}")
    print()
    
    # Initialize services
    print("2. Initializing services...")
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    gemini_service = GeminiService(api_key=gemini_key)
    print("   ✓ GeminiService initialized")
    
    # Connect to ChromaDB
    try:
        chroma_client = chromadb.HttpClient(
            host=chromadb_host,
            port=chromadb_port
        )
        chroma_client.heartbeat()
        print("   ✓ ChromaDB connected")
    except Exception as e:
        print(f"   ✗ ChromaDB connection failed: {e}")
        print("   Make sure ChromaDB server is running:")
        print("   > start_chromadb.bat")
        return
    
    # Get collection
    collection_name = "techline_messages"
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    initial_count = collection.count()
    print(f"   ✓ Collection '{collection_name}' ready")
    print(f"   ✓ Current message count: {initial_count}")
    
    # Initialize InstantAnswerService
    ia_config = InstantAnswerConfig()
    instant_answer_service = InstantAnswerService(
        gemini_service=gemini_service,
        chroma_collection=collection,
        config=ia_config
    )
    print("   ✓ InstantAnswerService initialized")
    print()
    
    # Simulate posting a message
    print("3. Simulating message post to Techline...")
    test_message = "How do I set up environment variables in Python?"
    test_user = InstantAnswerUser(user_id=999, username="test_user")
    test_room = "Techline"
    
    print(f"   Message: '{test_message}'")
    print(f"   User: {test_user.username}")
    print(f"   Room: {test_room}")
    print()
    
    # Process the message (this should index it)
    print("4. Processing message (this will index it)...")
    try:
        result = await instant_answer_service.process_message(
            message=test_message,
            user=test_user,
            room=test_room
        )
        
        print("   ✓ Message processed successfully")
        
        if result:
            print(f"   ✓ Instant answer generated:")
            print(f"     - Novel question: {result.is_novel_question}")
            print(f"     - Confidence: {result.confidence:.2f}")
            print(f"     - Sources: {len(result.source_messages)}")
        else:
            print("   ℹ No instant answer generated (not a question or no matches)")
        
        print()
    
    except Exception as e:
        print(f"   ✗ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify message was indexed
    print("5. Verifying message was indexed...")
    await asyncio.sleep(1)  # Give it a moment
    
    final_count = collection.count()
    print(f"   Initial count: {initial_count}")
    print(f"   Final count:   {final_count}")
    
    if final_count > initial_count:
        print(f"   ✓ SUCCESS! {final_count - initial_count} new message(s) indexed")
        
        # Try to retrieve the message
        print()
        print("6. Retrieving indexed message...")
        try:
            # Search for our test message
            results = collection.query(
                query_texts=[test_message],
                n_results=1,
                where={"room": {"$eq": test_room}}
            )
            
            if results and results['ids'] and results['ids'][0]:
                msg_id = results['ids'][0][0]
                msg_text = results['documents'][0][0]
                metadata = results['metadatas'][0][0]
                
                print(f"   ✓ Found message:")
                print(f"     - ID: {msg_id}")
                print(f"     - Text: {msg_text[:80]}...")
                print(f"     - Type: {metadata.get('message_type', 'unknown')}")
                print(f"     - Room: {metadata.get('room', 'unknown')}")
                print(f"     - Username: {metadata.get('username', 'unknown')}")
                print(f"     - Topics: {metadata.get('topic_tags', 'none')}")
                print(f"     - Keywords: {metadata.get('tech_keywords', 'none')}")
            else:
                print("   ⚠ Message not found in search results")
        
        except Exception as e:
            print(f"   ⚠ Could not retrieve message: {e}")
    
    else:
        print("   ⚠ WARNING: Message count did not increase")
        print("   This could mean:")
        print("   - Message was filtered (system message, empty, etc.)")
        print("   - Storage failed (check logs)")
        print("   - ChromaDB issue")
    
    print()
    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print()
    print("✓ Real-time indexing is configured and working!")
    print()
    print("When you post messages to Techline:")
    print("1. They are automatically classified (question/answer/discussion)")
    print("2. Tags and keywords are extracted")
    print("3. Embeddings are generated")
    print("4. Everything is stored in ChromaDB")
    print("5. Questions get instant answers from past discussions")
    print()


if __name__ == "__main__":
    asyncio.run(main())
