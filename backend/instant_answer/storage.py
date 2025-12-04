"""
Message Storage Service for Instant Answer Recall System.

This module provides message storage functionality using ChromaDB to store
messages with embeddings and metadata for semantic search and retrieval.

Requirements: 6.1, 6.2, 6.3, 10.5
"""

import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
import chromadb

from backend.instant_answer.classifier import MessageType, MessageClassification
from backend.instant_answer.tagger import MessageTags

logger = logging.getLogger(__name__)


@dataclass
class StoredMessage:
    """
    Message stored in ChromaDB.
    
    This dataclass represents a message with all its metadata that will be
    stored in ChromaDB for semantic search and retrieval.
    
    Attributes:
        id: Unique identifier for the message
        message_text: The message content
        username: Author of the message
        user_id: Numeric user ID
        room: Room where message was posted
        timestamp: When the message was posted
        message_type: Classification type (QUESTION, ANSWER, DISCUSSION)
        topic_tags: General topic tags
        tech_keywords: Technology-specific keywords
        contains_code: Whether message contains code blocks
        code_language: Detected programming language (if code present)
        embedding: Vector embedding for semantic search
    
    Requirements: 6.1, 6.2, 6.3, 10.5
    """
    id: str
    message_text: str
    username: str
    user_id: int
    room: str
    timestamp: datetime
    message_type: MessageType
    topic_tags: List[str]
    tech_keywords: List[str]
    contains_code: bool
    code_language: Optional[str]
    embedding: List[float]


class MessageStorageService:
    """
    Service for storing and retrieving messages in ChromaDB.
    
    This service handles:
    - Storing messages with embeddings and metadata
    - Retrieving messages by ID
    - Batch storage for efficiency
    - Error handling for storage failures
    
    Requirements: 6.1, 6.2, 6.3, 10.5
    """
    
    def __init__(
        self,
        chroma_collection: chromadb.Collection,
        gemini_service
    ):
        """
        Initialize the message storage service.
        
        Args:
            chroma_collection: ChromaDB collection for storing messages
            gemini_service: GeminiService instance for embedding generation
        
        Requirements: 6.1
        """
        self.chroma_collection = chroma_collection
        self.gemini_service = gemini_service
    
    async def store_message(
        self,
        message_text: str,
        username: str,
        user_id: int,
        room: str,
        classification: MessageClassification,
        tags: MessageTags,
        message_id: Optional[str] = None
    ) -> StoredMessage:
        """
        Store a message with embeddings and metadata in ChromaDB.
        
        This method:
        1. Generates a unique ID if not provided
        2. Creates an embedding for the message
        3. Stores the message with all metadata in ChromaDB
        4. Returns the StoredMessage object
        
        Args:
            message_text: The message content
            username: Author of the message
            user_id: Numeric user ID
            room: Room where message was posted
            classification: Message classification result
            tags: Message tags (topics, tech keywords, code info)
            message_id: Optional message ID (generates UUID if not provided)
        
        Returns:
            StoredMessage object with all stored data
        
        Raises:
            Exception: If storage fails (caller should handle gracefully)
        
        Requirements: 6.1, 6.2, 6.3, 10.5
        """
        try:
            # Generate message ID if not provided
            if message_id is None:
                message_id = f"msg_{uuid.uuid4()}"
            
            # Generate embedding for the message
            logger.info(f"Generating embedding for message {message_id}")
            embedding = await self._generate_embedding(message_text)
            
            # Create timestamp
            timestamp = datetime.now()
            
            # Create StoredMessage object
            stored_message = StoredMessage(
                id=message_id,
                message_text=message_text,
                username=username,
                user_id=user_id,
                room=room,
                timestamp=timestamp,
                message_type=classification.message_type,
                topic_tags=tags.topic_tags,
                tech_keywords=tags.tech_keywords,
                contains_code=tags.contains_code,
                code_language=tags.code_language,
                embedding=embedding
            )
            
            # Store in ChromaDB
            self._store_in_chromadb(stored_message)
            
            logger.info(
                f"Stored message {message_id} in ChromaDB "
                f"(room: {room}, type: {classification.message_type.value})"
            )
            
            return stored_message
        
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            raise
    
    async def store_messages_batch(
        self,
        messages: List[tuple[str, str, int, str, MessageClassification, MessageTags, Optional[str]]]
    ) -> List[StoredMessage]:
        """
        Store multiple messages in a batch for efficiency.
        
        This method processes multiple messages at once, which is more efficient
        than storing them individually. Useful for indexing historical messages.
        
        Args:
            messages: List of tuples containing:
                (message_text, username, user_id, room, classification, tags, message_id)
        
        Returns:
            List of StoredMessage objects for successfully stored messages
        
        Raises:
            Exception: If batch storage fails
        
        Requirements: 6.1, 6.2, 6.3
        """
        try:
            stored_messages = []
            
            logger.info(f"Batch storing {len(messages)} messages")
            
            # Process each message
            for msg_data in messages:
                message_text, username, user_id, room, classification, tags, message_id = msg_data
                
                try:
                    stored_msg = await self.store_message(
                        message_text=message_text,
                        username=username,
                        user_id=user_id,
                        room=room,
                        classification=classification,
                        tags=tags,
                        message_id=message_id
                    )
                    stored_messages.append(stored_msg)
                
                except Exception as e:
                    logger.error(f"Failed to store message in batch: {e}")
                    # Continue with other messages
                    continue
            
            logger.info(
                f"Batch storage complete: {len(stored_messages)}/{len(messages)} "
                f"messages stored successfully"
            )
            
            return stored_messages
        
        except Exception as e:
            logger.error(f"Batch storage failed: {e}")
            raise
    
    def retrieve_message(self, message_id: str) -> Optional[StoredMessage]:
        """
        Retrieve a message by ID from ChromaDB.
        
        Args:
            message_id: The unique message identifier
        
        Returns:
            StoredMessage object if found, None otherwise
        
        Requirements: 6.3
        """
        try:
            # Query ChromaDB by ID
            results = self.chroma_collection.get(
                ids=[message_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            # Check if message was found
            if not results or not results.get('ids') or not results['ids']:
                logger.warning(f"Message {message_id} not found in ChromaDB")
                return None
            
            # Parse the result
            stored_message = self._parse_chromadb_result(
                message_id=results['ids'][0],
                document=results['documents'][0],
                metadata=results['metadatas'][0],
                embedding=results['embeddings'][0]
            )
            
            logger.info(f"Retrieved message {message_id} from ChromaDB")
            
            return stored_message
        
        except Exception as e:
            logger.error(f"Failed to retrieve message {message_id}: {e}")
            return None
    
    async def update_message(
        self,
        message_id: str,
        message_text: str,
        classification: MessageClassification,
        tags: MessageTags
    ) -> bool:
        """
        Update an existing message in ChromaDB.
        
        This method updates the message content, embedding, and metadata
        when a message is edited.
        
        Args:
            message_id: The unique message identifier
            message_text: Updated message content
            classification: Updated classification
            tags: Updated tags
        
        Returns:
            True if update successful, False otherwise
        
        Requirements: 6.4 (from requirements document)
        """
        try:
            # Retrieve existing message to get other fields
            existing = self.retrieve_message(message_id)
            if not existing:
                logger.warning(f"Cannot update non-existent message {message_id}")
                return False
            
            # Generate new embedding
            embedding = await self._generate_embedding(message_text)
            
            # Update in ChromaDB (convert lists to strings)
            self.chroma_collection.update(
                ids=[message_id],
                documents=[message_text],
                embeddings=[embedding],
                metadatas=[{
                    "username": existing.username,
                    "user_id": existing.user_id,
                    "room": existing.room,
                    "timestamp": existing.timestamp.isoformat(),
                    "message_type": classification.message_type.value,
                    "topic_tags": ",".join(tags.topic_tags) if tags.topic_tags else "",
                    "tech_keywords": ",".join(tags.tech_keywords) if tags.tech_keywords else "",
                    "contains_code": tags.contains_code,
                    "code_language": tags.code_language if tags.code_language else ""
                }]
            )
            
            logger.info(f"Updated message {message_id} in ChromaDB")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update message {message_id}: {e}")
            return False
    
    def delete_message(self, message_id: str) -> bool:
        """
        Delete a message from ChromaDB.
        
        Args:
            message_id: The unique message identifier
        
        Returns:
            True if deletion successful, False otherwise
        
        Requirements: 6.5 (from requirements document)
        """
        try:
            self.chroma_collection.delete(ids=[message_id])
            logger.info(f"Deleted message {message_id} from ChromaDB")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Gemini API.
        
        Args:
            text: The text to embed
        
        Returns:
            List of floats representing the embedding vector
        
        Raises:
            Exception: If embedding generation fails
        
        Requirements: 6.1
        """
        try:
            import google.generativeai as genai
            
            # Generate embedding using Gemini API
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def _store_in_chromadb(self, stored_message: StoredMessage) -> None:
        """
        Store a message in ChromaDB.
        
        Args:
            stored_message: The message to store
        
        Raises:
            Exception: If storage fails
        
        Requirements: 6.2, 6.3, 10.5
        """
        try:
            # Prepare metadata (ChromaDB only supports str, int, float, bool)
            # Convert lists to comma-separated strings
            metadata = {
                "username": stored_message.username,
                "user_id": stored_message.user_id,
                "room": stored_message.room,
                "timestamp": stored_message.timestamp.isoformat(),
                "message_type": stored_message.message_type.value,
                "topic_tags": ",".join(stored_message.topic_tags) if stored_message.topic_tags else "",
                "tech_keywords": ",".join(stored_message.tech_keywords) if stored_message.tech_keywords else "",
                "contains_code": stored_message.contains_code,
                "code_language": stored_message.code_language if stored_message.code_language else ""
            }
            
            # Add to ChromaDB collection
            self.chroma_collection.add(
                ids=[stored_message.id],
                documents=[stored_message.message_text],
                embeddings=[stored_message.embedding],
                metadatas=[metadata]
            )
            
            logger.debug(f"Stored message {stored_message.id} in ChromaDB collection")
        
        except Exception as e:
            logger.error(f"Failed to store in ChromaDB: {e}")
            raise
    
    def _parse_chromadb_result(
        self,
        message_id: str,
        document: str,
        metadata: dict,
        embedding: List[float]
    ) -> StoredMessage:
        """
        Parse ChromaDB result into StoredMessage object.
        
        Args:
            message_id: Message ID from ChromaDB
            document: Message text from ChromaDB
            metadata: Metadata dict from ChromaDB
            embedding: Embedding vector from ChromaDB
        
        Returns:
            StoredMessage object
        
        Requirements: 6.3
        """
        # Parse timestamp
        timestamp_str = metadata.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            timestamp = datetime.now()
        
        # Parse message type
        message_type_str = metadata.get('message_type', 'discussion')
        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            message_type = MessageType.DISCUSSION
        
        # Parse lists from comma-separated strings
        topic_tags_str = metadata.get('topic_tags', '')
        topic_tags = [tag.strip() for tag in topic_tags_str.split(',') if tag.strip()] if topic_tags_str else []
        
        tech_keywords_str = metadata.get('tech_keywords', '')
        tech_keywords = [kw.strip() for kw in tech_keywords_str.split(',') if kw.strip()] if tech_keywords_str else []
        
        code_language = metadata.get('code_language', '')
        code_language = code_language if code_language else None
        
        return StoredMessage(
            id=message_id,
            message_text=document,
            username=metadata.get('username', 'unknown'),
            user_id=metadata.get('user_id', 0),
            room=metadata.get('room', 'unknown'),
            timestamp=timestamp,
            message_type=message_type,
            topic_tags=topic_tags,
            tech_keywords=tech_keywords,
            contains_code=metadata.get('contains_code', False),
            code_language=code_language,
            embedding=embedding
        )
