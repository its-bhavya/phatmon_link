"""
Integration tests for Semantic Search Engine.

Tests the search engine with real-like data flows.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.instant_answer.search_engine import SemanticSearchEngine
from backend.instant_answer.classifier import MessageType
from backend.instant_answer.tagger import MessageTags


class TestSemanticSearchEngineIntegration:
    """Integration tests for semantic search engine."""
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock Gemini service."""
        service = MagicMock()
        return service
    
    @pytest.fixture
    def mock_chroma_collection(self):
        """Create a mock ChromaDB collection."""
        collection = MagicMock()
        collection.query = MagicMock()
        return collection
    
    @pytest.fixture
    def search_engine(self, mock_gemini_service, mock_chroma_collection):
        """Create a search engine with mock dependencies."""
        return SemanticSearchEngine(
            mock_gemini_service,
            mock_chroma_collection
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_search_flow(self, search_engine, mock_chroma_collection):
        """Test complete search flow from query to ranked results."""
        # Mock embedding generation
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 768  # Typical embedding size
            
            # Mock ChromaDB with realistic data
            mock_chroma_collection.query.return_value = {
                'ids': [['msg_001', 'msg_002', 'msg_003']],
                'documents': [[
                    'You can use FastAPI with async def for async endpoints',
                    'Try using @app.get decorator for GET requests',
                    'FastAPI automatically validates request data'
                ]],
                'metadatas': [[
                    {
                        'username': 'alice',
                        'timestamp': '2025-12-01T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': ['api', 'async'],
                        'tech_keywords': ['fastapi', 'python'],
                        'contains_code': True,
                        'code_language': 'python'
                    },
                    {
                        'username': 'bob',
                        'timestamp': '2025-12-02T11:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': ['api', 'routing'],
                        'tech_keywords': ['fastapi'],
                        'contains_code': True,
                        'code_language': 'python'
                    },
                    {
                        'username': 'charlie',
                        'timestamp': '2025-12-03T12:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': ['validation'],
                        'tech_keywords': ['fastapi', 'pydantic'],
                        'contains_code': False,
                        'code_language': None
                    }
                ]],
                'distances': [[0.15, 0.25, 0.35]]  # Similarities: 0.85, 0.75, 0.65
            }
            
            # Execute search
            results = await search_engine.search(
                query="How do I create async endpoints in FastAPI?",
                room_filter="Techline",
                message_type_filter=MessageType.ANSWER,
                limit=5,
                min_similarity=0.6
            )
            
            # Verify results
            assert len(results) == 3
            
            # Check ranking (highest similarity first)
            assert results[0].similarity_score == 0.85
            assert results[0].username == 'alice'
            assert results[0].tags.contains_code is True
            
            assert results[1].similarity_score == 0.75
            assert results[1].username == 'bob'
            
            assert results[2].similarity_score == 0.65
            assert results[2].username == 'charlie'
            
            # Verify metadata filters were applied
            call_args = mock_chroma_collection.query.call_args
            assert call_args[1]['where']['room'] == 'Techline'
            assert call_args[1]['where']['message_type'] == 'answer'
    
    @pytest.mark.asyncio
    async def test_search_with_no_message_type_filter(self, search_engine, mock_chroma_collection):
        """Test search without message type filter."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 768
            
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1']],
                'documents': [['Test']],
                'metadatas': [[{
                    'username': 'alice',
                    'timestamp': '2025-12-05T10:00:00',
                    'room': 'Techline',
                    'message_type': 'question',
                    'topic_tags': [],
                    'tech_keywords': [],
                    'contains_code': False,
                    'code_language': None
                }]],
                'distances': [[0.2]]
            }
            
            results = await search_engine.search(
                query="test",
                room_filter="Techline",
                message_type_filter=None,  # No type filter
                min_similarity=0.5
            )
            
            # Verify only room filter was applied
            call_args = mock_chroma_collection.query.call_args
            assert call_args[1]['where'] == {'room': 'Techline'}
            assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_search_filters_low_quality_results(self, search_engine, mock_chroma_collection):
        """Test that low similarity results are filtered out."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 768
            
            # Mix of high and low quality results
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1', 'msg2', 'msg3', 'msg4']],
                'documents': [['High quality', 'Medium quality', 'Low quality', 'Very low quality']],
                'metadatas': [[
                    {
                        'username': f'user{i}',
                        'timestamp': '2025-12-05T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    }
                    for i in range(4)
                ]],
                'distances': [[0.1, 0.3, 0.5, 0.7]]  # Similarities: 0.9, 0.7, 0.5, 0.3
            }
            
            # Set high threshold
            results = await search_engine.search(
                query="test",
                min_similarity=0.65
            )
            
            # Only first two should pass threshold
            assert len(results) == 2
            assert results[0].similarity_score == 0.9
            assert results[1].similarity_score == 0.7
    
    @pytest.mark.asyncio
    async def test_search_preserves_message_metadata(self, search_engine, mock_chroma_collection):
        """Test that all message metadata is preserved in results."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 768
            
            mock_chroma_collection.query.return_value = {
                'ids': [['msg_123']],
                'documents': [['Complete message with all metadata']],
                'metadatas': [[{
                    'username': 'test_user',
                    'timestamp': '2025-12-05T15:30:45',
                    'room': 'Techline',
                    'message_type': 'answer',
                    'topic_tags': ['python', 'async', 'performance'],
                    'tech_keywords': ['fastapi', 'uvicorn', 'asyncio'],
                    'contains_code': True,
                    'code_language': 'python'
                }]],
                'distances': [[0.2]]
            }
            
            results = await search_engine.search(
                query="test",
                min_similarity=0.5
            )
            
            assert len(results) == 1
            result = results[0]
            
            # Verify all metadata is preserved
            assert result.message_id == 'msg_123'
            assert result.message_text == 'Complete message with all metadata'
            assert result.username == 'test_user'
            assert result.timestamp == datetime(2025, 12, 5, 15, 30, 45)
            assert result.similarity_score == 0.8
            assert result.room == 'Techline'
            
            # Verify tags
            assert result.tags.topic_tags == ['python', 'async', 'performance']
            assert result.tags.tech_keywords == ['fastapi', 'uvicorn', 'asyncio']
            assert result.tags.contains_code is True
            assert result.tags.code_language == 'python'
