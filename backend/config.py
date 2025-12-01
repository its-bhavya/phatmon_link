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
