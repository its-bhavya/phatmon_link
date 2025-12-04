"""
Configuration management for Phantom Link BBS.

This module loads and validates environment variables with sensible defaults
for development. All configuration is centralized here for easy management.

Requirements: All (infrastructure)
"""

import os
from typing import List
from pathlib import Path


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """
    Application configuration loaded from environment variables.
    
    This class provides centralized configuration management with:
    - Environment variable loading
    - Sensible defaults for development
    - Validation for required settings
    - Type conversion and parsing
    """
    
    # Database Configuration
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_HOURS: int
    
    # CORS Configuration
    CORS_ORIGINS: List[str]
    
    # Server Configuration
    HOST: str
    PORT: int
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    GEMINI_TEMPERATURE: float
    GEMINI_MAX_TOKENS: int
    
    # Profile Tracking Configuration
    PROFILE_RETENTION_DAYS: int
    PROFILE_CACHE_TTL_SECONDS: int
    
    # Support Bot Configuration
    SUPPORT_BOT_ENABLED: bool
    SUPPORT_SENTIMENT_THRESHOLD: float
    SUPPORT_CRISIS_DETECTION_ENABLED: bool
    
    # Instant Answer Recall Configuration
    INSTANT_ANSWER_ENABLED: bool
    INSTANT_ANSWER_MIN_SIMILARITY: float
    INSTANT_ANSWER_MAX_RESULTS: int
    INSTANT_ANSWER_CONFIDENCE_THRESHOLD: float
    INSTANT_ANSWER_MAX_SUMMARY_TOKENS: int
    CHROMADB_HOST: str
    CHROMADB_PORT: int
    CHROMADB_COLLECTION_NAME: str
    INSTANT_ANSWER_TARGET_ROOM: str
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from environment variables with defaults."""
        
        # Database Configuration
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "sqlite:///./phantom_link.db"
        )
        
        # JWT Configuration
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        
        # Parse JWT expiration hours with default
        jwt_expiration_str = os.getenv("JWT_EXPIRATION_HOURS", "1")
        try:
            self.JWT_EXPIRATION_HOURS = int(jwt_expiration_str)
        except ValueError:
            raise ConfigurationError(
                f"JWT_EXPIRATION_HOURS must be an integer, got: {jwt_expiration_str}"
            )
        
        # CORS Configuration
        cors_origins_str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:8000"
        )
        # Parse comma-separated list and strip whitespace
        self.CORS_ORIGINS = [
            origin.strip()
            for origin in cors_origins_str.split(",")
            if origin.strip()
        ]
        
        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        
        # Parse port with default
        port_str = os.getenv("PORT", "8000")
        try:
            self.PORT = int(port_str)
        except ValueError:
            raise ConfigurationError(
                f"PORT must be an integer, got: {port_str}"
            )
        
        # Gemini AI Configuration
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        # Parse Gemini temperature
        gemini_temp_str = os.getenv("GEMINI_TEMPERATURE", "0.9")
        try:
            self.GEMINI_TEMPERATURE = float(gemini_temp_str)
        except ValueError:
            raise ConfigurationError(
                f"GEMINI_TEMPERATURE must be a float, got: {gemini_temp_str}"
            )
        
        # Parse Gemini max tokens
        gemini_tokens_str = os.getenv("GEMINI_MAX_TOKENS", "500")
        try:
            self.GEMINI_MAX_TOKENS = int(gemini_tokens_str)
        except ValueError:
            raise ConfigurationError(
                f"GEMINI_MAX_TOKENS must be an integer, got: {gemini_tokens_str}"
            )
        
        # Profile Tracking Configuration
        profile_retention_str = os.getenv("PROFILE_RETENTION_DAYS", "30")
        try:
            self.PROFILE_RETENTION_DAYS = int(profile_retention_str)
        except ValueError:
            raise ConfigurationError(
                f"PROFILE_RETENTION_DAYS must be an integer, got: {profile_retention_str}"
            )
        
        profile_cache_str = os.getenv("PROFILE_CACHE_TTL_SECONDS", "300")
        try:
            self.PROFILE_CACHE_TTL_SECONDS = int(profile_cache_str)
        except ValueError:
            raise ConfigurationError(
                f"PROFILE_CACHE_TTL_SECONDS must be an integer, got: {profile_cache_str}"
            )
        
        # Support Bot Configuration
        support_enabled_str = os.getenv("SUPPORT_BOT_ENABLED", "true")
        self.SUPPORT_BOT_ENABLED = support_enabled_str.lower() in ("true", "1", "yes")
        
        # Parse Support sentiment threshold
        support_threshold_str = os.getenv("SUPPORT_SENTIMENT_THRESHOLD", "0.6")
        try:
            self.SUPPORT_SENTIMENT_THRESHOLD = float(support_threshold_str)
        except ValueError:
            raise ConfigurationError(
                f"SUPPORT_SENTIMENT_THRESHOLD must be a float, got: {support_threshold_str}"
            )
        
        # Parse Support crisis detection enabled
        crisis_enabled_str = os.getenv("SUPPORT_CRISIS_DETECTION_ENABLED", "true")
        self.SUPPORT_CRISIS_DETECTION_ENABLED = crisis_enabled_str.lower() in ("true", "1", "yes")
        
        # Instant Answer Recall Configuration
        instant_answer_enabled_str = os.getenv("INSTANT_ANSWER_ENABLED", "true")
        self.INSTANT_ANSWER_ENABLED = instant_answer_enabled_str.lower() in ("true", "1", "yes")
        
        # Parse Instant Answer minimum similarity threshold
        instant_answer_similarity_str = os.getenv("INSTANT_ANSWER_MIN_SIMILARITY", "0.7")
        try:
            self.INSTANT_ANSWER_MIN_SIMILARITY = float(instant_answer_similarity_str)
        except ValueError:
            raise ConfigurationError(
                f"INSTANT_ANSWER_MIN_SIMILARITY must be a float, got: {instant_answer_similarity_str}"
            )
        
        # Parse Instant Answer max results
        instant_answer_max_results_str = os.getenv("INSTANT_ANSWER_MAX_RESULTS", "5")
        try:
            self.INSTANT_ANSWER_MAX_RESULTS = int(instant_answer_max_results_str)
        except ValueError:
            raise ConfigurationError(
                f"INSTANT_ANSWER_MAX_RESULTS must be an integer, got: {instant_answer_max_results_str}"
            )
        
        # Parse Instant Answer confidence threshold
        instant_answer_confidence_str = os.getenv("INSTANT_ANSWER_CONFIDENCE_THRESHOLD", "0.6")
        try:
            self.INSTANT_ANSWER_CONFIDENCE_THRESHOLD = float(instant_answer_confidence_str)
        except ValueError:
            raise ConfigurationError(
                f"INSTANT_ANSWER_CONFIDENCE_THRESHOLD must be a float, got: {instant_answer_confidence_str}"
            )
        
        # Parse Instant Answer max summary tokens
        instant_answer_max_tokens_str = os.getenv("INSTANT_ANSWER_MAX_SUMMARY_TOKENS", "300")
        try:
            self.INSTANT_ANSWER_MAX_SUMMARY_TOKENS = int(instant_answer_max_tokens_str)
        except ValueError:
            raise ConfigurationError(
                f"INSTANT_ANSWER_MAX_SUMMARY_TOKENS must be an integer, got: {instant_answer_max_tokens_str}"
            )
        
        # ChromaDB Configuration
        self.CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
        
        # Parse ChromaDB port
        chromadb_port_str = os.getenv("CHROMADB_PORT", "8001")
        try:
            self.CHROMADB_PORT = int(chromadb_port_str)
        except ValueError:
            raise ConfigurationError(
                f"CHROMADB_PORT must be an integer, got: {chromadb_port_str}"
            )
        
        self.CHROMADB_COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "techline_messages")
        self.INSTANT_ANSWER_TARGET_ROOM = os.getenv("INSTANT_ANSWER_TARGET_ROOM", "Techline")
    
    def _validate_config(self):
        """
        Validate required configuration values.
        
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        errors = []
        
        # Validate JWT_SECRET_KEY
        if not self.JWT_SECRET_KEY:
            # In development, generate a warning but provide a default
            # In production, this should be required
            if self._is_production():
                errors.append(
                    "JWT_SECRET_KEY is required in production. "
                    "Set the JWT_SECRET_KEY environment variable."
                )
            else:
                # Use a development default but warn
                self.JWT_SECRET_KEY = "dev-secret-key-change-in-production"
                print(
                    "WARNING: JWT_SECRET_KEY not set. Using development default. "
                    "DO NOT use this in production!"
                )
        
        # Validate JWT_SECRET_KEY length (should be reasonably long)
        if len(self.JWT_SECRET_KEY) < 16:
            if self._is_production():
                errors.append(
                    "JWT_SECRET_KEY must be at least 16 characters long for security."
                )
            else:
                print(
                    "WARNING: JWT_SECRET_KEY is short. "
                    "Use a longer key in production (at least 16 characters)."
                )
        
        # Validate JWT_ALGORITHM
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if self.JWT_ALGORITHM not in valid_algorithms:
            errors.append(
                f"JWT_ALGORITHM must be one of {valid_algorithms}, "
                f"got: {self.JWT_ALGORITHM}"
            )
        
        # Validate JWT_EXPIRATION_HOURS
        if self.JWT_EXPIRATION_HOURS <= 0:
            errors.append(
                f"JWT_EXPIRATION_HOURS must be positive, got: {self.JWT_EXPIRATION_HOURS}"
            )
        
        # Validate CORS_ORIGINS
        if not self.CORS_ORIGINS:
            errors.append(
                "CORS_ORIGINS must contain at least one origin. "
                "Set the CORS_ORIGINS environment variable."
            )
        
        # Validate PORT range
        if not (1 <= self.PORT <= 65535):
            errors.append(
                f"PORT must be between 1 and 65535, got: {self.PORT}"
            )
        
        # Validate DATABASE_URL format
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL cannot be empty.")
        
        # Validate Gemini configuration
        # Validate Gemini temperature range
        if not (0.0 <= self.GEMINI_TEMPERATURE <= 2.0):
            errors.append(
                f"GEMINI_TEMPERATURE must be between 0.0 and 2.0, got: {self.GEMINI_TEMPERATURE}"
            )
        
        # Validate Gemini max tokens
        if self.GEMINI_MAX_TOKENS <= 0:
            errors.append(
                f"GEMINI_MAX_TOKENS must be positive, got: {self.GEMINI_MAX_TOKENS}"
            )
        
        # Validate profile tracking configuration
        if self.PROFILE_RETENTION_DAYS <= 0:
            errors.append(
                f"PROFILE_RETENTION_DAYS must be positive, got: {self.PROFILE_RETENTION_DAYS}"
            )
        
        if self.PROFILE_CACHE_TTL_SECONDS < 0:
            errors.append(
                f"PROFILE_CACHE_TTL_SECONDS must be non-negative, got: {self.PROFILE_CACHE_TTL_SECONDS}"
            )
        
        # Validate Support Bot configuration
        if not (0.0 <= self.SUPPORT_SENTIMENT_THRESHOLD <= 1.0):
            errors.append(
                f"SUPPORT_SENTIMENT_THRESHOLD must be between 0.0 and 1.0, got: {self.SUPPORT_SENTIMENT_THRESHOLD}"
            )
        
        # Validate Instant Answer Recall configuration
        if not (0.0 <= self.INSTANT_ANSWER_MIN_SIMILARITY <= 1.0):
            errors.append(
                f"INSTANT_ANSWER_MIN_SIMILARITY must be between 0.0 and 1.0, got: {self.INSTANT_ANSWER_MIN_SIMILARITY}"
            )
        
        if self.INSTANT_ANSWER_MAX_RESULTS <= 0:
            errors.append(
                f"INSTANT_ANSWER_MAX_RESULTS must be positive, got: {self.INSTANT_ANSWER_MAX_RESULTS}"
            )
        
        if not (0.0 <= self.INSTANT_ANSWER_CONFIDENCE_THRESHOLD <= 1.0):
            errors.append(
                f"INSTANT_ANSWER_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0, got: {self.INSTANT_ANSWER_CONFIDENCE_THRESHOLD}"
            )
        
        if self.INSTANT_ANSWER_MAX_SUMMARY_TOKENS <= 0:
            errors.append(
                f"INSTANT_ANSWER_MAX_SUMMARY_TOKENS must be positive, got: {self.INSTANT_ANSWER_MAX_SUMMARY_TOKENS}"
            )
        
        if not (1 <= self.CHROMADB_PORT <= 65535):
            errors.append(
                f"CHROMADB_PORT must be between 1 and 65535, got: {self.CHROMADB_PORT}"
            )
        
        if not self.CHROMADB_COLLECTION_NAME:
            errors.append("CHROMADB_COLLECTION_NAME cannot be empty.")
        
        if not self.INSTANT_ANSWER_TARGET_ROOM:
            errors.append("INSTANT_ANSWER_TARGET_ROOM cannot be empty.")
        
        # If there are validation errors, raise exception
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ConfigurationError(error_message)
    
    def _is_production(self) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            True if in production, False otherwise
        """
        env = os.getenv("ENVIRONMENT", "development").lower()
        return env in ("production", "prod")
    
    def __repr__(self) -> str:
        """Return string representation of configuration (without secrets)."""
        return (
            f"Config(\n"
            f"  DATABASE_URL={self.DATABASE_URL}\n"
            f"  JWT_ALGORITHM={self.JWT_ALGORITHM}\n"
            f"  JWT_EXPIRATION_HOURS={self.JWT_EXPIRATION_HOURS}\n"
            f"  CORS_ORIGINS={self.CORS_ORIGINS}\n"
            f"  HOST={self.HOST}\n"
            f"  PORT={self.PORT}\n"
            f"  JWT_SECRET_KEY={'***' if self.JWT_SECRET_KEY else 'NOT SET'}\n"
            f")"
        )


# Global configuration instance
# This is loaded once when the module is imported
_config: Config = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config instance with loaded and validated configuration
    
    Raises:
        ConfigurationError: If configuration is invalid
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """
    Reload configuration from environment variables.
    
    Useful for testing or when environment variables change.
    
    Returns:
        New Config instance with reloaded configuration
    """
    global _config
    _config = Config()
    return _config


# Convenience function to load config at module import
# This ensures configuration errors are caught early
try:
    _config = Config()
except ConfigurationError as e:
    # Re-raise to make configuration errors visible at startup
    raise
