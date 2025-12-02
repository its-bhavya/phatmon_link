"""
Pattern Detection Service for Vecna Adversarial AI Module.

This module provides pattern detection for system triggers including spam detection,
command repetition detection, and unusual activity detection based on baseline deviations.

Requirements: 2.2, 2.3, 2.4
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
from backend.vecna.user_profile import UserProfile


class PatternDetector:
    """
    Pattern detection for system triggers.
    
    This class provides methods for detecting anomalous patterns in user behavior
    including spam, command repetition, and unusual activity deviating from baseline.
    
    Attributes:
        spam_threshold: Number of similar messages to trigger spam detection
        spam_window: Time window in seconds for spam detection
        command_repeat_threshold: Number of repeated commands to trigger detection
        command_repeat_window: Time window in seconds for command repetition
        anomaly_deviation_threshold: Deviation threshold for unusual activity
    """
    
    def __init__(
        self,
        spam_threshold: int = 3,
        spam_window: int = 5,
        command_repeat_threshold: int = 3,
        command_repeat_window: int = 10,
        anomaly_deviation_threshold: float = 2.0
    ):
        """
        Initialize the pattern detector with configurable thresholds.
        
        Args:
            spam_threshold: Number of messages to consider spam (default: 3)
            spam_window: Time window in seconds for spam detection (default: 5)
            command_repeat_threshold: Number of repeated commands (default: 3)
            command_repeat_window: Time window in seconds for command repetition (default: 10)
            anomaly_deviation_threshold: Deviation multiplier for anomaly detection (default: 2.0)
        """
        self.spam_threshold = spam_threshold
        self.spam_window = spam_window
        self.command_repeat_threshold = command_repeat_threshold
        self.command_repeat_window = command_repeat_window
        self.anomaly_deviation_threshold = anomaly_deviation_threshold
    
    def detect_spam(
        self, 
        user_id: int, 
        recent_messages: List[Tuple[str, datetime]]
    ) -> bool:
        """
        Detect spam patterns in recent messages.
        
        Spam is detected when a user sends multiple messages within a short
        time window. This method checks both message frequency and content
        similarity.
        
        Args:
            user_id: User database ID
            recent_messages: List of tuples containing (message_text, timestamp)
        
        Returns:
            True if spam pattern detected, False otherwise
        
        Requirements: 2.2 (spam pattern detection)
        """
        if len(recent_messages) < self.spam_threshold:
            return False
        
        # Get messages within the spam window
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=self.spam_window)
        
        messages_in_window = [
            (msg, timestamp) for msg, timestamp in recent_messages
            if timestamp >= cutoff_time
        ]
        
        # Check if we have enough messages in the window
        if len(messages_in_window) >= self.spam_threshold:
            return True
        
        return False
    
    def detect_command_repetition(
        self, 
        user_profile: UserProfile
    ) -> bool:
        """
        Detect repeated command execution.
        
        This method checks if a user has executed the same or similar commands
        repeatedly within a short time window, which may indicate automated
        behavior or frustration.
        
        Args:
            user_profile: UserProfile object containing command history
        
        Returns:
            True if command repetition detected, False otherwise
        
        Requirements: 2.3 (command repetition detection)
        """
        # Delegate to UserProfile's built-in method
        return user_profile.detect_command_repetition(
            window_seconds=self.command_repeat_window
        )
    
    def detect_unusual_activity(
        self, 
        user_profile: UserProfile,
        current_activity: Dict[str, Any]
    ) -> bool:
        """
        Detect activity deviating from user baseline.
        
        This method compares current activity metrics against the user's
        established baseline to identify unusual behavior patterns that
        may warrant Vecna activation.
        
        Args:
            user_profile: UserProfile object containing baseline data
            current_activity: Dict containing current activity metrics
                Expected keys: 'messages_per_minute', 'commands_per_minute',
                'room_switches_per_hour'
        
        Returns:
            True if unusual activity detected, False otherwise
        
        Requirements: 2.4 (anomaly detection)
        """
        # Calculate deviation from baseline
        deviation = user_profile.calculate_deviation(current_activity)
        
        # Check if deviation exceeds threshold
        if deviation >= self.anomaly_deviation_threshold:
            return True
        
        return False
