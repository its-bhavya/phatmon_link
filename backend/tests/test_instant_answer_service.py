"""
Tests for InstantAnswerService orchestrator.

This module tests the main orchestration service that coordinates all
instant answer operations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.instant_answer.service import (
    InstantAnswerService,
    User,
    InstantAnswerError,
    ClassificationError,
    SearchError,
    SummaryError,
    StorageError
)
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.classifier import MessageType, MessageClassification
from backend.instant_answer.tagger import MessageTags
from backend.instant_answer.search_engine import SearchResult
from backend.instant_answer.summary_generator import InstantAnswer


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock()
    service._generate_content = AsyncMock()
    return service


@pytest.fixture
def mock_chroma_collection():
    """Create a mock ChromaDB collection."""
    collection = Mock()
    collection.add = Mock()
    collection.query = Mock()
    collection.get = Mock()
    return collection


@pytest.fixture
def config():
    """Create test configuration."""
    return InstantAnswerConfig(
        enabled=True,
        target_room="Techline",
        min_similarity_threshold=0.7,
        max_search_results=5,
        classification_confidence_threshold=0.6,
        max_summary_tokens=300,
        chroma_collection_name="test_messages",
        chroma_host="localhost",
        chroma_port=8001,
        embedding_model="models/embedding-001"
    )


@pytest.fixture
def instant_answer_service(mock_gemini_service, mock_chroma_collection, config):
    """Create InstantAnswerService with mocked dependencies."""
    return InstantAnswerService(
        gemini_service=mock_gemini_service,
        chroma_collection=mock_chroma_collection,
        config=config
    )


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(user_id=1, username="testuser")


class TestInstantAnswerService:
    """Test suite for InstantAnswerService."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, instant_answer_service, config):
        """Test that service initializes correctly with all sub-services."""
        assert instant_answer_service.config == config
        assert instant_answer_service.classifier is not None
        assert instant_answer_service.tagger is not None
        assert instant_answer_service.search_engine is not None
        assert instant_answer_service.summary_generator is not None
        assert instant_answer_service.storage_service is not None
    
    @pytest.mark.asyncio
    async def test_process_message_disabled_system(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that disabled system returns None."""
        instant_answer_service.config.enabled = False
        
        result = await instant_answer_service.process_message(
            message="How do I use FastAPI?",
            user=test_user,
            room="Techline"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_message_wrong_room(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that messages in non-target rooms are skipped."""
        result = await instant_answer_service.process_message(
            message="How do I use FastAPI?",
            user=test_user,
            room="Lobby"  # Not Techline
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_message_non_question(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that non-question messages return None."""
        # Mock classification to return DISCUSSION
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.DISCUSSION,
                confidence=0.9,
                contains_code=False,
                reasoning="General discussion"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    result = await instant_answer_service.process_message(
                        message="That's interesting!",
                        user=test_user,
                        room="Techline"
                    )
                    
                    assert result is None
    
    @pytest.mark.asyncio
    async def test_process_message_question_with_results(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that questions trigger search and summary generation."""
        # Mock classification to return QUESTION
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.95,
                contains_code=False,
                reasoning="Question detected"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=["api", "web"],
                    tech_keywords=["fastapi", "python"],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    # Mock search to return results
                    mock_search_result = SearchResult(
                        message_id="msg_123",
                        message_text="You can use FastAPI by...",
                        username="helper",
                        timestamp=datetime.now(),
                        similarity_score=0.85,
                        tags=MessageTags([], [], False, None),
                        room="Techline"
                    )
                    
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.return_value = [mock_search_result]
                        
                        # Mock summary generation
                        mock_instant_answer = InstantAnswer(
                            summary="Based on past discussions, you can use FastAPI by...",
                            source_messages=[mock_search_result],
                            confidence=0.85,
                            is_novel_question=False
                        )
                        
                        with patch.object(
                            instant_answer_service.summary_generator,
                            'generate_summary',
                            new_callable=AsyncMock
                        ) as mock_summary:
                            mock_summary.return_value = mock_instant_answer
                            
                            result = await instant_answer_service.process_message(
                                message="How do I use FastAPI?",
                                user=test_user,
                                room="Techline"
                            )
                            
                            assert result is not None
                            assert result.summary == mock_instant_answer.summary
                            assert result.is_novel_question is False
                            assert len(result.source_messages) == 1
    
    @pytest.mark.asyncio
    async def test_process_message_novel_question(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that questions with no results return novel question indicator."""
        # Mock classification to return QUESTION
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.95,
                contains_code=False,
                reasoning="Question detected"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    # Mock search to return empty results
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.return_value = []
                        
                        result = await instant_answer_service.process_message(
                            message="What is quantum computing?",
                            user=test_user,
                            room="Techline"
                        )
                        
                        assert result is not None
                        assert result.is_novel_question is True
                        assert len(result.source_messages) == 0
    
    @pytest.mark.asyncio
    async def test_classification_failure_fallback(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that classification failures default to DISCUSSION."""
        # Mock classification to raise exception
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.side_effect = Exception("API error")
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    result = await instant_answer_service.process_message(
                        message="Test message",
                        user=test_user,
                        room="Techline"
                    )
                    
                    # Should return None (treated as DISCUSSION)
                    assert result is None
    
    @pytest.mark.asyncio
    async def test_storage_failure_continues_processing(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that storage failures don't prevent message processing."""
        # Mock classification
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.DISCUSSION,
                confidence=0.9,
                contains_code=False,
                reasoning="Discussion"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage to raise exception
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ) as mock_store:
                    mock_store.side_effect = Exception("ChromaDB error")
                    
                    # Should not raise exception
                    result = await instant_answer_service.process_message(
                        message="Test message",
                        user=test_user,
                        room="Techline"
                    )
                    
                    # Processing continues, returns None for non-question
                    assert result is None
    
    @pytest.mark.asyncio
    async def test_search_failure_returns_empty_results(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that search failures return empty results."""
        # Mock classification to return QUESTION
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.95,
                contains_code=False,
                reasoning="Question"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    # Mock search to raise exception
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.side_effect = Exception("Search error")
                        
                        result = await instant_answer_service.process_message(
                            message="How do I use FastAPI?",
                            user=test_user,
                            room="Techline"
                        )
                        
                        # Should return novel question (empty results)
                        assert result is not None
                        assert result.is_novel_question is True
    
    @pytest.mark.asyncio
    async def test_low_confidence_classification_skips_instant_answer(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that low confidence classifications skip instant answer."""
        # Mock classification with low confidence
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.4,  # Below threshold of 0.6
                contains_code=False,
                reasoning="Uncertain question"
            )
            
            # Mock tagging
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.return_value = MessageTags(
                    topic_tags=[],
                    tech_keywords=[],
                    contains_code=False,
                    code_language=None
                )
                
                # Mock storage
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ):
                    result = await instant_answer_service.process_message(
                        message="Maybe a question?",
                        user=test_user,
                        room="Techline"
                    )
                    
                    # Should return None due to low confidence
                    assert result is None
