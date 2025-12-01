"""
Tests for rate limiter functionality.

This module tests:
- Message rate limiting (10 messages per 10 seconds)
- Command rate limiting (5 commands per 5 seconds)
- Warning on first violation
- Temporary mute on repeated violations
- Disconnect recommendation on persistent abuse
"""

import pytest
from datetime import datetime, timedelta
from backend.rate_limiter import RateLimiter, UserRateLimitState


class TestUserRateLimitState:
    """Test UserRateLimitState class."""
    
    def test_initialization(self):
        """Test that UserRateLimitState initializes correctly."""
        state = UserRateLimitState("testuser")
        
        assert state.username == "testuser"
        assert len(state.message_timestamps) == 0
        assert len(state.command_timestamps) == 0
        assert len(state.violations) == 0
        assert state.muted_until is None
        assert state.warning_sent is False
    
    def test_is_muted_when_not_muted(self):
        """Test is_muted returns False when user is not muted."""
        state = UserRateLimitState("testuser")
        assert state.is_muted() is False
    
    def test_is_muted_when_muted(self):
        """Test is_muted returns True when user is muted."""
        state = UserRateLimitState("testuser")
        state.muted_until = datetime.utcnow() + timedelta(seconds=30)
        assert state.is_muted() is True
    
    def test_is_muted_expires(self):
        """Test that mute expires after timeout."""
        state = UserRateLimitState("testuser")
        state.muted_until = datetime.utcnow() - timedelta(seconds=1)
        assert state.is_muted() is False
        assert state.muted_until is None
    
    def test_add_timestamps(self):
        """Test adding message and command timestamps."""
        state = UserRateLimitState("testuser")
        
        state.add_message_timestamp()
        assert len(state.message_timestamps) == 1
        
        state.add_command_timestamp()
        assert len(state.command_timestamps) == 1
    
    def test_add_violation(self):
        """Test recording violations."""
        state = UserRateLimitState("testuser")
        
        state.add_violation('message')
        assert len(state.violations) == 1
        assert state.violations[0].violation_type == 'message'
    
    def test_get_recent_violations(self):
        """Test getting recent violations."""
        state = UserRateLimitState("testuser")
        
        # Add old violation
        state.add_violation('message')
        state.violations[0].timestamp = datetime.utcnow() - timedelta(seconds=120)
        
        # Add recent violation
        state.add_violation('command')
        
        recent = state.get_recent_violations(seconds=60)
        assert len(recent) == 1
        assert recent[0].violation_type == 'command'


class TestRateLimiter:
    """Test RateLimiter class."""
    
    def test_initialization(self):
        """Test that RateLimiter initializes with correct defaults."""
        limiter = RateLimiter()
        
        assert limiter.message_limit == 10
        assert limiter.message_window == 10
        assert limiter.command_limit == 5
        assert limiter.command_window == 5
        assert limiter.mute_duration == 30
        assert len(limiter.user_states) == 0
    
    def test_custom_initialization(self):
        """Test RateLimiter with custom parameters."""
        limiter = RateLimiter(
            message_limit=5,
            message_window=20,
            command_limit=3,
            command_window=10,
            mute_duration=60
        )
        
        assert limiter.message_limit == 5
        assert limiter.message_window == 20
        assert limiter.command_limit == 3
        assert limiter.command_window == 10
        assert limiter.mute_duration == 60
    
    def test_message_within_limit(self):
        """Test that messages within limit are allowed."""
        limiter = RateLimiter(message_limit=10, message_window=10)
        
        # Send 10 messages (within limit)
        for i in range(10):
            allowed, message, disconnect = limiter.check_message_limit("testuser")
            assert allowed is True
            assert message == ""
            assert disconnect is False
    
    def test_message_exceeds_limit_warning(self):
        """Test that exceeding message limit sends warning."""
        limiter = RateLimiter(message_limit=3, message_window=10)
        
        # Send 3 messages (within limit)
        for i in range(3):
            allowed, _, _ = limiter.check_message_limit("testuser")
            assert allowed is True
        
        # 4th message should trigger warning
        allowed, message, disconnect = limiter.check_message_limit("testuser")
        assert allowed is False
        assert "Warning" in message
        assert "Rate limit exceeded" in message
        assert disconnect is False
    
    def test_message_repeated_violation_mute(self):
        """Test that repeated violations result in temporary mute."""
        limiter = RateLimiter(message_limit=2, message_window=10, mute_duration=30)
        
        # First violation - warning
        for i in range(2):
            limiter.check_message_limit("testuser")
        allowed, message, disconnect = limiter.check_message_limit("testuser")
        assert allowed is False
        assert "Warning" in message
        
        # Second violation - mute
        for i in range(2):
            limiter.check_message_limit("testuser")
        allowed, message, disconnect = limiter.check_message_limit("testuser")
        assert allowed is False
        assert "muted" in message.lower()
        assert "30 seconds" in message
        assert disconnect is False
        
        # Verify user is muted
        state = limiter.user_states["testuser"]
        assert state.is_muted() is True
    
    def test_message_persistent_abuse_disconnect(self):
        """Test that persistent abuse triggers disconnect."""
        limiter = RateLimiter(message_limit=2, message_window=10, mute_duration=30)
        
        # Manually create violations to simulate persistent abuse
        state = limiter._get_user_state("testuser")
        
        # Add 3 violations within 60 seconds
        for i in range(3):
            state.add_violation('message')
        
        # Next rate limit check should trigger disconnect
        for i in range(2):
            limiter.check_message_limit("testuser")
        allowed, message, disconnect = limiter.check_message_limit("testuser")
        assert allowed is False
        assert disconnect is True
        assert "disconnected" in message.lower()
    
    def test_command_within_limit(self):
        """Test that commands within limit are allowed."""
        limiter = RateLimiter(command_limit=5, command_window=5)
        
        # Send 5 commands (within limit)
        for i in range(5):
            allowed, message, disconnect = limiter.check_command_limit("testuser")
            assert allowed is True
            assert message == ""
            assert disconnect is False
    
    def test_command_exceeds_limit(self):
        """Test that exceeding command limit sends error."""
        limiter = RateLimiter(command_limit=3, command_window=5)
        
        # Send 3 commands (within limit)
        for i in range(3):
            allowed, _, _ = limiter.check_command_limit("testuser")
            assert allowed is True
        
        # 4th command should be blocked
        allowed, message, disconnect = limiter.check_command_limit("testuser")
        assert allowed is False
        assert "Command rate limit exceeded" in message
        assert disconnect is False
    
    def test_command_persistent_abuse_disconnect(self):
        """Test that persistent command abuse triggers disconnect."""
        limiter = RateLimiter(command_limit=2, command_window=5)
        
        # Trigger 3 violations
        for violation in range(3):
            for i in range(2):
                limiter.check_command_limit("testuser")
            limiter.check_command_limit("testuser")
        
        # Next violation should trigger disconnect
        for i in range(2):
            limiter.check_command_limit("testuser")
        allowed, message, disconnect = limiter.check_command_limit("testuser")
        assert allowed is False
        assert disconnect is True
    
    def test_muted_user_cannot_send_messages(self):
        """Test that muted users cannot send messages."""
        limiter = RateLimiter(message_limit=2, message_window=10, mute_duration=30)
        
        # Trigger mute
        for i in range(2):
            limiter.check_message_limit("testuser")
        limiter.check_message_limit("testuser")  # Warning
        
        for i in range(2):
            limiter.check_message_limit("testuser")
        limiter.check_message_limit("testuser")  # Mute
        
        # Try to send message while muted
        allowed, message, disconnect = limiter.check_message_limit("testuser")
        assert allowed is False
        assert "muted" in message.lower()
        assert "seconds remaining" in message.lower()
    
    def test_reset_user(self):
        """Test resetting user rate limit state."""
        limiter = RateLimiter()
        
        # Create some state
        limiter.check_message_limit("testuser")
        assert "testuser" in limiter.user_states
        
        # Reset
        limiter.reset_user("testuser")
        assert "testuser" not in limiter.user_states
    
    def test_cleanup_inactive_users(self):
        """Test cleaning up inactive users."""
        limiter = RateLimiter()
        
        # Create state for multiple users
        limiter.check_message_limit("user1")
        limiter.check_message_limit("user2")
        limiter.check_message_limit("user3")
        
        assert len(limiter.user_states) == 3
        
        # Cleanup, keeping only user1 and user2
        limiter.cleanup_inactive_users(["user1", "user2"])
        
        assert len(limiter.user_states) == 2
        assert "user1" in limiter.user_states
        assert "user2" in limiter.user_states
        assert "user3" not in limiter.user_states
    
    def test_separate_message_and_command_limits(self):
        """Test that message and command limits are tracked separately."""
        limiter = RateLimiter(message_limit=3, command_limit=2)
        
        # Send 3 messages (at limit)
        for i in range(3):
            allowed, _, _ = limiter.check_message_limit("testuser")
            assert allowed is True
        
        # Send 2 commands (at limit)
        for i in range(2):
            allowed, _, _ = limiter.check_command_limit("testuser")
            assert allowed is True
        
        # Next message should be blocked
        allowed, _, _ = limiter.check_message_limit("testuser")
        assert allowed is False
        
        # Next command should be blocked
        allowed, _, _ = limiter.check_command_limit("testuser")
        assert allowed is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
