"""
Semantic Search Engine for Instant Answer Recall System.

This module provides semantic search functionality using ChromaDB vector search
and Gemini embeddings to find similar messages based on content similarity.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.2, 8.4
"""

import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import chromadb

from backend.instant_answer.classifier import MessageType
from backend.instant_answer.tagger import MessageTags
from backend.instant_answer.retry_utils import retry_with_backoff, with_timeout

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """
    Single search result from ChromaDB.
    
    Attributes:
        message_id: Unique identifier for the message
        message_text: The message content
        username: Author of the message
        timestamp: When the message was posted
        similarity_score: Cosine similarity score (0.0-1.0)
        tags: Message tags (topics, tech keywords, code info)
        room: Room where message was posted
    
    Requirements: 3.4
    """
    message_id: str
    message_text: str
    username: str
    timestamp: datetime
    similarity_score: float
    tags: MessageTags
    room: str


class SemanticSearchEngine:
    """
    Semantic search using ChromaDB and Gemini embeddings.
    
    This engine performs vector similarity search to find messages that are
    semantically similar to a query, even when wording differs. It uses:
    - Gemini API for generating embeddings
    - ChromaDB for vector storage and similarity search
    - Metadata filters for refining results (room, message type, tags)
    - Similarity threshold filtering to ensure quality results
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    
    def __init__(
        self,
        gemini_service,
        chroma_collection: chromadb.Collection,
        embedding_model: str = "models/text-embedding-004"
    ):
        """
        Initialize the semantic search engine.
        
        Args:
            gemini_service: GeminiService instance for embedding generation
            chroma_collection: ChromaDB collection for vector search
            embedding_model: Gemini embedding model name
        
        Requirements: 3.1, 3.2
        """
        self.gemini_service = gemini_service
        self.chroma_collection = chroma_collection
        self.embedding_model = embedding_model
    
    async def search(
        self,
        query: str,
        room_filter: str = "Techline",
        message_type_filter: Optional[MessageType] = MessageType.ANSWER,
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[SearchResult]:
        """
        Search for similar messages using vector similarity.
        
        This method:
        1. Generates an embedding for the query using Gemini API (with timeout)
        2. Queries ChromaDB for similar message vectors (with retry)
        3. Applies metadata filters (room, message type)
        4. Ranks results by similarity score
        5. Filters out results below similarity threshold
        
        Args:
            query: The search query text
            room_filter: Filter results to specific room (default: "Techline")
            message_type_filter: Filter by message type (default: ANSWER)
            limit: Maximum number of results to return
            min_similarity: Minimum similarity score threshold (0.0-1.0)
        
        Returns:
            List of SearchResult objects, ranked by similarity score
        
        Raises:
            Exception: If search fails (caller should handle gracefully)
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.2, 8.4
        """
        try:
            # Generate embedding for the query with timeout (2 seconds)
            logger.info(f"Generating embedding for query: {query[:50]}...")
            query_embedding = await with_timeout(
                self.generate_embedding,
                query,
                timeout=2.0,
                operation_name="embedding_generation"
            )
            
            # Build metadata filter with proper ChromaDB operators
            if message_type_filter:
                where_filter = {
                    "$and": [
                        {"room": {"$eq": room_filter}},
                        {"message_type": {"$eq": message_type_filter.value}}
                    ]
                }
            else:
                where_filter = {"room": {"$eq": room_filter}}
            
            logger.info(
                f"Searching ChromaDB with filters: room={room_filter}, "
                f"message_type={message_type_filter.value if message_type_filter else 'any'}"
            )
            
            # Query ChromaDB for similar vectors with retry (1 retry, 0.5s delay)
            results = await retry_with_backoff(
                self._query_chromadb,
                query_embedding,
                limit,
                where_filter,
                max_retries=1,
                initial_delay=0.5,
                operation_name="chromadb_query"
            )
            
            # Parse and rank results
            search_results = self._parse_search_results(results, min_similarity)
            
            # Sort by similarity score (descending) and limit
            search_results.sort(key=lambda x: x.similarity_score, reverse=True)
            search_results = search_results[:limit]
            
            logger.info(
                f"Found {len(search_results)} results above similarity threshold "
                f"{min_similarity}"
            )
            
            return search_results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def _query_chromadb(
        self,
        query_embedding: List[float],
        limit: int,
        where_filter: dict
    ) -> dict:
        """
        Query ChromaDB with the given parameters.
        
        This is a separate method to allow retry logic to be applied.
        
        Args:
            query_embedding: The query embedding vector
            limit: Number of results to return
            where_filter: Metadata filters
        
        Returns:
            ChromaDB query results
        
        Requirements: 8.2
        """
        # ChromaDB query is synchronous, wrap in asyncio.to_thread
        return await asyncio.to_thread(
            self.chroma_collection.query,
            query_embeddings=[query_embedding],
            n_results=limit * 2,  # Get more results to filter by threshold
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Gemini API.
        
        Uses Google's Gemini embedding model to convert text into a
        high-dimensional vector representation for semantic similarity search.
        
        Args:
            text: The text to embed
        
        Returns:
            List of floats representing the embedding vector
        
        Raises:
            Exception: If embedding generation fails
        
        Requirements: 3.1
        """
        try:
            import google.generativeai as genai
            
            # Generate embedding using Gemini API (newer model)
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def _parse_search_results(
        self,
        results: dict,
        min_similarity: float
    ) -> List[SearchResult]:
        """
        Parse ChromaDB query results into SearchResult objects.
        
        Converts ChromaDB's raw query results into structured SearchResult
        objects, filtering by similarity threshold and extracting metadata.
        
        Args:
            results: Raw results from ChromaDB query
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of SearchResult objects above threshold
        
        Requirements: 3.4, 3.5
        """
        search_results = []
        
        # ChromaDB returns results as lists within lists
        if not results or not results.get('ids') or not results['ids'][0]:
            return search_results
        
        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        for i in range(len(ids)):
            # Convert distance to similarity score (cosine similarity)
            # ChromaDB returns cosine distance, so similarity = 1 - distance
            similarity_score = 1.0 - distances[i]
            
            # Filter by similarity threshold
            if similarity_score < min_similarity:
                logger.debug(
                    f"Filtering result {ids[i]} with similarity {similarity_score:.3f} "
                    f"(below threshold {min_similarity})"
                )
                continue
            
            metadata = metadatas[i]
            
            # Parse timestamp
            timestamp_str = metadata.get('timestamp', '')
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                timestamp = datetime.now()
            
            # Reconstruct MessageTags from metadata
            # Handle both list format (from tests) and string format (from storage)
            topic_tags_raw = metadata.get('topic_tags', '')
            if isinstance(topic_tags_raw, list):
                topic_tags = topic_tags_raw
            elif isinstance(topic_tags_raw, str):
                topic_tags = [tag.strip() for tag in topic_tags_raw.split(',') if tag.strip()] if topic_tags_raw else []
            else:
                topic_tags = []
            
            tech_keywords_raw = metadata.get('tech_keywords', '')
            if isinstance(tech_keywords_raw, list):
                tech_keywords = tech_keywords_raw
            elif isinstance(tech_keywords_raw, str):
                tech_keywords = [kw.strip() for kw in tech_keywords_raw.split(',') if kw.strip()] if tech_keywords_raw else []
            else:
                tech_keywords = []
            
            code_language = metadata.get('code_language', '')
            code_language = code_language if code_language else None
            
            tags = MessageTags(
                topic_tags=topic_tags,
                tech_keywords=tech_keywords,
                contains_code=metadata.get('contains_code', False),
                code_language=code_language
            )
            
            # Create SearchResult
            search_result = SearchResult(
                message_id=ids[i],
                message_text=documents[i],
                username=metadata.get('username', 'unknown'),
                timestamp=timestamp,
                similarity_score=similarity_score,
                tags=tags,
                room=metadata.get('room', 'unknown')
            )
            
            search_results.append(search_result)
        
        return search_results
