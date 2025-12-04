"""
Unit tests for Message Storage Service.

Tests the message storage functionality including storing, retrieving,
updating, and deleting messages in ChromaDB.

Requirements: 6.1, 6.2, 6.3, 10.5
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import chromadb
from chromadb.config import Settings

from backend.instant_answer.storage import MessageStorageService, StoredMessage
from backend.instant_answer.classifier import MessageType, MessageClassification
from backend.instant_answer.tagger import MessageTags


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock()
    service._generate_content = AsyncMock()
    return service


@pytest.fixture
def chroma_client():
    """Create an in-memory ChromaDB client for testing."""
    return chromadb.Client(Settings(anonymized_telemetry=False, allow_reset=True))


@pytest.fixture
def chroma_collection(chroma_client):
    """Create an in-memory ChromaDB collection for testing."""
    # Reset to ensure clean state
    chroma_client.reset()
    
    collection = chroma_client.get_or_create_collection(
        name="test_messages",
        metadata={"hnsw:space": "cosine"}
    )
    return collection


@pytest.fixture
def storage_service(chroma_collection, mock_gemini_service):
    """Create a MessageStorageService instance for testing."""
    return MessageStorageService(
        chroma_collection=chroma_collection,
        gemini_service=mock_gemini_service
    )


@pytest.fixture
def sample_classification():
    """Create a sample message classification."""
    return MessageClassification(
        message_type=MessageType.QUESTION,
        confidence=0.95,
        contains_code=False,
        reasoning="Contains interrogative pattern"
    )


@pytest.fixture
def sample_tags():
    """Create sample message tags."""
    return MessageTags(
        topic_tags=["authentication", "security"],
        tech_keywords=["python", "fastapi"],
        contains_code=False,
        code_language=None
    )


@pytest.mark.asyncio
async def test_store_message_basic(storage_service, sample_classification, sample_tags):
    """Test basic message storage."""
    # Mock embedding generation
    mock_embedding = [0.1] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store a message
        stored_msg = await storage_service.store_message(
            message_text="How do I implement JWT auth?",
            username="alice",
            user_id=123,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags
        )
        
        # Verify stored message
        assert stored_msg.message_text == "How do I implement JWT auth?"
        assert stored_msg.username == "alice"
        assert stored_msg.user_id == 123
        assert stored_msg.room == "Techline"
        assert stored_msg.message_type == MessageType.QUESTION
        assert stored_msg.topic_tags == ["authentication", "security"]
        assert stored_msg.tech_keywords == ["python", "fastapi"]
        assert stored_msg.contains_code is False
        assert stored_msg.embedding == mock_embedding
        assert stored_msg.id.startswith("msg_")


@pytest.mark.asyncio
async def test_store_message_with_custom_id(storage_service, sample_classification, sample_tags):
    """Test storing a message with a custom ID."""
    mock_embedding = [0.1] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store with custom ID
        stored_msg = await storage_service.store_message(
            message_text="Test message",
            username="bob",
            user_id=456,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags,
            message_id="custom_id_123"
        )
        
        assert stored_msg.id == "custom_id_123"


@pytest.mark.asyncio
async def test_store_message_with_code(storage_service, sample_classification):
    """Test storing a message with code."""
    tags_with_code = MessageTags(
        topic_tags=["debugging"],
        tech_keywords=["python"],
        contains_code=True,
        code_language="python"
    )
    
    mock_embedding = [0.2] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        stored_msg = await storage_service.store_message(
            message_text="Here's the fix:\n```python\ndef foo():\n    pass\n```",
            username="charlie",
            user_id=789,
            room="Techline",
            classification=sample_classification,
            tags=tags_with_code
        )
        
        assert stored_msg.contains_code is True
        assert stored_msg.code_language == "python"


@pytest.mark.asyncio
async def test_retrieve_message(storage_service, sample_classification, sample_tags):
    """Test retrieving a stored message."""
    mock_embedding = [0.3] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store a message
        stored_msg = await storage_service.store_message(
            message_text="Test retrieval",
            username="dave",
            user_id=111,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags,
            message_id="test_retrieve_123"
        )
        
        # Retrieve the message
        retrieved_msg = storage_service.retrieve_message("test_retrieve_123")
        
        assert retrieved_msg is not None
        assert retrieved_msg.id == "test_retrieve_123"
        assert retrieved_msg.message_text == "Test retrieval"
        assert retrieved_msg.username == "dave"
        assert retrieved_msg.user_id == 111
        assert retrieved_msg.room == "Techline"
        assert retrieved_msg.message_type == MessageType.QUESTION


def test_retrieve_nonexistent_message(storage_service):
    """Test retrieving a message that doesn't exist."""
    retrieved_msg = storage_service.retrieve_message("nonexistent_id")
    assert retrieved_msg is None


@pytest.mark.asyncio
async def test_batch_storage(storage_service, sample_classification, sample_tags):
    """Test batch storage of multiple messages."""
    mock_embedding = [0.4] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Prepare batch of messages
        messages = [
            ("Message 1", "user1", 1, "Techline", sample_classification, sample_tags, "batch_1"),
            ("Message 2", "user2", 2, "Techline", sample_classification, sample_tags, "batch_2"),
            ("Message 3", "user3", 3, "Techline", sample_classification, sample_tags, "batch_3"),
        ]
        
        # Store batch
        stored_messages = await storage_service.store_messages_batch(messages)
        
        # Verify all messages were stored
        assert len(stored_messages) == 3
        assert stored_messages[0].id == "batch_1"
        assert stored_messages[1].id == "batch_2"
        assert stored_messages[2].id == "batch_3"
        
        # Verify they can be retrieved
        retrieved_1 = storage_service.retrieve_message("batch_1")
        assert retrieved_1 is not None
        assert retrieved_1.message_text == "Message 1"


@pytest.mark.asyncio
async def test_update_message(storage_service, sample_classification, sample_tags):
    """Test updating an existing message."""
    mock_embedding = [0.5] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store initial message
        await storage_service.store_message(
            message_text="Original message",
            username="eve",
            user_id=222,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags,
            message_id="update_test_123"
        )
        
        # Update the message
        new_classification = MessageClassification(
            message_type=MessageType.ANSWER,
            confidence=0.88,
            contains_code=True,
            reasoning="Now contains solution"
        )
        new_tags = MessageTags(
            topic_tags=["solution"],
            tech_keywords=["jwt"],
            contains_code=True,
            code_language="python"
        )
        
        success = await storage_service.update_message(
            message_id="update_test_123",
            message_text="Updated message with code",
            classification=new_classification,
            tags=new_tags
        )
        
        assert success is True
        
        # Retrieve and verify update
        updated_msg = storage_service.retrieve_message("update_test_123")
        assert updated_msg is not None
        assert updated_msg.message_text == "Updated message with code"
        assert updated_msg.message_type == MessageType.ANSWER
        assert updated_msg.contains_code is True


@pytest.mark.asyncio
async def test_update_nonexistent_message(storage_service, sample_classification, sample_tags):
    """Test updating a message that doesn't exist."""
    success = await storage_service.update_message(
        message_id="nonexistent",
        message_text="Updated",
        classification=sample_classification,
        tags=sample_tags
    )
    assert success is False


@pytest.mark.asyncio
async def test_delete_message(storage_service, sample_classification, sample_tags):
    """Test deleting a message."""
    mock_embedding = [0.6] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store a message
        await storage_service.store_message(
            message_text="To be deleted",
            username="frank",
            user_id=333,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags,
            message_id="delete_test_123"
        )
        
        # Verify it exists
        assert storage_service.retrieve_message("delete_test_123") is not None
        
        # Delete the message
        success = storage_service.delete_message("delete_test_123")
        assert success is True
        
        # Verify it's gone
        assert storage_service.retrieve_message("delete_test_123") is None


@pytest.mark.asyncio
async def test_room_identifier_storage(storage_service, sample_classification, sample_tags):
    """Test that room identifier is properly stored (Requirement 10.5)."""
    mock_embedding = [0.7] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        # Store message in Techline
        stored_msg = await storage_service.store_message(
            message_text="Techline message",
            username="grace",
            user_id=444,
            room="Techline",
            classification=sample_classification,
            tags=sample_tags,
            message_id="room_test_1"
        )
        
        assert stored_msg.room == "Techline"
        
        # Retrieve and verify room is preserved
        retrieved_msg = storage_service.retrieve_message("room_test_1")
        assert retrieved_msg is not None
        assert retrieved_msg.room == "Techline"


@pytest.mark.asyncio
async def test_classification_metadata_storage(storage_service, sample_tags):
    """Test that classification metadata is properly stored (Requirement 2.4)."""
    classification = MessageClassification(
        message_type=MessageType.ANSWER,
        confidence=0.92,
        contains_code=True,
        reasoning="Provides solution with code"
    )
    
    mock_embedding = [0.8] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        stored_msg = await storage_service.store_message(
            message_text="Answer with code",
            username="henry",
            user_id=555,
            room="Techline",
            classification=classification,
            tags=sample_tags,
            message_id="classification_test_1"
        )
        
        # Verify classification is stored
        assert stored_msg.message_type == MessageType.ANSWER
        
        # Retrieve and verify classification is preserved
        retrieved_msg = storage_service.retrieve_message("classification_test_1")
        assert retrieved_msg is not None
        assert retrieved_msg.message_type == MessageType.ANSWER


@pytest.mark.asyncio
async def test_tag_storage(storage_service, sample_classification):
    """Test that tags are properly stored (Requirement 5.5)."""
    tags = MessageTags(
        topic_tags=["deployment", "docker", "kubernetes"],
        tech_keywords=["docker", "k8s", "helm"],
        contains_code=True,
        code_language="yaml"
    )
    
    mock_embedding = [0.9] * 768
    with patch.object(storage_service, '_generate_embedding', return_value=mock_embedding):
        stored_msg = await storage_service.store_message(
            message_text="Kubernetes deployment config",
            username="iris",
            user_id=666,
            room="Techline",
            classification=sample_classification,
            tags=tags,
            message_id="tag_test_1"
        )
        
        # Verify tags are stored
        assert stored_msg.topic_tags == ["deployment", "docker", "kubernetes"]
        assert stored_msg.tech_keywords == ["docker", "k8s", "helm"]
        assert stored_msg.code_language == "yaml"
        
        # Retrieve and verify tags are preserved
        retrieved_msg = storage_service.retrieve_message("tag_test_1")
        assert retrieved_msg is not None
        assert retrieved_msg.topic_tags == ["deployment", "docker", "kubernetes"]
        assert retrieved_msg.tech_keywords == ["docker", "k8s", "helm"]
        assert retrieved_msg.code_language == "yaml"


@pytest.mark.asyncio
async def test_storage_error_handling(storage_service, sample_classification, sample_tags):
    """Test error handling when storage fails."""
    # Mock embedding generation to raise an error
    with patch.object(storage_service, '_generate_embedding', side_effect=Exception("API Error")):
        with pytest.raises(Exception):
            await storage_service.store_message(
                message_text="This will fail",
                username="jack",
                user_id=777,
                room="Techline",
                classification=sample_classification,
                tags=sample_tags
            )


@pytest.mark.asyncio
async def test_batch_storage_partial_failure(storage_service, sample_classification, sample_tags):
    """Test batch storage continues on partial failures."""
    # Mock embedding to fail on second message
    call_count = 0
    
    async def mock_embedding(text):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise Exception("Embedding failed")
        return [0.1] * 768
    
    with patch.object(storage_service, '_generate_embedding', side_effect=mock_embedding):
        messages = [
            ("Message 1", "user1", 1, "Techline", sample_classification, sample_tags, "partial_1"),
            ("Message 2", "user2", 2, "Techline", sample_classification, sample_tags, "partial_2"),
            ("Message 3", "user3", 3, "Techline", sample_classification, sample_tags, "partial_3"),
        ]
        
        stored_messages = await storage_service.store_messages_batch(messages)
        
        # Should have stored 2 out of 3 messages
        assert len(stored_messages) == 2
        assert stored_messages[0].id == "partial_1"
        assert stored_messages[1].id == "partial_3"
