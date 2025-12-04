"""
Tests for error handling and graceful degradation in Instant Answer Recall System.

This module tests:
- Retry logic for Gemini API calls (2 retries with exponential backoff)
- Retry logic for ChromaDB operations (1 retry)
- Timeout handling for all async operations
- Fallback behavior for classification failures
- Message preservation on failures

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.instant_answer.service import (
    InstantAnswerService,
    User,
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
from backend.instant_answer.retry_utils import retry_with_backoff, with_timeout


class TestRetryLogic:
    """Test retry logic for various operations."""
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_succeeds_first_attempt(self):
        """Test that retry_with_backoff returns immediately on success."""
        async def successful_operation():
            return "success"
        
        result = await retry_with_backoff(
            successful_operation,
            max_retries=2,
            operation_name="test_operation"
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_succeeds_after_retry(self):
        """Test that retry_with_backoff retries and eventually succeeds."""
        call_count = 0
        
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_backoff(
            flaky_operation,
            max_retries=2,
            initial_delay=0.1,  # Short delay for testing
            operation_name="test_operation"
        )
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_fails_after_max_retries(self):
        """Test that retry_with_backoff raises after max retries."""
        async def failing_operation():
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            await retry_with_backoff(
                failing_operation,
                max_retries=2,
                initial_delay=0.1,
                operation_name="test_operation"
            )
    
    @pytest.mark.asyncio
    async def test_with_timeout_succeeds(self):
        """Test that with_timeout returns result within timeout."""
        async def quick_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await with_timeout(
            quick_operation,
            timeout=1.0,
            operation_name="test_operation"
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_timeout_raises_on_timeout(self):
        """Test that with_timeout raises TimeoutError."""
        async def slow_operation():
            await asyncio.sleep(2.0)
            return "success"
        
        with pytest.raises(asyncio.TimeoutError):
            await with_timeout(
                slow_operation,
                timeout=0.1,
                operation_name="test_operation"
            )


class TestGeminiAPIErrorHandling:
    """Test error handling for Gemini API calls."""
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock Gemini service."""
        service = MagicMock()
        service._generate_content = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_gemini_api_retry_on_failure(self):
        """Test that Gemini API calls retry on failure.
        
        Requirements: 8.1
        """
        # Test the retry logic directly in GeminiService
        from backend.vecna.gemini_service import GeminiService
        
        # Create a real GeminiService with a fake API key
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model_class.return_value = mock_model
                
                service = GeminiService(api_key="fake_key")
                
                # First call fails, second succeeds
                call_count = 0
                def generate_side_effect(prompt):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        raise Exception("API error")
                    response = MagicMock()
                    response.text = "Success"
                    return response
                
                mock_model.generate_content.side_effect = generate_side_effect
                
                result = await service._generate_content(
                    "test prompt",
                    operation="test",
                    max_retries=2
                )
                
                # Should have retried and succeeded
                assert result == "Success"
                assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_gemini_api_timeout_handling(self):
        """Test that Gemini API calls handle timeouts.
        
        Requirements: 8.4
        """
        # Test the timeout logic directly in GeminiService
        from backend.vecna.gemini_service import GeminiService, GeminiServiceError
        
        # Create a real GeminiService with a fake API key
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model_class.return_value = mock_model
                
                service = GeminiService(api_key="fake_key")
                
                # Simulate slow response
                def slow_generate(prompt):
                    import time
                    time.sleep(10)  # Sleep longer than timeout
                    response = MagicMock()
                    response.text = "Success"
                    return response
                
                mock_model.generate_content.side_effect = slow_generate
                
                # Should timeout and raise exception
                with pytest.raises(GeminiServiceError, match="timed out"):
                    await service._generate_content(
                        "test prompt",
                        operation="test",
                        timeout=0.1,  # Very short timeout
                        max_retries=0  # No retries for timeout test
                    )


class TestChromaDBErrorHandling:
    """Test error handling for ChromaDB operations."""
    
    @pytest.fixture
    def mock_chroma_collection(self):
        """Create a mock ChromaDB collection."""
        collection = MagicMock()
        collection.query = MagicMock()
        collection.add = MagicMock()
        return collection
    
    @pytest.mark.asyncio
    async def test_chromadb_retry_on_failure(self, mock_chroma_collection):
        """Test that ChromaDB operations retry on failure.
        
        Requirements: 8.2
        """
        from backend.instant_answer.search_engine import SemanticSearchEngine
        
        mock_gemini_service = MagicMock()
        mock_gemini_service._generate_content = AsyncMock()
        
        # First query fails, second succeeds
        mock_chroma_collection.query.side_effect = [
            Exception("Connection error"),
            {
                'ids': [['msg1']],
                'documents': [['Test message']],
                'metadatas': [[{
                    'username': 'alice',
                    'room': 'Techline',
                    'timestamp': '2025-01-01T00:00:00',
                    'message_type': 'answer',
                    'topic_tags': 'testing',
                    'tech_keywords': 'python',
                    'contains_code': False,
                    'code_language': ''
                }]],
                'distances': [[0.2]]
            }
        ]
        
        search_engine = SemanticSearchEngine(
            mock_gemini_service,
            mock_chroma_collection
        )
        
        # Mock embedding generation
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 768
            
            results = await search_engine.search("test query")
            
            # Should have retried and succeeded
            assert len(results) == 1
            assert mock_chroma_collection.query.call_count == 2


class TestGracefulDegradation:
    """Test graceful degradation when components fail."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return InstantAnswerConfig(
            enabled=True,
            target_room="Techline",
            min_similarity_threshold=0.7,
            max_search_results=5,
            classification_confidence_threshold=0.6
        )
    
    @pytest.fixture
    def test_user(self):
        """Create test user."""
        return User(user_id=1, username="testuser")
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create mock Gemini service."""
        service = MagicMock()
        service._generate_content = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_chroma_collection(self):
        """Create mock ChromaDB collection."""
        return MagicMock()
    
    @pytest.fixture
    def instant_answer_service(self, mock_gemini_service, mock_chroma_collection, config):
        """Create InstantAnswerService with mocked dependencies."""
        return InstantAnswerService(
            mock_gemini_service,
            mock_chroma_collection,
            config
        )
    
    @pytest.mark.asyncio
    async def test_classification_failure_fallback(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that classification failure defaults to DISCUSSION.
        
        Requirements: 8.3
        """
        # Mock classifier to raise exception
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.side_effect = Exception("Classification failed")
            
            # Mock other services to succeed
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
                    
                    # Should return None (fallback to DISCUSSION, no instant answer)
                    assert result is None
    
    @pytest.mark.asyncio
    async def test_storage_failure_continues_processing(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that storage failure doesn't prevent message processing.
        
        Requirements: 8.2, 8.5
        """
        # Mock classification
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.9,
                contains_code=False,
                reasoning="Test"
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
                
                # Mock storage to fail
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ) as mock_store:
                    mock_store.side_effect = Exception("Storage failed")
                    
                    # Mock search to return empty results
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.return_value = []
                        
                        # Should still process and return novel question
                        result = await instant_answer_service.process_message(
                            message="How do I use FastAPI?",
                            user=test_user,
                            room="Techline"
                        )
                        
                        # Should return novel question despite storage failure
                        assert result is not None
                        assert result.is_novel_question is True
    
    @pytest.mark.asyncio
    async def test_search_failure_returns_empty_results(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that search failure returns empty results gracefully.
        
        Requirements: 8.1, 8.4
        """
        # Mock classification
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.9,
                contains_code=False,
                reasoning="Test"
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
                    # Mock search to fail
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.side_effect = Exception("Search failed")
                        
                        # Should handle search failure gracefully
                        result = await instant_answer_service.process_message(
                            message="How do I use FastAPI?",
                            user=test_user,
                            room="Techline"
                        )
                        
                        # Should return novel question (search failed, returns empty results)
                        # The service treats empty results as a novel question
                        assert result is not None
                        assert result.is_novel_question is True
    
    @pytest.mark.asyncio
    async def test_summary_generation_failure_returns_none(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that summary generation failure returns None gracefully.
        
        Requirements: 8.1
        """
        # Mock classification
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = MessageClassification(
                message_type=MessageType.QUESTION,
                confidence=0.9,
                contains_code=False,
                reasoning="Test"
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
                    # Mock search to return results
                    mock_search_result = SearchResult(
                        message_id="msg1",
                        message_text="Test answer",
                        username="alice",
                        timestamp=datetime.now(),
                        similarity_score=0.9,
                        tags=MessageTags([], [], False, None),
                        room="Techline"
                    )
                    
                    with patch.object(
                        instant_answer_service.search_engine,
                        'search',
                        new_callable=AsyncMock
                    ) as mock_search:
                        mock_search.return_value = [mock_search_result]
                        
                        # Mock summary generation to fail
                        with patch.object(
                            instant_answer_service.summary_generator,
                            'generate_summary',
                            new_callable=AsyncMock
                        ) as mock_summary:
                            mock_summary.side_effect = Exception("Summary failed")
                            
                            # Should handle summary failure gracefully
                            result = await instant_answer_service.process_message(
                                message="How do I use FastAPI?",
                                user=test_user,
                                room="Techline"
                            )
                            
                            # Should return None (summary failed, no instant answer)
                            assert result is None
    
    @pytest.mark.asyncio
    async def test_message_always_processed_on_any_failure(
        self,
        instant_answer_service,
        test_user
    ):
        """Test that message processing never crashes completely.
        
        Requirements: 8.5
        """
        # Mock all services to fail
        with patch.object(
            instant_answer_service.classifier,
            'classify',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.side_effect = Exception("Classification failed")
            
            with patch.object(
                instant_answer_service.tagger,
                'tag_message',
                new_callable=AsyncMock
            ) as mock_tag:
                mock_tag.side_effect = Exception("Tagging failed")
                
                with patch.object(
                    instant_answer_service.storage_service,
                    'store_message',
                    new_callable=AsyncMock
                ) as mock_store:
                    mock_store.side_effect = Exception("Storage failed")
                    
                    # Should not raise exception, returns None
                    result = await instant_answer_service.process_message(
                        message="Test message",
                        user=test_user,
                        room="Techline"
                    )
                    
                    # Should return None without crashing
                    assert result is None
