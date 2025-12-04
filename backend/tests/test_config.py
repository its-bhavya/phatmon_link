"""
Tests for configuration management.

This module tests the Config class to ensure:
- Environment variables are loaded correctly
- Defaults are applied when variables are not set
- Validation catches invalid configuration
- Type conversion works properly
"""

import os
import pytest
from backend.config import Config, ConfigurationError, get_config, reload_config


class TestConfig:
    """Test suite for configuration management."""
    
    def test_default_configuration(self):
        """Test that default configuration values are set correctly."""
        # Clear environment variables
        env_vars = [
            "DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM",
            "JWT_EXPIRATION_HOURS", "CORS_ORIGINS", "HOST", "PORT"
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            config = Config()
            
            # Check defaults
            assert config.DATABASE_URL == "sqlite:///./phantom_link.db"
            assert config.JWT_ALGORITHM == "HS256"
            assert config.JWT_EXPIRATION_HOURS == 1
            assert "http://localhost:3000" in config.CORS_ORIGINS
            assert "http://localhost:8000" in config.CORS_ORIGINS
            assert config.HOST == "0.0.0.0"
            assert config.PORT == 8000
            
            # JWT_SECRET_KEY should have a development default
            assert config.JWT_SECRET_KEY == "dev-secret-key-change-in-production"
        
        finally:
            # Restore environment variables
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
    
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        # Set environment variables
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        os.environ["JWT_ALGORITHM"] = "HS384"
        os.environ["JWT_EXPIRATION_HOURS"] = "2"
        os.environ["CORS_ORIGINS"] = "http://example.com,http://test.com"
        os.environ["HOST"] = "127.0.0.1"
        os.environ["PORT"] = "9000"
        
        try:
            config = Config()
            
            assert config.DATABASE_URL == "sqlite:///./test.db"
            assert config.JWT_SECRET_KEY == "test-secret-key-1234567890"
            assert config.JWT_ALGORITHM == "HS384"
            assert config.JWT_EXPIRATION_HOURS == 2
            assert config.CORS_ORIGINS == ["http://example.com", "http://test.com"]
            assert config.HOST == "127.0.0.1"
            assert config.PORT == 9000
        
        finally:
            # Clean up
            for var in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM",
                       "JWT_EXPIRATION_HOURS", "CORS_ORIGINS", "HOST", "PORT"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_invalid_jwt_expiration_hours(self):
        """Test that invalid JWT_EXPIRATION_HOURS raises error."""
        os.environ["JWT_EXPIRATION_HOURS"] = "invalid"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "JWT_EXPIRATION_HOURS must be an integer" in str(exc_info.value)
        
        finally:
            if "JWT_EXPIRATION_HOURS" in os.environ:
                del os.environ["JWT_EXPIRATION_HOURS"]
    
    def test_invalid_port(self):
        """Test that invalid PORT raises error."""
        os.environ["PORT"] = "not-a-number"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PORT must be an integer" in str(exc_info.value)
        
        finally:
            if "PORT" in os.environ:
                del os.environ["PORT"]
    
    def test_port_out_of_range(self):
        """Test that PORT outside valid range raises error."""
        os.environ["PORT"] = "70000"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PORT must be between 1 and 65535" in str(exc_info.value)
        
        finally:
            for var in ["PORT", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_negative_jwt_expiration(self):
        """Test that negative JWT_EXPIRATION_HOURS raises error."""
        os.environ["JWT_EXPIRATION_HOURS"] = "-1"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "JWT_EXPIRATION_HOURS must be positive" in str(exc_info.value)
        
        finally:
            for var in ["JWT_EXPIRATION_HOURS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_invalid_jwt_algorithm(self):
        """Test that invalid JWT_ALGORITHM raises error."""
        os.environ["JWT_ALGORITHM"] = "INVALID"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "JWT_ALGORITHM must be one of" in str(exc_info.value)
        
        finally:
            for var in ["JWT_ALGORITHM", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_cors_origins_parsing(self):
        """Test that CORS_ORIGINS are parsed correctly."""
        os.environ["CORS_ORIGINS"] = "http://a.com, http://b.com , http://c.com"
        
        try:
            config = Config()
            
            # Should strip whitespace
            assert config.CORS_ORIGINS == ["http://a.com", "http://b.com", "http://c.com"]
        
        finally:
            if "CORS_ORIGINS" in os.environ:
                del os.environ["CORS_ORIGINS"]
    
    def test_config_repr(self):
        """Test that config __repr__ doesn't expose secrets."""
        os.environ["JWT_SECRET_KEY"] = "super-secret-key-1234567890"
        
        try:
            config = Config()
            repr_str = repr(config)
            
            # Should not contain the actual secret
            assert "super-secret-key-1234567890" not in repr_str
            # Should indicate secret is set
            assert "***" in repr_str or "NOT SET" in repr_str
        
        finally:
            if "JWT_SECRET_KEY" in os.environ:
                del os.environ["JWT_SECRET_KEY"]
    
    def test_gemini_configuration_defaults(self):
        """Test that Gemini configuration defaults are set correctly."""
        config = Config()
        
        assert config.GEMINI_MODEL == "gemini-2.0-flash"
        assert config.GEMINI_TEMPERATURE == 0.9
        assert config.GEMINI_MAX_TOKENS == 500
    
    def test_invalid_gemini_temperature(self):
        """Test that invalid GEMINI_TEMPERATURE raises error."""
        os.environ["GEMINI_TEMPERATURE"] = "not-a-float"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "GEMINI_TEMPERATURE must be a float" in str(exc_info.value)
        
        finally:
            for var in ["GEMINI_TEMPERATURE", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_gemini_temperature_out_of_range(self):
        """Test that GEMINI_TEMPERATURE outside valid range raises error."""
        os.environ["GEMINI_TEMPERATURE"] = "3.0"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "GEMINI_TEMPERATURE must be between 0.0 and 2.0" in str(exc_info.value)
        
        finally:
            for var in ["GEMINI_TEMPERATURE", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_invalid_gemini_max_tokens(self):
        """Test that invalid GEMINI_MAX_TOKENS raises error."""
        os.environ["GEMINI_MAX_TOKENS"] = "not-an-int"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "GEMINI_MAX_TOKENS must be an integer" in str(exc_info.value)
        
        finally:
            for var in ["GEMINI_MAX_TOKENS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_negative_gemini_max_tokens(self):
        """Test that negative GEMINI_MAX_TOKENS raises error."""
        os.environ["GEMINI_MAX_TOKENS"] = "-1"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "GEMINI_MAX_TOKENS must be positive" in str(exc_info.value)
        
        finally:
            for var in ["GEMINI_MAX_TOKENS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_profile_tracking_defaults(self):
        """Test that profile tracking configuration defaults are set correctly."""
        config = Config()
        
        assert config.PROFILE_RETENTION_DAYS == 30
        assert config.PROFILE_CACHE_TTL_SECONDS == 300
    
    def test_invalid_profile_retention_days(self):
        """Test that invalid PROFILE_RETENTION_DAYS raises error."""
        os.environ["PROFILE_RETENTION_DAYS"] = "not-an-int"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PROFILE_RETENTION_DAYS must be an integer" in str(exc_info.value)
        
        finally:
            for var in ["PROFILE_RETENTION_DAYS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_negative_profile_retention_days(self):
        """Test that negative PROFILE_RETENTION_DAYS raises error."""
        os.environ["PROFILE_RETENTION_DAYS"] = "0"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PROFILE_RETENTION_DAYS must be positive" in str(exc_info.value)
        
        finally:
            for var in ["PROFILE_RETENTION_DAYS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_invalid_profile_cache_ttl(self):
        """Test that invalid PROFILE_CACHE_TTL_SECONDS raises error."""
        os.environ["PROFILE_CACHE_TTL_SECONDS"] = "not-an-int"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PROFILE_CACHE_TTL_SECONDS must be an integer" in str(exc_info.value)
        
        finally:
            for var in ["PROFILE_CACHE_TTL_SECONDS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_negative_profile_cache_ttl(self):
        """Test that negative PROFILE_CACHE_TTL_SECONDS raises error."""
        os.environ["PROFILE_CACHE_TTL_SECONDS"] = "-1"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            assert "PROFILE_CACHE_TTL_SECONDS must be non-negative" in str(exc_info.value)
        
        finally:
            for var in ["PROFILE_CACHE_TTL_SECONDS", "JWT_SECRET_KEY"]:
                if var in os.environ:
                    del os.environ[var]
