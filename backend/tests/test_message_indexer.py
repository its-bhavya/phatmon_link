"""
Tests for Message Indexer.

This module tests the background message indexing functionality for the
Instant Answer Recall system.

Requirements: 6.1, 6.2, 6.3
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from backend.instant_answer.indexer import MessageIndexer, index_historical_messages
from backend.instant_answer.service import InstantAnswerService, User
from backend.instant_answer.classifier import MessageClassification, MessageType
from backend.instant_answer.tagger import MessageTags


@pytest.fixture
def mock_instant_answer_service():
    """Create a mock InstantAnswerService."""
    service = Mock(spec=InstantAnswerService)
    
    # Mock classifier
    service.classifier = Mock()
    service.classifier.classify = AsyncMock(return_value=MessageClassification(
        message_type=MessageType.QUESTION,
        confidence=0.8,
        contains_code=False,
        reasoning="Test classification"
    ))
    
    # Mock tagger
    service.tagger = Mock()
    service.tagger.tag_message = AsyncMock(return_value=MessageTags(
        topic_tags=["testing"],
        tech_keywords=["Python"],
        contains_code=False,
        code_language=None
    ))
    
    # Mock storage service
    service.storage_service = Mock()
    service.storage_service.store_message = AsyncMock()
    
    return service


@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    return [
        {
            "type": "chat_message",
            "username": "alice",
            "content": "How do I use pytest?",
            "timestamp": "2025-12-05T10:00:00Z",
            "room": "Techline"
        },
        {
            "type": "chat_message",
            "username": "bob",
            "content": "You can use pytest fixtures for setup",
            "timestamp": "2025-12-05T10:01:00Z",
            "room": "Techline"
        },
        {
            "type": "system",
            "content": "* alice has entered the room",
            "timestamp": "2025-12-05T10:02:00Z"
        },
        {
            "type": "chat_message",
            "username": "charlie",
            "content": "",  # Empty message
            "timestamp": "2025-12-05T10:03:00Z",
            "room": "Techline"
        }
    ]


@pytest.mark.asyncio
async def test_indexer_initialization():
    """Test that MessageIndexer initializes correctly."""
    service = Mock(spec=InstantAnswerService)
    indexer = MessageIndexer(service, batch_size=5)
    
    assert indexer.instant_answer_service == service
    assert indexer.batch_size == 5
    assert indexer.total_processed == 0
    assert indexer.total_stored == 0
    assert indexer.total_failed == 0


@pytest.mark.asyncio
async def test_index_room_messages(mock_instant_answer_service, sample_messages):
    """Test indexing room messages."""
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=2)
    
    stats = await indexer.index_room_messages("Techline", sample_messages)
    
    # Should process all messages
    assert stats["processed"] == 4
    
    # Should store only valid chat messages (2 valid, 1 system, 1 empty)
    assert stats["stored"] == 2
    
    # Should fail on system and empty messages
    assert stats["failed"] == 2
    
    # Verify storage was called for valid messages
    assert mock_instant_answer_service.storage_service.store_message.call_count == 2


@pytest.mark.asyncio
async def test_index_room_messages_with_batching(mock_instant_answer_service):
    """Test that messages are processed in batches."""
    # Create 10 messages
    messages = [
        {
            "type": "chat_message",
            "username": f"user{i}",
            "content": f"Message {i}",
            "timestamp": f"2025-12-05T10:{i:02d}:00Z",
            "room": "Techline"
        }
        for i in range(10)
    ]
    
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=3)
    
    stats = await indexer.index_room_messages("Techline", messages)
    
    # Should process all messages
    assert stats["processed"] == 10
    assert stats["stored"] == 10
    assert stats["failed"] == 0


@pytest.mark.asyncio
async def test_index_room_messages_skips_system_messages(mock_instant_answer_service):
    """Test that system messages are skipped."""
    messages = [
        {
            "type": "system",
            "content": "System message",
            "timestamp": "2025-12-05T10:00:00Z"
        },
        {
            "type": "error",
            "content": "Error message",
            "timestamp": "2025-12-05T10:01:00Z"
        },
        {
            "type": "support_response",
            "content": "Support response",
            "timestamp": "2025-12-05T10:02:00Z"
        }
    ]
    
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=10)
    
    stats = await indexer.index_room_messages("Techline", messages)
    
    # Should process all but store none
    assert stats["processed"] == 3
    assert stats["stored"] == 0
    assert stats["failed"] == 3
    
    # Storage should not be called
    assert mock_instant_answer_service.storage_service.store_message.call_count == 0


@pytest.mark.asyncio
async def test_index_room_messages_handles_classification_failure(mock_instant_answer_service):
    """Test that classification failures are handled gracefully."""
    # Make classifier fail
    mock_instant_answer_service.classifier.classify = AsyncMock(
        side_effect=Exception("Classification failed")
    )
    
    messages = [
        {
            "type": "chat_message",
            "username": "alice",
            "content": "Test message",
            "timestamp": "2025-12-05T10:00:00Z",
            "room": "Techline"
        }
    ]
    
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=10)
    
    stats = await indexer.index_room_messages("Techline", messages)
    
    # Should still process and store with fallback classification
    assert stats["processed"] == 1
    assert stats["stored"] == 1
    assert stats["failed"] == 0


@pytest.mark.asyncio
async def test_index_room_messages_handles_tagging_failure(mock_instant_answer_service):
    """Test that tagging failures are handled gracefully."""
    # Make tagger fail
    mock_instant_answer_service.tagger.tag_message = AsyncMock(
        side_effect=Exception("Tagging failed")
    )
    
    messages = [
        {
            "type": "chat_message",
            "username": "alice",
            "content": "Test message",
            "timestamp": "2025-12-05T10:00:00Z",
            "room": "Techline"
        }
    ]
    
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=10)
    
    stats = await indexer.index_room_messages("Techline", messages)
    
    # Should still process and store with empty tags
    assert stats["processed"] == 1
    assert stats["stored"] == 1
    assert stats["failed"] == 0


@pytest.mark.asyncio
async def test_index_room_messages_handles_storage_failure(mock_instant_answer_service):
    """Test that storage failures are handled gracefully."""
    # Make storage fail
    mock_instant_answer_service.storage_service.store_message = AsyncMock(
        side_effect=Exception("Storage failed")
    )
    
    messages = [
        {
            "type": "chat_message",
            "username": "alice",
            "content": "Test message",
            "timestamp": "2025-12-05T10:00:00Z",
            "room": "Techline"
        }
    ]
    
    indexer = MessageIndexer(mock_instant_answer_service, batch_size=10)
    
    stats = await indexer.index_room_messages("Techline", messages)
    
    # Should process but fail to store
    assert stats["processed"] == 1
    assert stats["stored"] == 0
    assert stats["failed"] == 1


@pytest.mark.asyncio
async def test_index_historical_messages_with_room_service(mock_instant_answer_service):
    """Test the convenience function with room service."""
    # Create mock room service
    mock_room_service = Mock()
    mock_room = Mock()
    mock_room.get_recent_messages = Mock(return_value=[
        {
            "type": "chat_message",
            "username": "alice",
            "content": "Test message",
            "timestamp": "2025-12-05T10:00:00Z",
            "room": "Techline"
        }
    ])
    mock_room_service.get_room = Mock(return_value=mock_room)
    
    stats = await index_historical_messages(
        instant_answer_service=mock_instant_answer_service,
        room_service=mock_room_service,
        target_room="Techline",
        batch_size=10
    )
    
    # Should process the message
    assert stats["processed"] == 1
    assert stats["stored"] == 1
    assert stats["failed"] == 0
    
    # Verify room service was called
    mock_room_service.get_room.assert_called_once_with("Techline")
    mock_room.get_recent_messages.assert_called_once_with(limit=1000)


@pytest.mark.asyncio
async def test_index_historical_messages_room_not_found(mock_instant_answer_service):
    """Test that missing room is handled gracefully."""
    # Create mock room service that returns None
    mock_room_service = Mock()
    mock_room_service.get_room = Mock(return_value=None)
    
    stats = await index_historical_messages(
        instant_answer_service=mock_instant_answer_service,
        room_service=mock_room_service,
        target_room="NonExistent",
        batch_size=10
    )
    
    # Should return zero stats
    assert stats["processed"] == 0
    assert stats["stored"] == 0
    assert stats["failed"] == 0


@pytest.mark.asyncio
async def test_index_historical_messages_no_messages(mock_instant_answer_service):
    """Test that empty room history is handled gracefully."""
    # Create mock room service with empty history
    mock_room_service = Mock()
    mock_room = Mock()
    mock_room.get_recent_messages = Mock(return_value=[])
    mock_room_service.get_room = Mock(return_value=mock_room)
    
    stats = await index_historical_messages(
        instant_answer_service=mock_instant_answer_service,
        room_service=mock_room_service,
        target_room="Techline",
        batch_size=10
    )
    
    # Should return zero stats
    assert stats["processed"] == 0
    assert stats["stored"] == 0
    assert stats["failed"] == 0
