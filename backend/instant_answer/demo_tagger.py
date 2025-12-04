"""
Demo script for testing the AutoTagger with real Gemini API.

This script demonstrates the auto-tagging functionality by processing
sample messages and displaying the extracted tags.

Usage:
    python -m backend.instant_answer.demo_tagger
"""

import asyncio
import os
from backend.vecna.gemini_service import GeminiService
from backend.instant_answer.tagger import AutoTagger


async def demo_tagger():
    """Demonstrate auto-tagging with sample messages."""
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Initialize services
    print("Initializing Gemini service...")
    gemini_service = GeminiService(api_key=api_key)
    tagger = AutoTagger(gemini_service)
    
    # Sample messages to tag
    test_messages = [
        "How do I implement JWT authentication in FastAPI?",
        "My React app is slow when rendering large lists",
        """
        Here's a Python solution:
        ```python
        def calculate_sum(numbers):
            return sum(numbers)
        ```
        """,
        "Thanks for the help!",
        "I'm getting a 500 error when deploying to AWS Lambda",
        "What's the best way to handle database migrations in Django?",
    ]
    
    print("\n" + "="*80)
    print("AUTO-TAGGING DEMO")
    print("="*80 + "\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"Text: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        try:
            # Tag the message
            tags = await tagger.tag_message(message)
            
            print(f"\nResults:")
            print(f"  Topic Tags: {', '.join(tags.topic_tags) if tags.topic_tags else 'None'}")
            print(f"  Tech Keywords: {', '.join(tags.tech_keywords) if tags.tech_keywords else 'None'}")
            print(f"  Contains Code: {tags.contains_code}")
            print(f"  Code Language: {tags.code_language or 'N/A'}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        print("-" * 80)
    
    print("\nDemo complete!")


if __name__ == "__main__":
    asyncio.run(demo_tagger())
