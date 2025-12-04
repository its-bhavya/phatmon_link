"""
Tests for Semantic Search Engine.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.instant_answer.search_engine import (
    SemanticSearchEngine,
    SearchResult
)
from backend.instant_answer.classifier import MessageType
from backend.instant_answer.tagger import MessageTags


class TestSemanticSearchEngine:
    """Test suite for semantic search engine."""
    
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
            mock_chroma_collection,
            embedding_model="models/embedding-001"
        )
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, search_engine):
        """Test embedding generation using Gemini API."""
        with patch('google.generativeai.embed_content') as mock_embed:
            mock_embed.return_value = {
                'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]
            }
            
            embedding = await search_engine.generate_embedding("test query")
            
            assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_embed.assert_called_once_with(
                model="models/embedding-001",
                content="test query",
                task_type="retrieval_document"
            )
    
    @pytest.mark.asyncio
    async def test_search_with_results(self, search_engine, mock_chroma_collection):
        """Test search that returns results above threshold."""
        # Mock embedding generation
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            # Mock ChromaDB query results
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1', 'msg2']],
                'documents': [['Answer 1', 'Answer 2']],
                'metadatas': [[
                    {
                        'username': 'alice',
                        'timestamp': '2025-12-05T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': ['python'],
                        'tech_keywords': ['fastapi'],
                        'contains_code': True,
                        'code_language': 'python'
                    },
                    {
                        'username': 'bob',
                        'timestamp': '2025-12-05T11:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': ['javascript'],
                        'tech_keywords': ['react'],
                        'contains_code': False,
                        'code_language': None
                    }
                ]],
                'distances': [[0.2, 0.4]]  # Similarity scores: 0.8, 0.6
            }
            
            results = await search_engine.search(
                query="How do I use FastAPI?",
                room_filter="Techline",
                message_type_filter=MessageType.ANSWER,
                limit=5,
                min_similarity=0.5
            )
            
            assert len(results) == 2
            assert results[0].message_id == 'msg1'
            assert results[0].similarity_score == 0.8
            assert results[0].username == 'alice'
            assert results[1].message_id == 'msg2'
            assert results[1].similarity_score == 0.6
    
    @pytest.mark.asyncio
    async def test_search_filters_by_threshold(self, search_engine, mock_chroma_collection):
        """Test that search filters out results below similarity threshold."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            # Mock results with varying similarity scores
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1', 'msg2', 'msg3']],
                'documents': [['Answer 1', 'Answer 2', 'Answer 3']],
                'metadatas': [[
                    {
                        'username': 'alice',
                        'timestamp': '2025-12-05T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    },
                    {
                        'username': 'bob',
                        'timestamp': '2025-12-05T11:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    },
                    {
                        'username': 'charlie',
                        'timestamp': '2025-12-05T12:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    }
                ]],
                'distances': [[0.1, 0.4, 0.5]]  # Similarities: 0.9, 0.6, 0.5
            }
            
            # Set threshold to 0.7 - should only return first result
            results = await search_engine.search(
                query="test query",
                min_similarity=0.7
            )
            
            assert len(results) == 1
            assert results[0].similarity_score == 0.9
    
    @pytest.mark.asyncio
    async def test_search_returns_empty_for_no_matches(self, search_engine, mock_chroma_collection):
        """Test that search returns empty list when no results above threshold."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            # Mock results all below threshold
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1']],
                'documents': [['Answer 1']],
                'metadatas': [[
                    {
                        'username': 'alice',
                        'timestamp': '2025-12-05T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    }
                ]],
                'distances': [[0.5]]  # Similarity: 0.5
            }
            
            # Set threshold to 0.7 - should return empty
            results = await search_engine.search(
                query="test query",
                min_similarity=0.7
            )
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_applies_metadata_filters(self, search_engine, mock_chroma_collection):
        """Test that search applies room and message type filters."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            mock_chroma_collection.query.return_value = {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
            
            await search_engine.search(
                query="test query",
                room_filter="Techline",
                message_type_filter=MessageType.ANSWER,
                limit=5,
                min_similarity=0.7
            )
            
            # Verify ChromaDB was called with correct filters
            mock_chroma_collection.query.assert_called_once()
            call_args = mock_chroma_collection.query.call_args
            
            assert call_args[1]['where'] == {
                'room': 'Techline',
                'message_type': 'answer'
            }
    
    @pytest.mark.asyncio
    async def test_search_ranks_by_similarity(self, search_engine, mock_chroma_collection):
        """Test that search results are ranked by similarity score."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            # Mock results in non-sorted order
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1', 'msg2', 'msg3']],
                'documents': [['Answer 1', 'Answer 2', 'Answer 3']],
                'metadatas': [[
                    {
                        'username': 'alice',
                        'timestamp': '2025-12-05T10:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    },
                    {
                        'username': 'bob',
                        'timestamp': '2025-12-05T11:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    },
                    {
                        'username': 'charlie',
                        'timestamp': '2025-12-05T12:00:00',
                        'room': 'Techline',
                        'message_type': 'answer',
                        'topic_tags': [],
                        'tech_keywords': [],
                        'contains_code': False,
                        'code_language': None
                    }
                ]],
                'distances': [[0.4, 0.1, 0.3]]  # Similarities: 0.6, 0.9, 0.7
            }
            
            results = await search_engine.search(
                query="test query",
                min_similarity=0.5
            )
            
            # Should be sorted by similarity (descending)
            assert len(results) == 3
            assert results[0].similarity_score == 0.9
            assert results[1].similarity_score == 0.7
            assert results[2].similarity_score == 0.6
    
    @pytest.mark.asyncio
    async def test_search_respects_limit(self, search_engine, mock_chroma_collection):
        """Test that search respects the result limit."""
        with patch.object(search_engine, 'generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            
            # Mock 5 results
            mock_chroma_collection.query.return_value = {
                'ids': [['msg1', 'msg2', 'msg3', 'msg4', 'msg5']],
                'documents': [['A1', 'A2', 'A3', 'A4', 'A5']],
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
                    for i in range(5)
                ]],
                'distances': [[0.1, 0.2, 0.3, 0.4, 0.5]]
            }
            
            # Request only 3 results
            results = await search_engine.search(
                query="test query",
                limit=3,
                min_similarity=0.0
            )
            
            assert len(results) == 3
    
    def test_parse_search_results_with_tags(self, search_engine):
        """Test parsing of search results with complete metadata."""
        raw_results = {
            'ids': [['msg1']],
            'documents': [['Test message']],
            'metadatas': [[
                {
                    'username': 'alice',
                    'timestamp': '2025-12-05T10:00:00',
                    'room': 'Techline',
                    'message_type': 'answer',
                    'topic_tags': ['python', 'api'],
                    'tech_keywords': ['fastapi', 'uvicorn'],
                    'contains_code': True,
                    'code_language': 'python'
                }
            ]],
            'distances': [[0.2]]
        }
        
        results = search_engine._parse_search_results(raw_results, min_similarity=0.5)
        
        assert len(results) == 1
        assert results[0].message_id == 'msg1'
        assert results[0].message_text == 'Test message'
        assert results[0].username == 'alice'
        assert results[0].similarity_score == 0.8
        assert results[0].tags.topic_tags == ['python', 'api']
        assert results[0].tags.tech_keywords == ['fastapi', 'uvicorn']
        assert results[0].tags.contains_code is True
        assert results[0].tags.code_language == 'python'
    
    def test_parse_search_results_empty(self, search_engine):
        """Test parsing of empty search results."""
        raw_results = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        results = search_engine._parse_search_results(raw_results, min_similarity=0.5)
        
        assert len(results) == 0
