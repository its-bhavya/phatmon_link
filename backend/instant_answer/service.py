"""
Instant Answer Service Orchestrator for Instant Answer Recall System.

This module provides the main orchestration service that coordinates all
instant answer operations including classification, tagging, search, summary
generation, and storage.

Requirements: 1.2, 1.4, 1.5, 10.1, 10.2, 8.1, 8.2, 8.3, 8.4, 8.5
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.classifier import MessageClassifier, MessageType, MessageClassification
from backend.instant_answer.tagger import AutoTagger, MessageTags
from backend.instant_answer.search_engine import SemanticSearchEngine, SearchResult
from backend.instant_answer.summary_generator import SummaryGenerator, InstantAnswer
from backend.instant_answer.storage import MessageStorageService

logger = logging.getLogger(__name__)


class InstantAnswerError(Exception):
    """Base exception for instant answer system."""
    pass


class ClassificationError(InstantAnswerError):
    """Error during message classification."""
    pass


class SearchError(InstantAnswerError):
    """Error during semantic search."""
    pass


class SummaryError(InstantAnswerError):
    """Error during summary generation."""
    pass


class StorageError(InstantAnswerError):
    """Error during message storage."""
    pass


@dataclass
class User:
    """
    User data for instant answer processing.
    
    Attributes:
        user_id: Numeric user ID
        username: User's display name
    """
    user_id: int
    username: str


class InstantAnswerService:
    """
    Main orchestrator for instant answer recall functionality.
    
    This service coordinates all instant answer operations:
    1. Message classification (question/answer/discussion)
    2. Auto-tagging (topics, tech keywords, code detection)
    3. Semantic search (find similar past messages)
    4. Summary generation (create coherent answers)
    5. Message storage (store with embeddings and metadata)
    
    The service implements graceful error handling to ensure that failures
    in AI processing never prevent normal chat functionality.
    
    Requirements: 1.2, 1.4, 1.5, 10.1, 10.2, 8.1, 8.2, 8.3, 8.4, 8.5
    """
    
    def __init__(
        self,
        gemini_service,
        chroma_collection,
        config: InstantAnswerConfig
    ):
        """
        Initialize the instant answer service.
        
        Args:
            gemini_service: GeminiService instance for API calls
            chroma_collection: ChromaDB collection for vector storage
            config: Configuration for instant answer system
        
        Requirements: 1.2, 10.1
        """
        self.config = config
        
        # Initialize sub-services
        self.classifier = MessageClassifier(gemini_service)
        self.tagger = AutoTagger(gemini_service)
        self.search_engine = SemanticSearchEngine(
            gemini_service,
            chroma_collection,
            config.embedding_model
        )
        self.summary_generator = SummaryGenerator(
            gemini_service,
            config.max_summary_tokens
        )
        self.storage_service = MessageStorageService(
            chroma_collection,
            gemini_service
        )
        
        logger.info(
            f"InstantAnswerService initialized "
            f"(enabled={config.enabled}, target_room={config.target_room})"
        )
    
    async def process_message(
        self,
        message: str,
        user: User,
        room: str
    ) -> Optional[InstantAnswer]:
        """
        Process a message and generate instant answer if applicable.
        
        This is the main entry point for instant answer processing. It:
        1. Checks if the system is enabled and room matches target
        2. Classifies the message type
        3. Tags the message with metadata
        4. Stores the message in ChromaDB
        5. If it's a question, searches for similar past messages
        6. Generates an AI summary from search results
        7. Returns the instant answer (or None if not a question)
        
        The method implements graceful error handling at each step to ensure
        that failures never prevent normal message posting.
        
        Args:
            message: The message text to process
            user: User object with user_id and username
            room: Room where message was posted
        
        Returns:
            InstantAnswer if question detected and answer generated, None otherwise
        
        Requirements: 1.2, 1.4, 1.5, 10.1, 10.2, 8.1, 8.2, 8.3, 8.4, 8.5
        """
        try:
            # Check if system is enabled
            if not self.config.enabled:
                logger.debug("Instant answer system is disabled")
                return None
            
            # Check if room matches target room (Techline only)
            if room != self.config.target_room:
                logger.debug(
                    f"Skipping instant answer for room '{room}' "
                    f"(target room: '{self.config.target_room}')"
                )
                return None
            
            logger.info(
                f"Processing message from {user.username} in {room}: "
                f"{message[:50]}..."
            )
            
            # Step 1: Classify the message
            classification = await self._classify_message_with_fallback(message)
            
            # Step 2: Tag the message
            tags = await self._tag_message_with_fallback(message)
            
            # Step 3: Store the message (always store, even if other steps fail)
            await self._store_message_with_fallback(
                message, user, room, classification, tags
            )
            
            # Step 4: If it's a question, search and generate instant answer
            if classification.message_type == MessageType.QUESTION:
                logger.info(f"Question detected, initiating search and summary")
                
                # Check confidence threshold
                if classification.confidence < self.config.classification_confidence_threshold:
                    logger.warning(
                        f"Classification confidence {classification.confidence:.2f} "
                        f"below threshold {self.config.classification_confidence_threshold}, "
                        f"skipping instant answer"
                    )
                    return None
                
                # Search for similar past messages
                search_results = await self._search_with_fallback(message, room)
                
                # Generate summary if we have results
                if search_results:
                    instant_answer = await self._generate_summary_with_fallback(
                        message, search_results
                    )
                    
                    if instant_answer:
                        logger.info(
                            f"Generated instant answer with {len(instant_answer.source_messages)} "
                            f"sources (confidence: {instant_answer.confidence:.2f})"
                        )
                        return instant_answer
                else:
                    logger.info("No relevant search results found, returning novel question")
                    return InstantAnswer(
                        summary="This appears to be a novel question! No similar discussions found in the history.",
                        source_messages=[],
                        confidence=1.0,
                        is_novel_question=True
                    )
            
            # Not a question, no instant answer needed
            logger.debug(
                f"Message classified as {classification.message_type.value}, "
                f"no instant answer needed"
            )
            return None
        
        except Exception as e:
            # Catch-all error handler to ensure we never crash
            logger.error(f"Unexpected error in process_message: {e}", exc_info=True)
            return None
    
    async def _classify_message_with_fallback(
        self,
        message: str
    ) -> MessageClassification:
        """
        Classify message with graceful error handling.
        
        If classification fails, defaults to DISCUSSION type to allow
        normal message posting to continue.
        
        Args:
            message: The message to classify
        
        Returns:
            MessageClassification (defaults to DISCUSSION on failure)
        
        Requirements: 8.3
        """
        try:
            classification = await self.classifier.classify(message)
            logger.debug(
                f"Classified as {classification.message_type.value} "
                f"(confidence: {classification.confidence:.2f})"
            )
            return classification
        
        except Exception as e:
            logger.warning(
                f"Classification failed, defaulting to DISCUSSION: {e}"
            )
            # Fallback to DISCUSSION type
            return MessageClassification(
                message_type=MessageType.DISCUSSION,
                confidence=0.5,
                contains_code=False,
                reasoning="Classification failed, using fallback"
            )
    
    async def _tag_message_with_fallback(
        self,
        message: str
    ) -> MessageTags:
        """
        Tag message with graceful error handling.
        
        If tagging fails, returns empty tags to allow processing to continue.
        
        Args:
            message: The message to tag
        
        Returns:
            MessageTags (empty tags on failure)
        
        Requirements: 8.3
        """
        try:
            tags = await self.tagger.tag_message(message)
            logger.debug(
                f"Tagged with {len(tags.topic_tags)} topics, "
                f"{len(tags.tech_keywords)} tech keywords"
            )
            return tags
        
        except Exception as e:
            logger.warning(f"Tagging failed, using empty tags: {e}")
            # Fallback to empty tags
            return MessageTags(
                topic_tags=[],
                tech_keywords=[],
                contains_code=False,
                code_language=None
            )
    
    async def _store_message_with_fallback(
        self,
        message: str,
        user: User,
        room: str,
        classification: MessageClassification,
        tags: MessageTags
    ) -> None:
        """
        Store message with graceful error handling.
        
        Logs errors but doesn't raise exceptions to ensure message
        posting continues even if storage fails.
        
        Args:
            message: The message text
            user: User object
            room: Room name
            classification: Message classification
            tags: Message tags
        
        Requirements: 8.2, 8.5
        """
        try:
            await self.storage_service.store_message(
                message_text=message,
                username=user.username,
                user_id=user.user_id,
                room=room,
                classification=classification,
                tags=tags
            )
            logger.debug(f"Stored message in ChromaDB")
        
        except Exception as e:
            logger.error(
                f"Failed to store message in ChromaDB: {e}. "
                f"Message will still be posted normally."
            )
            # Don't raise - allow message posting to continue
    
    async def _search_with_fallback(
        self,
        query: str,
        room: str
    ) -> list[SearchResult]:
        """
        Search for similar messages with graceful error handling.
        
        If search fails, returns empty list to allow processing to continue.
        
        Args:
            query: The search query
            room: Room to filter by
        
        Returns:
            List of SearchResult objects (empty on failure)
        
        Requirements: 8.1, 8.4
        """
        try:
            search_results = await self.search_engine.search(
                query=query,
                room_filter=room,
                message_type_filter=MessageType.ANSWER,
                limit=self.config.max_search_results,
                min_similarity=self.config.min_similarity_threshold
            )
            logger.debug(f"Found {len(search_results)} search results")
            return search_results
        
        except Exception as e:
            logger.warning(f"Search failed, returning empty results: {e}")
            # Fallback to empty results
            return []
    
    async def _generate_summary_with_fallback(
        self,
        question: str,
        search_results: list[SearchResult]
    ) -> Optional[InstantAnswer]:
        """
        Generate summary with graceful error handling.
        
        If summary generation fails, returns None to allow processing to continue.
        
        Args:
            question: The user's question
            search_results: Search results to summarize
        
        Returns:
            InstantAnswer or None on failure
        
        Requirements: 8.1
        """
        try:
            instant_answer = await self.summary_generator.generate_summary(
                question=question,
                search_results=search_results
            )
            logger.debug("Generated summary successfully")
            return instant_answer
        
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            # Fallback to None - no instant answer will be sent
            return None
