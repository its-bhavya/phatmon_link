"""
Rate limiter for Phantom Link BBS.

This module provides rate limiting functionality for messages and commands
to prevent spam and abuse.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import deque


class RateLimitViolation:
    """
    Represents a rate limit violation.
    
    Attributes:
        username: Username that violated the limit
        violation_type: Type of violation ('message' or 'command')
        timestamp: When the violation occurred
    """
    
    def __init__(self, username: str, violation_type: str):
        self.username = username
        self.violation_type = violation_type
        self.timestamp = datetime.utcnow()


class UserRateLimitState:
    """
    Tracks rate limit state for a single user.
    
    Attributes:
        username: Username being tracked
        message_timestamps: Deque of recent message timestamps
        command_timestamps: Deque of recent command timestamps
        violations: List of rate limit violations
        muted_until: Timestamp when temporary mute expires (None if not muted)
        warning_sent: Whether a warning has been sent for current violation
    """
    
    def __init__(self, username: str):
        self.username = username
        self.message_timestamps: deque = deque()
        self.command_timestamps: deque = deque()
        self.violations: List[RateLimitViolation] = []
        self.muted_until: datetime = None
        self.warning_sent: bool = False
    
    def is_muted(self) -> bool:
        """
        Check if user is currently muted.
        
        Returns:
            True if user is muted, False otherwise
        """
        if self.muted_until is None:
            return False
        
        if datetime.utcnow() >= self.muted_until:
            # Mute has expired
            self.muted_until = None
            self.warning_sent = False
            return False
        
        return True
    
    def add_message_timestamp(self) -> None:
        """Add a timestamp for a message."""
        self.message_timestamps.append(datetime.utcnow())
    
    def add_command_timestamp(self) -> None:
        """Add a timestamp for a command."""
        self.command_timestamps.append(datetime.utcnow())
    
    def add_violation(self, violation_type: str) -> None:
        """
        Record a rate limit violation.
        
        Args:
            violation_type: Type of violation ('message' or 'command')
        """
        violation = RateLimitViolation(self.username, violation_type)
        self.violations.append(violation)
    
    def get_recent_violations(self, seconds: int = 60) -> List[RateLimitViolation]:
        """
        Get violations within the last N seconds.
        
        Args:
            seconds: Time window to check (default: 60 seconds)
            
        Returns:
            List of recent violations
        """
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        return [v for v in self.violations if v.timestamp >= cutoff]
    
    def clean_old_timestamps(self, message_window: int = 10, command_window: int = 5) -> None:
        """
        Remove timestamps outside the rate limit windows.
        
        Args:
            message_window: Message rate limit window in seconds (default: 10)
            command_window: Command rate limit window in seconds (default: 5)
        """
        now = datetime.utcnow()
        
        # Clean message timestamps
        message_cutoff = now - timedelta(seconds=message_window)
        while self.message_timestamps and self.message_timestamps[0] < message_cutoff:
            self.message_timestamps.popleft()
        
        # Clean command timestamps
        command_cutoff = now - timedelta(seconds=command_window)
        while self.command_timestamps and self.command_timestamps[0] < command_cutoff:
            self.command_timestamps.popleft()


class RateLimiter:
    """
    Rate limiter for messages and commands.
    
    This class implements:
    - Message rate limiting: 10 messages per 10 seconds per user
    - Command rate limiting: 5 commands per 5 seconds per user
    - Warning on first violation
    - Temporary mute (30 seconds) on repeated violations
    - Disconnect recommendation on persistent abuse
    
    Attributes:
        user_states: Dict mapping username to UserRateLimitState
        message_limit: Maximum messages per window
        message_window: Time window for message limit (seconds)
        command_limit: Maximum commands per window
        command_window: Time window for command limit (seconds)
        mute_duration: Duration of temporary mute (seconds)
    """
    
    def __init__(
        self,
        message_limit: int = 10,
        message_window: int = 10,
        command_limit: int = 5,
        command_window: int = 5,
        mute_duration: int = 30
    ):
        """
        Initialize the rate limiter.
        
        Args:
            message_limit: Maximum messages per window (default: 10)
            message_window: Message window in seconds (default: 10)
            command_limit: Maximum commands per window (default: 5)
            command_window: Command window in seconds (default: 5)
            mute_duration: Mute duration in seconds (default: 30)
        """
        self.user_states: Dict[str, UserRateLimitState] = {}
        self.message_limit = message_limit
        self.message_window = message_window
        self.command_limit = command_limit
        self.command_window = command_window
        self.mute_duration = mute_duration
    
    def _get_user_state(self, username: str) -> UserRateLimitState:
        """
        Get or create user rate limit state.
        
        Args:
            username: Username to get state for
            
        Returns:
            UserRateLimitState for the user
        """
        if username not in self.user_states:
            self.user_states[username] = UserRateLimitState(username)
        return self.user_states[username]
    
    def check_message_limit(self, username: str) -> tuple[bool, str, bool]:
        """
        Check if user can send a message.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple of (allowed, message, should_disconnect)
            - allowed: True if message is allowed, False if rate limited
            - message: Error/warning message if not allowed, empty string if allowed
            - should_disconnect: True if user should be disconnected for persistent abuse
        """
        state = self._get_user_state(username)
        
        # Check if user is muted
        if state.is_muted():
            remaining = (state.muted_until - datetime.utcnow()).total_seconds()
            return (
                False,
                f"You are temporarily muted. {int(remaining)} seconds remaining.",
                False
            )
        
        # Clean old timestamps
        state.clean_old_timestamps(self.message_window, self.command_window)
        
        # Check if within limit
        if len(state.message_timestamps) < self.message_limit:
            # Within limit, allow message
            state.add_message_timestamp()
            return (True, "", False)
        
        # Rate limit exceeded
        state.add_violation('message')
        recent_violations = state.get_recent_violations(seconds=60)
        
        # Check for persistent abuse (3+ violations in last 60 seconds)
        if len(recent_violations) >= 3:
            return (
                False,
                "You have been disconnected for persistent rate limit violations.",
                True
            )
        
        # Check for repeated violations (2+ violations)
        if len(recent_violations) >= 2:
            # Apply temporary mute
            state.muted_until = datetime.utcnow() + timedelta(seconds=self.mute_duration)
            return (
                False,
                f"Rate limit exceeded. You have been muted for {self.mute_duration} seconds.",
                False
            )
        
        # First violation - send warning
        if not state.warning_sent:
            state.warning_sent = True
            return (
                False,
                f"Warning: Rate limit exceeded. Maximum {self.message_limit} messages per {self.message_window} seconds. Repeated violations will result in a temporary mute.",
                False
            )
        
        # Subsequent violations before mute
        return (
            False,
            f"Rate limit exceeded. Maximum {self.message_limit} messages per {self.message_window} seconds.",
            False
        )
    
    def check_command_limit(self, username: str) -> tuple[bool, str, bool]:
        """
        Check if user can execute a command.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple of (allowed, message, should_disconnect)
            - allowed: True if command is allowed, False if rate limited
            - message: Error message if not allowed, empty string if allowed
            - should_disconnect: True if user should be disconnected for persistent abuse
        """
        state = self._get_user_state(username)
        
        # Commands are not blocked by mute, but still rate limited
        
        # Clean old timestamps
        state.clean_old_timestamps(self.message_window, self.command_window)
        
        # Check if within limit
        if len(state.command_timestamps) < self.command_limit:
            # Within limit, allow command
            state.add_command_timestamp()
            return (True, "", False)
        
        # Rate limit exceeded
        state.add_violation('command')
        recent_violations = state.get_recent_violations(seconds=60)
        
        # Check for persistent abuse (3+ violations in last 60 seconds)
        if len(recent_violations) >= 3:
            return (
                False,
                "You have been disconnected for persistent rate limit violations.",
                True
            )
        
        # For commands, just send error and ignore
        return (
            False,
            f"Command rate limit exceeded. Maximum {self.command_limit} commands per {self.command_window} seconds.",
            False
        )
    
    def reset_user(self, username: str) -> None:
        """
        Reset rate limit state for a user (e.g., on disconnect).
        
        Args:
            username: Username to reset
        """
        if username in self.user_states:
            del self.user_states[username]
    
    def cleanup_inactive_users(self, active_usernames: List[str]) -> None:
        """
        Remove rate limit state for users who are no longer connected.
        
        Args:
            active_usernames: List of currently active usernames
        """
        inactive_users = [
            username for username in self.user_states.keys()
            if username not in active_usernames
        ]
        
        for username in inactive_users:
            del self.user_states[username]
