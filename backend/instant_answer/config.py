"""
Configuration for Instant Answer Recall System.

This module provides configuration management for the instant answer system,
loading settings from the main application config.

Requirements: 9.1, 9.5
"""

from dataclasses import dataclass
from backend.config import Config


@dataclass
class InstantAnswerConfig:
    """
    Configuration for instant answer system.
    
    This class encapsulates all configuration settings for the instant answer
    recall system, including search thresholds, ChromaDB connection details,
    and feature flags.
    
    Attributes:
        enabled: Whether the instant answer system is enabled
        target_room: The room where instant answers are active (e.g., "Techline")
        min_similarity_threshold: Minimum similarity score for search results (0.0-1.0)
        max_search_results: Maximum number of search results to return
        classification_confidence_threshold: Minimum confidence for message classification (0.0-1.0)
        max_summary_tokens: Maximum tokens for AI-generated summaries
        chroma_collection_name: Name of the ChromaDB collection
        chroma_host: ChromaDB server host
        chroma_port: ChromaDB server port
        embedding_model: Gemini embedding model name
    """
    
    enabled: bool = True
    target_room: str = "Techline"
    min_similarity_threshold: float = 0.7
    max_search_results: int = 5
    classification_confidence_threshold: float = 0.6
    max_summary_tokens: int = 300
    chroma_collection_name: str = "techline_messages"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    embedding_model: str = "models/embedding-001"
    
    @classmethod
    def from_app_config(cls, app_config: Config) -> "InstantAnswerConfig":
        """
        Create InstantAnswerConfig from application Config.
        
        Args:
            app_config: Main application configuration
            
        Returns:
            InstantAnswerConfig instance with values from app config
        """
        return cls(
            enabled=app_config.INSTANT_ANSWER_ENABLED,
            target_room=app_config.INSTANT_ANSWER_TARGET_ROOM,
            min_similarity_threshold=app_config.INSTANT_ANSWER_MIN_SIMILARITY,
            max_search_results=app_config.INSTANT_ANSWER_MAX_RESULTS,
            classification_confidence_threshold=app_config.INSTANT_ANSWER_CONFIDENCE_THRESHOLD,
            max_summary_tokens=app_config.INSTANT_ANSWER_MAX_SUMMARY_TOKENS,
            chroma_collection_name=app_config.CHROMADB_COLLECTION_NAME,
            chroma_host=app_config.CHROMADB_HOST,
            chroma_port=app_config.CHROMADB_PORT,
            embedding_model="models/embedding-001"  # Gemini embedding model
        )
    
    def __repr__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"InstantAnswerConfig(\n"
            f"  enabled={self.enabled}\n"
            f"  target_room={self.target_room}\n"
            f"  min_similarity_threshold={self.min_similarity_threshold}\n"
            f"  max_search_results={self.max_search_results}\n"
            f"  classification_confidence_threshold={self.classification_confidence_threshold}\n"
            f"  max_summary_tokens={self.max_summary_tokens}\n"
            f"  chroma_collection_name={self.chroma_collection_name}\n"
            f"  chroma_host={self.chroma_host}\n"
            f"  chroma_port={self.chroma_port}\n"
            f"  embedding_model={self.embedding_model}\n"
            f")"
        )
