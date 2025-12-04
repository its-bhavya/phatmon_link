"""
Demo script for Message Classifier.

This script demonstrates the message classification functionality
without requiring a real Gemini API key.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.instant_answer.classifier import MessageClassifier, MessageType


async def demo_classifier():
    """Demonstrate the message classifier with sample messages."""
    
    # Create a mock Gemini service for demo purposes
    mock_service = MagicMock()
    
    async def mock_classify(prompt, operation=None):
        """Mock classification based on message content."""
        import re
        match = re.search(r'Message to classify:\s*"([^"]*)"', prompt, re.DOTALL)
        if not match:
            return "TYPE: discussion\nCONFIDENCE: 0.5\nREASONING: Unable to parse"
        
        message = match.group(1).lower()
        
        if any(word in message for word in ["how", "what", "why", "when", "?"]):
            return "TYPE: question\nCONFIDENCE: 0.92\nREASONING: Contains interrogative pattern"
        elif any(phrase in message for phrase in ["try this", "you can", "here's"]):
            return "TYPE: answer\nCONFIDENCE: 0.88\nREASONING: Provides solution"
        else:
            return "TYPE: discussion\nCONFIDENCE: 0.85\nREASONING: General conversation"
    
    mock_service._generate_content = AsyncMock(side_effect=mock_classify)
    
    # Create classifier
    classifier = MessageClassifier(mock_service)
    
    # Test messages
    test_messages = [
        "How do I implement JWT authentication in FastAPI?",
        """Try this approach:
```python
from fastapi import Depends
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```""",
        "That's a great point! I hadn't thought of it that way.",
        "What's the best way to handle database migrations?",
        "You can use Alembic for database migrations. Here's how: alembic init",
    ]
    
    print("=" * 70)
    print("MESSAGE CLASSIFIER DEMO")
    print("=" * 70)
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Message {i}:")
        print(f"  Content: {message[:60]}{'...' if len(message) > 60 else ''}")
        
        result = await classifier.classify(message)
        
        print(f"  Type: {result.message_type.value.upper()}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Contains Code: {result.contains_code}")
        print(f"  Reasoning: {result.reasoning}")
        print()


if __name__ == "__main__":
    asyncio.run(demo_classifier())
