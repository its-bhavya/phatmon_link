"""
Fast Batch Message Indexer for Instant Answer Recall System.

This module provides optimized batch indexing with parallel embedding generation
and bulk ChromaDB inserts for processing large volumes of historical messages.

Requirements: 6.1, 6.2, 6.3
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from backend.instant_answer.classifier import MessageClassification, MessageType
from backend.instant_answer.tagger import MessageTags

logger = logging.getLogger(__name__)


class FastMessageIndexer:
    """
    High-performance batch indexer for historical messages.
    
    This indexer uses:
    - Parallel batch embedding (12 texts per batch, 10 workers)
    - Bulk ChromaDB inserts (1000 items at a time)
    - Efficient metadata pre-processing
    
    This is significantly faster than the standard indexer for large datasets.
    
    Requirements: 6.1, 6.2, 6.3
    """
    
    def __init__(
        self,
        instant_answer_service,
        embedding_batch_size: int = 12,
        max_workers: int = 10,
        chromadb_batch_size: int = 1000
    ):
        """
        Initialize the fast message indexer.
        
        Args:
            instant_answer_service: InstantAnswerService instance
            embedding_batch_size: Number of texts to embed per API call
            max_workers: Number of parallel workers for embedding
            chromadb_batch_size: Number of items to insert into ChromaDB at once
        
        Requirements: 6.1
        """
        self.instant_answer_service = instant_answer_service
        self.embedding_batch_size = embedding_batch_size
        self.max_workers = max_workers
        self.chromadb_batch_size = chromadb_batch_size
        self.total_processed = 0
        self.total_stored = 0
        self.total_failed = 0
    
    async def index_room_messages_fast(
        self,
        room_name: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Index messages using fast batch processing.
        
        This method:
        1. Pre-filters and validates all messages
        2. Classifies and tags messages in batches
        3. Generates embeddings in parallel batches
        4. Bulk inserts into ChromaDB
        
        Args:
            room_name: Name of the room being indexed
            messages: List of message dicts from room history
        
        Returns:
            Dict with statistics: processed, stored, failed counts
        
        Requirements: 6.1, 6.2, 6.3
        """
        logger.info(
            f"Starting FAST indexing for room '{room_name}' "
            f"({len(messages)} messages)"
        )
        
        self.total_processed = 0
        self.total_stored = 0
        self.total_failed = 0
        
        # Step 1: Pre-filter and prepare messages
        valid_messages = []
        for msg_data in messages:
            message_text = msg_data.get("content", "")
            username = msg_data.get("username", "unknown")
            message_type = msg_data.get("type", "")
            
            # Skip invalid messages
            if not message_text or not message_text.strip():
                self.total_failed += 1
                continue
            
            if message_type in ["system", "error", "support_response", "instant_answer"]:
                self.total_failed += 1
                continue
            
            valid_messages.append(msg_data)
        
        logger.info(f"Filtered to {len(valid_messages)} valid messages")
        
        if not valid_messages:
            return {
                "processed": 0,
                "stored": 0,
                "failed": self.total_failed
            }
        
        # Step 2: Classify and tag all messages
        logger.info("Classifying and tagging messages...")
        classifications = []
        tags_list = []
        
        for msg_data in valid_messages:
            message_text = msg_data.get("content", "")
            
            # Classify
            classification = await self._classify_safe(message_text)
            classifications.append(classification)
            
            # Tag
            tags = await self._tag_safe(message_text)
            tags_list.append(tags)
            
            self.total_processed += 1
            
            if self.total_processed % 10 == 0:
                logger.info(f"Classified {self.total_processed}/{len(valid_messages)}")
        
        # Step 3: Generate embeddings in parallel batches
        logger.info("Generating embeddings in parallel...")
        texts = [msg.get("content", "") for msg in valid_messages]
        embeddings = await self._embed_texts_parallel(texts)
        
        # Step 4: Prepare data for bulk insert
        logger.info("Preparing bulk insert data...")
        ids = []
        documents = []
        embeddings_list = []
        metadatas = []
        
        for i, msg_data in enumerate(valid_messages):
            message_text = msg_data.get("content", "")
            username = msg_data.get("username", "unknown")
            timestamp_str = msg_data.get("timestamp")
            
            # Parse timestamp
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.utcnow()
            except (ValueError, TypeError):
                timestamp = datetime.utcnow()
            
            # Generate message ID
            message_id = f"msg_{timestamp.timestamp()}_{username}_{i}"
            
            # Prepare metadata
            classification = classifications[i]
            tags = tags_list[i]
            
            metadata = {
                "username": username,
                "user_id": 0,  # Historical messages don't have user_id
                "room": room_name,
                "timestamp": timestamp.isoformat(),
                "message_type": classification.message_type.value,
                "topic_tags": ",".join(tags.topic_tags) if tags.topic_tags else "",
                "tech_keywords": ",".join(tags.tech_keywords) if tags.tech_keywords else "",
                "contains_code": tags.contains_code,
                "code_language": tags.code_language if tags.code_language else ""
            }
            
            ids.append(message_id)
            documents.append(message_text)
            embeddings_list.append(embeddings[i])
            metadatas.append(metadata)
        
        # Step 5: Bulk insert into ChromaDB
        logger.info(f"Bulk inserting {len(ids)} messages into ChromaDB...")
        collection = self.instant_answer_service.storage_service.chroma_collection
        
        for i in range(0, len(ids), self.chromadb_batch_size):
            batch_ids = ids[i:i + self.chromadb_batch_size]
            batch_docs = documents[i:i + self.chromadb_batch_size]
            batch_embeddings = embeddings_list[i:i + self.chromadb_batch_size]
            batch_metadatas = metadatas[i:i + self.chromadb_batch_size]
            
            try:
                await asyncio.to_thread(
                    collection.add,
                    ids=batch_ids,
                    documents=batch_docs,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                self.total_stored += len(batch_ids)
                logger.info(f"Inserted batch: {self.total_stored}/{len(ids)}")
            
            except Exception as e:
                logger.error(f"Failed to insert batch: {e}")
                self.total_failed += len(batch_ids)
        
        logger.info(
            f"FAST indexing complete for room '{room_name}': "
            f"{self.total_stored}/{self.total_processed} messages stored successfully"
        )
        
        return {
            "processed": self.total_processed,
            "stored": self.total_stored,
            "failed": self.total_failed
        }
    
    async def _embed_texts_parallel(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using parallel batch processing.
        
        This uses ThreadPoolExecutor to process multiple batches in parallel,
        significantly speeding up embedding generation for large datasets.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        
        Requirements: 6.1
        """
        import google.generativeai as genai
        
        embeddings = []
        
        def embed_batch(batch):
            """Embed a batch of texts (runs in thread pool)."""
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=batch,
                    task_type="retrieval_document"
                )
                return result["embedding"]
            except Exception as e:
                logger.error(f"Embedding batch failed: {e}")
                # Return zero vectors as fallback
                return [[0.0] * 768 for _ in batch]
        
        # Create batches
        batches = [
            texts[i:i + self.embedding_batch_size]
            for i in range(0, len(texts), self.embedding_batch_size)
        ]
        
        logger.info(f"Processing {len(batches)} embedding batches in parallel...")
        
        # Process batches in parallel using ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            futures = [
                loop.run_in_executor(executor, embed_batch, batch)
                for batch in batches
            ]
            
            # Wait for all to complete
            results = await asyncio.gather(*futures)
        
        # Flatten results
        for batch_emb in results:
            embeddings.extend(batch_emb)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        return embeddings
    
    async def _classify_safe(self, message: str) -> MessageClassification:
        """Classify message with error handling."""
        try:
            return await self.instant_answer_service.classifier.classify(message)
        except Exception as e:
            logger.warning(f"Classification failed: {e}")
            return MessageClassification(
                message_type=MessageType.DISCUSSION,
                confidence=0.5,
                contains_code=False,
                reasoning="Classification failed"
            )
    
    async def _tag_safe(self, message: str) -> MessageTags:
        """Tag message with error handling."""
        try:
            return await self.instant_answer_service.tagger.tag_message(message)
        except Exception as e:
            logger.warning(f"Tagging failed: {e}")
            return MessageTags(
                topic_tags=[],
                tech_keywords=[],
                contains_code=False,
                code_language=None
            )


async def fast_index_historical_messages(
    instant_answer_service,
    room_service,
    target_room: str = "Techline",
    embedding_batch_size: int = 12,
    max_workers: int = 10
) -> Dict[str, int]:
    """
    Fast index all historical messages from a specific room.
    
    This uses parallel batch embedding and bulk ChromaDB inserts for
    significantly faster indexing of large message histories.
    
    Args:
        instant_answer_service: InstantAnswerService instance
        room_service: RoomService instance to get room history
        target_room: Name of room to index (default: Techline)
        embedding_batch_size: Texts per embedding API call
        max_workers: Parallel workers for embedding
    
    Returns:
        Dict with statistics: processed, stored, failed counts
    
    Requirements: 6.1, 6.2, 6.3
    """
    logger.info(f"Starting FAST historical indexing for room: {target_room}")
    
    # Get the room
    room = room_service.get_room(target_room)
    if not room:
        logger.error(f"Room '{target_room}' not found")
        return {"processed": 0, "stored": 0, "failed": 0}
    
    # Get all messages from room history
    messages = room.get_recent_messages(limit=10000)  # Get up to 10k messages
    
    if not messages:
        logger.info(f"No messages found in room '{target_room}'")
        return {"processed": 0, "stored": 0, "failed": 0}
    
    # Create fast indexer and process messages
    indexer = FastMessageIndexer(
        instant_answer_service=instant_answer_service,
        embedding_batch_size=embedding_batch_size,
        max_workers=max_workers
    )
    
    stats = await indexer.index_room_messages_fast(target_room, messages)
    
    logger.info(
        f"FAST historical indexing complete: "
        f"{stats['stored']}/{stats['processed']} messages indexed"
    )
    
    return stats
