"""
Background Message Indexer for Instant Answer Recall System.

This module provides background indexing functionality to process and store
historical messages from chat rooms into ChromaDB for semantic search.

Requirements: 6.1, 6.2, 6.3
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.instant_answer.service import InstantAnswerService, User
from backend.instant_answer.classifier import MessageClassification, MessageType
from backend.instant_answer.tagger import MessageTags

logger = logging.getLogger(__name__)


class MessageIndexer:
    """
    Background indexer for processing historical messages.
    
    This service:
    - Fetches historical messages from room history
    - Processes messages in batches for efficiency
    - Classifies and tags each message
    - Stores messages with embeddings in ChromaDB
    - Provides progress logging
    - Handles messages without embeddings
    
    Requirements: 6.1, 6.2, 6.3
    """
    
    def __init__(
        self,
        instant_answer_service: InstantAnswerService,
        batch_size: int = 10
    ):
        """
        Initialize the message indexer.
        
        Args:
            instant_answer_service: InstantAnswerService instance for processing
            batch_size: Number of messages to process in each batch
        
        Requirements: 6.1
        """
        self.instant_answer_service = instant_answer_service
        self.batch_size = batch_size
        self.total_processed = 0
        self.total_stored = 0
        self.total_failed = 0
    
    async def index_room_messages(
        self,
        room_name: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Index all messages from a specific room.
        
        This method processes messages in batches, classifying and tagging
        each message before storing it in ChromaDB with embeddings.
        
        Args:
            room_name: Name of the room being indexed
            messages: List of message dicts from room history
        
        Returns:
            Dict with statistics: processed, stored, failed counts
        
        Requirements: 6.1, 6.2, 6.3
        """
        import time
        start_time = time.time()
        
        logger.info(
            f"[INDEXER] Starting indexing | "
            f"room={room_name} "
            f"total_messages={len(messages)} "
            f"batch_size={self.batch_size}"
        )
        
        self.total_processed = 0
        self.total_stored = 0
        self.total_failed = 0
        
        # Process messages in batches
        for i in range(0, len(messages), self.batch_size):
            batch = messages[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(messages) + self.batch_size - 1) // self.batch_size
            
            batch_start = time.time()
            logger.info(
                f"[INDEXER] Processing batch | "
                f"batch={batch_num}/{total_batches} "
                f"messages={len(batch)}"
            )
            
            await self._process_batch(room_name, batch)
            
            batch_time = time.time() - batch_start
            success_rate = (self.total_stored / self.total_processed * 100) if self.total_processed > 0 else 0
            
            # Log progress
            logger.info(
                f"[INDEXER] Batch complete | "
                f"batch={batch_num}/{total_batches} "
                f"processed={self.total_processed}/{len(messages)} "
                f"stored={self.total_stored} "
                f"failed={self.total_failed} "
                f"success_rate={success_rate:.1f}% "
                f"batch_time={batch_time:.3f}s"
            )
        
        total_time = time.time() - start_time
        success_rate = (self.total_stored / self.total_processed * 100) if self.total_processed > 0 else 0
        
        logger.info(
            f"[INDEXER] Indexing complete | "
            f"room={room_name} "
            f"processed={self.total_processed} "
            f"stored={self.total_stored} "
            f"failed={self.total_failed} "
            f"success_rate={success_rate:.1f}% "
            f"total_time={total_time:.3f}s"
        )
        
        return {
            "processed": self.total_processed,
            "stored": self.total_stored,
            "failed": self.total_failed
        }
    
    async def _process_batch(
        self,
        room_name: str,
        batch: List[Dict[str, Any]]
    ) -> None:
        """
        Process a batch of messages.
        
        Args:
            room_name: Name of the room
            batch: List of message dicts to process
        
        Requirements: 6.1, 6.2, 6.3
        """
        for message_data in batch:
            self.total_processed += 1
            
            try:
                # Extract message fields
                message_text = message_data.get("content", "")
                username = message_data.get("username", "unknown")
                timestamp_str = message_data.get("timestamp")
                
                # Skip empty messages
                if not message_text or not message_text.strip():
                    logger.debug(
                        f"[INDEXER] Skipping empty message | "
                        f"user={username}"
                    )
                    self.total_failed += 1
                    continue
                
                # Skip system messages
                message_type = message_data.get("type", "")
                if message_type in ["system", "error", "support_response", "instant_answer"]:
                    logger.debug(
                        f"[INDEXER] Skipping system message | "
                        f"type={message_type}"
                    )
                    self.total_failed += 1
                    continue
                
                # Parse timestamp
                try:
                    if timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.utcnow()
                except (ValueError, TypeError):
                    timestamp = datetime.utcnow()
                
                # Classify the message
                classification = await self._classify_message_safe(message_text)
                
                # Tag the message
                tags = await self._tag_message_safe(message_text)
                
                # Create a user object (we don't have user_id from history, use 0)
                user = User(user_id=0, username=username)
                
                # Store the message
                await self._store_message_safe(
                    message_text=message_text,
                    user=user,
                    room=room_name,
                    classification=classification,
                    tags=tags,
                    timestamp=timestamp
                )
                
                self.total_stored += 1
                
                logger.debug(
                    f"[INDEXER] Message indexed | "
                    f"user={username} "
                    f"type={classification.message_type.value} "
                    f"progress={self.total_stored}/{self.total_processed}"
                )
                
            except Exception as e:
                logger.error(
                    f"[INDEXER] Failed to process message | "
                    f"error={str(e)} "
                    f"user={username} "
                    f"progress={self.total_processed}",
                    exc_info=True
                )
                self.total_failed += 1
                continue
    
    async def _classify_message_safe(
        self,
        message: str
    ) -> MessageClassification:
        """
        Classify message with error handling.
        
        Args:
            message: The message to classify
        
        Returns:
            MessageClassification (defaults to DISCUSSION on failure)
        
        Requirements: 6.2
        """
        try:
            classification = await self.instant_answer_service.classifier.classify(message)
            return classification
        except Exception as e:
            logger.warning(f"Classification failed during indexing: {e}")
            # Fallback to DISCUSSION
            return MessageClassification(
                message_type=MessageType.DISCUSSION,
                confidence=0.5,
                contains_code=False,
                reasoning="Classification failed during indexing"
            )
    
    async def _tag_message_safe(
        self,
        message: str
    ) -> MessageTags:
        """
        Tag message with error handling.
        
        Args:
            message: The message to tag
        
        Returns:
            MessageTags (empty tags on failure)
        
        Requirements: 6.2
        """
        try:
            tags = await self.instant_answer_service.tagger.tag_message(message)
            return tags
        except Exception as e:
            logger.warning(f"Tagging failed during indexing: {e}")
            # Fallback to empty tags
            return MessageTags(
                topic_tags=[],
                tech_keywords=[],
                contains_code=False,
                code_language=None
            )
    
    async def _store_message_safe(
        self,
        message_text: str,
        user: User,
        room: str,
        classification: MessageClassification,
        tags: MessageTags,
        timestamp: datetime
    ) -> None:
        """
        Store message with error handling.
        
        Args:
            message_text: The message content
            user: User object
            room: Room name
            classification: Message classification
            tags: Message tags
            timestamp: Message timestamp
        
        Requirements: 6.1, 6.2, 6.3
        """
        try:
            # Generate a unique message ID based on timestamp and username
            message_id = f"msg_{timestamp.timestamp()}_{user.username}"
            
            await self.instant_answer_service.storage_service.store_message(
                message_text=message_text,
                username=user.username,
                user_id=user.user_id,
                room=room,
                classification=classification,
                tags=tags,
                message_id=message_id
            )
        except Exception as e:
            logger.error(f"Failed to store message during indexing: {e}")
            raise


async def index_historical_messages(
    instant_answer_service: InstantAnswerService,
    room_service,
    target_room: str = "Techline",
    batch_size: int = 10
) -> Dict[str, int]:
    """
    Index all historical messages from a specific room.
    
    This is a convenience function that creates an indexer and processes
    all messages from the specified room's history.
    
    Args:
        instant_answer_service: InstantAnswerService instance
        room_service: RoomService instance to get room history
        target_room: Name of room to index (default: Techline)
        batch_size: Number of messages to process per batch
    
    Returns:
        Dict with statistics: processed, stored, failed counts
    
    Requirements: 6.1, 6.2, 6.3
    """
    logger.info(f"Starting historical message indexing for room: {target_room}")
    
    # Get the room
    room = room_service.get_room(target_room)
    if not room:
        logger.error(f"Room '{target_room}' not found")
        return {
            "processed": 0,
            "stored": 0,
            "failed": 0
        }
    
    # Get all messages from room history
    messages = room.get_recent_messages(limit=1000)  # Get up to 1000 messages
    
    if not messages:
        logger.info(f"No messages found in room '{target_room}'")
        return {
            "processed": 0,
            "stored": 0,
            "failed": 0
        }
    
    # Create indexer and process messages
    indexer = MessageIndexer(
        instant_answer_service=instant_answer_service,
        batch_size=batch_size
    )
    
    stats = await indexer.index_room_messages(target_room, messages)
    
    logger.info(
        f"Historical indexing complete: "
        f"{stats['stored']}/{stats['processed']} messages indexed"
    )
    
    return stats
