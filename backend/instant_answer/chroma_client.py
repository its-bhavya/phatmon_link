"""
ChromaDB client initialization and management.

This module provides functions to initialize and manage the ChromaDB client
and collection for the instant answer system.

Requirements: 6.1, 6.2, 9.1
"""

import chromadb
from chromadb.config import Settings
from typing import Optional
import logging

from backend.instant_answer.config import InstantAnswerConfig

logger = logging.getLogger(__name__)


def init_chromadb_client(config: InstantAnswerConfig) -> Optional[chromadb.Client]:
    """
    Initialize ChromaDB client.
    
    Creates a ChromaDB client connection using the configuration settings.
    Uses in-memory mode for development if connection fails.
    
    Args:
        config: Instant answer configuration
        
    Returns:
        ChromaDB client instance, or None if initialization fails
        
    Requirements: 6.1, 9.1
    """
    try:
        # Try to connect to ChromaDB server
        client = chromadb.HttpClient(
            host=config.chroma_host,
            port=config.chroma_port,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Test connection
        client.heartbeat()
        
        logger.info(f"ChromaDB client initialized: {config.chroma_host}:{config.chroma_port}")
        return client
        
    except Exception as e:
        logger.warning(f"Failed to connect to ChromaDB server: {e}")
        logger.info("Falling back to in-memory ChromaDB client")
        
        try:
            # Fall back to in-memory client for development
            client = chromadb.Client(
                Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("In-memory ChromaDB client initialized")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            return None


def init_chromadb_collection(
    client: chromadb.Client,
    config: InstantAnswerConfig
) -> Optional[chromadb.Collection]:
    """
    Initialize or get ChromaDB collection.
    
    Creates the collection if it doesn't exist, or retrieves it if it does.
    The collection stores message embeddings with metadata for semantic search.
    
    Args:
        client: ChromaDB client instance
        config: Instant answer configuration
        
    Returns:
        ChromaDB collection instance, or None if initialization fails
        
    Requirements: 6.2
    """
    try:
        # Get or create collection
        collection = client.get_or_create_collection(
            name=config.chroma_collection_name,
            metadata={
                "description": "Techline room messages with embeddings for instant answer recall",
                "hnsw:space": "cosine"  # Use cosine similarity for semantic search
            }
        )
        
        logger.info(f"ChromaDB collection initialized: {config.chroma_collection_name}")
        logger.info(f"Collection contains {collection.count()} documents")
        
        return collection
        
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB collection: {e}")
        return None


def close_chromadb_client(client: Optional[chromadb.Client]) -> None:
    """
    Close ChromaDB client connection.
    
    Performs cleanup when shutting down the application.
    
    Args:
        client: ChromaDB client instance to close
    """
    if client:
        try:
            # ChromaDB client doesn't have explicit close method
            # Just log the shutdown
            logger.info("ChromaDB client connection closed")
        except Exception as e:
            logger.error(f"Error closing ChromaDB client: {e}")
