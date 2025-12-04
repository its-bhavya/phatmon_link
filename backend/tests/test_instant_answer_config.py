"""
Tests for Instant Answer configuration.

Requirements: 9.1, 9.5
"""

import os
import pytest
from backend.config import Config, ConfigurationError
from backend.instant_answer.config import InstantAnswerConfig


class TestInstantAnswerConfig:
    """Test suite for instant answer configuration."""
    
    def test_default_configuration(self):
        """Test that default instant answer configuration loads correctly."""
        # Set minimal required env vars
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        
        config = Config()
        instant_config = InstantAnswerConfig.from_app_config(config)
        
        # Verify defaults
        assert instant_config.enabled is True
        assert instant_config.target_room == "Techline"
        assert instant_config.min_similarity_threshold == 0.7
        assert instant_config.max_search_results == 5
        assert instant_config.classification_confidence_threshold == 0.6
        assert instant_config.max_summary_tokens == 300
        assert instant_config.chroma_collection_name == "techline_messages"
        assert instant_config.chroma_host == "localhost"
        assert instant_config.chroma_port == 8001
        assert instant_config.embedding_model == "models/embedding-001"
    
    def test_custom_configuration(self):
        """Test that custom instant answer configuration loads correctly."""
        # Set custom env vars
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        os.environ["INSTANT_ANSWER_ENABLED"] = "false"
        os.environ["INSTANT_ANSWER_MIN_SIMILARITY"] = "0.8"
        os.environ["INSTANT_ANSWER_MAX_RESULTS"] = "10"
        os.environ["INSTANT_ANSWER_CONFIDENCE_THRESHOLD"] = "0.7"
        os.environ["INSTANT_ANSWER_MAX_SUMMARY_TOKENS"] = "500"
        os.environ["CHROMADB_HOST"] = "remote-host"
        os.environ["CHROMADB_PORT"] = "9000"
        os.environ["CHROMADB_COLLECTION_NAME"] = "custom_collection"
        os.environ["INSTANT_ANSWER_TARGET_ROOM"] = "CustomRoom"
        
        config = Config()
        instant_config = InstantAnswerConfig.from_app_config(config)
        
        # Verify custom values
        assert instant_config.enabled is False
        assert instant_config.target_room == "CustomRoom"
        assert instant_config.min_similarity_threshold == 0.8
        assert instant_config.max_search_results == 10
        assert instant_config.classification_confidence_threshold == 0.7
        assert instant_config.max_summary_tokens == 500
        assert instant_config.chroma_collection_name == "custom_collection"
        assert instant_config.chroma_host == "remote-host"
        assert instant_config.chroma_port == 9000
        
        # Clean up
        del os.environ["INSTANT_ANSWER_ENABLED"]
        del os.environ["INSTANT_ANSWER_MIN_SIMILARITY"]
        del os.environ["INSTANT_ANSWER_MAX_RESULTS"]
        del os.environ["INSTANT_ANSWER_CONFIDENCE_THRESHOLD"]
        del os.environ["INSTANT_ANSWER_MAX_SUMMARY_TOKENS"]
        del os.environ["CHROMADB_HOST"]
        del os.environ["CHROMADB_PORT"]
        del os.environ["CHROMADB_COLLECTION_NAME"]
        del os.environ["INSTANT_ANSWER_TARGET_ROOM"]
    
    def test_invalid_similarity_threshold(self):
        """Test that invalid similarity threshold raises error."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        os.environ["INSTANT_ANSWER_MIN_SIMILARITY"] = "1.5"
        
        with pytest.raises(ConfigurationError) as exc_info:
            Config()
        
        assert "INSTANT_ANSWER_MIN_SIMILARITY must be between 0.0 and 1.0" in str(exc_info.value)
        
        # Clean up
        del os.environ["INSTANT_ANSWER_MIN_SIMILARITY"]
    
    def test_invalid_max_results(self):
        """Test that invalid max results raises error."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        os.environ["INSTANT_ANSWER_MAX_RESULTS"] = "-1"
        
        with pytest.raises(ConfigurationError) as exc_info:
            Config()
        
        assert "INSTANT_ANSWER_MAX_RESULTS must be positive" in str(exc_info.value)
        
        # Clean up
        del os.environ["INSTANT_ANSWER_MAX_RESULTS"]
    
    def test_invalid_confidence_threshold(self):
        """Test that invalid confidence threshold raises error."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        os.environ["INSTANT_ANSWER_CONFIDENCE_THRESHOLD"] = "2.0"
        
        with pytest.raises(ConfigurationError) as exc_info:
            Config()
        
        assert "INSTANT_ANSWER_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0" in str(exc_info.value)
        
        # Clean up
        del os.environ["INSTANT_ANSWER_CONFIDENCE_THRESHOLD"]
    
    def test_invalid_chromadb_port(self):
        """Test that invalid ChromaDB port raises error."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        os.environ["CHROMADB_PORT"] = "70000"
        
        with pytest.raises(ConfigurationError) as exc_info:
            Config()
        
        assert "CHROMADB_PORT must be between 1 and 65535" in str(exc_info.value)
        
        # Clean up
        del os.environ["CHROMADB_PORT"]
    
    def test_config_repr(self):
        """Test that configuration repr works correctly."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
        os.environ["GEMINI_API_KEY"] = "test-api-key"
        
        config = Config()
        instant_config = InstantAnswerConfig.from_app_config(config)
        
        repr_str = repr(instant_config)
        
        # Verify key fields are in repr
        assert "enabled=True" in repr_str
        assert "target_room=Techline" in repr_str
        assert "min_similarity_threshold=0.7" in repr_str
        assert "chroma_collection_name=techline_messages" in repr_str
