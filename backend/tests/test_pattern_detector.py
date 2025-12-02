"""
Tests for Pattern Detection Service.

This module tests the PatternDetector functionality including:
- Spam detection with configurable thresholds
- Command repetition detection
- Unusual activity detection using baseline deviation
"""

import pytest
from datetime import datetime, timedelta
from backend.vecna.pattern_detector import PatternDetector
from backend.vecna.user_profile import UserProfile


@pytest.fixture
def pattern_detector():
    """Create a PatternDetector instance with default settings."""
    return PatternDetector(
        spam_threshold=3,
        spam_window=5,
        command_repeat_threshold=3,
        command_repeat_window=10,
        anomaly_deviation_threshold=2.0
    )


@pytest.fixture
def user_profile():
    """Create a test user profile."""
    return UserProfile(user_id=1)


def test_pattern_detector_initialization():
    """Test PatternDetector initialization with custom thresholds."""
    detector = PatternDetector(
        spam_threshold=5,
        spam_window=10,
        command_repeat_threshold=4,
        command_repeat_window=20,
        anomaly_deviation_threshold=3.0
    )
    
    assert detector.spam_threshold == 5
    assert detector.spam_window == 10
    assert detector.command_repeat_threshold == 4
    assert detector.command_repeat_window == 20
    assert detector.anomaly_deviation_threshold == 3.0


def test_detect_spam_no_spam(pattern_detector):
    """Test spam detection with normal messages."""
    now = datetime.utcnow()
    recent_messages = [
        ("Hello", now - timedelta(seconds=10)),
        ("How are you?", now - timedelta(seconds=5))
    ]
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    assert is_spam is False


def test_detect_spam_threshold_met(pattern_detector):
    """Test spam detection when threshold is met."""
    now = datetime.utcnow()
    recent_messages = [
        ("spam1", now - timedelta(seconds=1)),
        ("spam2", now - timedelta(seconds=2)),
        ("spam3", now - timedelta(seconds=3))
    ]
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    assert is_spam is True


def test_detect_spam_outside_window(pattern_detector):
    """Test that spam detection only considers messages within time window."""
    now = datetime.utcnow()
    recent_messages = [
        ("msg1", now - timedelta(seconds=1)),
        ("msg2", now - timedelta(seconds=2)),
        ("msg3", now - timedelta(seconds=10))  # Outside 5-second window
    ]
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    # Only 2 messages in window, below threshold of 3
    assert is_spam is False


def test_detect_spam_exactly_at_threshold(pattern_detector):
    """Test spam detection when exactly at threshold."""
    now = datetime.utcnow()
    recent_messages = [
        ("msg1", now),
        ("msg2", now - timedelta(seconds=1)),
        ("msg3", now - timedelta(seconds=2))
    ]
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    # Exactly 3 messages in 5-second window
    assert is_spam is True


def test_detect_spam_insufficient_messages(pattern_detector):
    """Test spam detection with insufficient messages."""
    now = datetime.utcnow()
    recent_messages = [
        ("msg1", now)
    ]
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    assert is_spam is False


def test_detect_spam_empty_messages(pattern_detector):
    """Test spam detection with empty message list."""
    recent_messages = []
    
    is_spam = pattern_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    
    assert is_spam is False


def test_detect_command_repetition_no_repetition(pattern_detector, user_profile):
    """Test command repetition detection with varied commands."""
    now = datetime.utcnow()
    user_profile.command_history = [
        ("/join Archives", now),
        ("/list", now - timedelta(seconds=5)),
        ("/help", now - timedelta(seconds=8))
    ]
    
    is_repetition = pattern_detector.detect_command_repetition(user_profile)
    
    assert is_repetition is False


def test_detect_command_repetition_with_repetition(pattern_detector, user_profile):
    """Test command repetition detection with repeated commands."""
    now = datetime.utcnow()
    user_profile.command_history = [
        ("/list", now),
        ("/list", now - timedelta(seconds=3)),
        ("/list", now - timedelta(seconds=6))
    ]
    
    is_repetition = pattern_detector.detect_command_repetition(user_profile)
    
    assert is_repetition is True


def test_detect_command_repetition_outside_window(pattern_detector, user_profile):
    """Test that command repetition only considers time window."""
    now = datetime.utcnow()
    user_profile.command_history = [
        ("/list", now),
        ("/list", now - timedelta(seconds=15)),  # Outside 10s window
        ("/list", now - timedelta(seconds=20))   # Outside 10s window
    ]
    
    is_repetition = pattern_detector.detect_command_repetition(user_profile)
    
    # Only 1 command in window, below threshold
    assert is_repetition is False


def test_detect_command_repetition_insufficient_commands(pattern_detector, user_profile):
    """Test command repetition with insufficient command history."""
    now = datetime.utcnow()
    user_profile.command_history = [
        ("/list", now)
    ]
    
    is_repetition = pattern_detector.detect_command_repetition(user_profile)
    
    assert is_repetition is False


def test_detect_command_repetition_empty_history(pattern_detector, user_profile):
    """Test command repetition with empty command history."""
    user_profile.command_history = []
    
    is_repetition = pattern_detector.detect_command_repetition(user_profile)
    
    assert is_repetition is False


def test_detect_unusual_activity_no_baseline(pattern_detector, user_profile):
    """Test unusual activity detection with no baseline."""
    current_activity = {
        'messages_per_minute': 10.0,
        'commands_per_minute': 5.0
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # Should return False when no baseline exists
    assert is_unusual is False


def test_detect_unusual_activity_normal(pattern_detector, user_profile):
    """Test unusual activity detection with normal activity."""
    user_profile.activity_baseline = {
        'messages_per_minute': 2.0,
        'commands_per_minute': 1.0
    }
    
    current_activity = {
        'messages_per_minute': 2.1,
        'commands_per_minute': 1.0
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # Low deviation, should not trigger
    assert is_unusual is False


def test_detect_unusual_activity_high_deviation(pattern_detector, user_profile):
    """Test unusual activity detection with high deviation."""
    user_profile.activity_baseline = {
        'messages_per_minute': 2.0,
        'commands_per_minute': 1.0
    }
    
    current_activity = {
        'messages_per_minute': 10.0,  # 5x baseline
        'commands_per_minute': 5.0     # 5x baseline
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # High deviation (4.0), should trigger (threshold is 2.0)
    assert is_unusual is True


def test_detect_unusual_activity_at_threshold(pattern_detector, user_profile):
    """Test unusual activity detection at exact threshold."""
    user_profile.activity_baseline = {
        'messages_per_minute': 2.0
    }
    
    # Deviation of exactly 2.0 (threshold)
    current_activity = {
        'messages_per_minute': 6.0  # 3x baseline = 2.0 deviation
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # At threshold, should trigger
    assert is_unusual is True


def test_detect_unusual_activity_partial_metrics(pattern_detector, user_profile):
    """Test unusual activity with partial metric overlap."""
    user_profile.activity_baseline = {
        'messages_per_minute': 2.0,
        'commands_per_minute': 1.0
    }
    
    # Only provide one metric
    current_activity = {
        'messages_per_minute': 10.0
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # Should still calculate deviation for available metrics
    # Deviation = (10-2)/2 = 4.0, which exceeds threshold of 2.0
    assert is_unusual is True


def test_detect_unusual_activity_zero_baseline(pattern_detector, user_profile):
    """Test unusual activity with zero baseline values."""
    user_profile.activity_baseline = {
        'messages_per_minute': 0.0,
        'commands_per_minute': 1.0
    }
    
    current_activity = {
        'messages_per_minute': 5.0,
        'commands_per_minute': 5.0
    }
    
    is_unusual = pattern_detector.detect_unusual_activity(user_profile, current_activity)
    
    # Should handle zero baseline gracefully
    # Only commands_per_minute deviation is calculated: (5-1)/1 = 4.0
    assert is_unusual is True


def test_custom_thresholds():
    """Test PatternDetector with custom thresholds."""
    # More lenient detector
    lenient_detector = PatternDetector(
        spam_threshold=10,
        spam_window=30,
        anomaly_deviation_threshold=5.0
    )
    
    now = datetime.utcnow()
    recent_messages = [
        ("msg1", now),
        ("msg2", now - timedelta(seconds=1)),
        ("msg3", now - timedelta(seconds=2))
    ]
    
    # Should not trigger with lenient threshold
    is_spam = lenient_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    assert is_spam is False
    
    # More strict detector
    strict_detector = PatternDetector(
        spam_threshold=2,
        spam_window=10,
        anomaly_deviation_threshold=1.0
    )
    
    # Should trigger with strict threshold
    is_spam = strict_detector.detect_spam(user_id=1, recent_messages=recent_messages)
    assert is_spam is True


def test_integration_all_patterns(pattern_detector, user_profile):
    """Test integration of all pattern detection methods."""
    now = datetime.utcnow()
    
    # Set up profile with baseline
    user_profile.activity_baseline = {
        'messages_per_minute': 2.0,
        'commands_per_minute': 1.0
    }
    
    # Set up command history with repetition
    user_profile.command_history = [
        ("/list", now),
        ("/list", now - timedelta(seconds=3)),
        ("/list", now - timedelta(seconds=6))
    ]
    
    # Test spam detection
    spam_messages = [
        ("spam", now),
        ("spam", now - timedelta(seconds=1)),
        ("spam", now - timedelta(seconds=2))
    ]
    assert pattern_detector.detect_spam(user_id=1, recent_messages=spam_messages) is True
    
    # Test command repetition
    assert pattern_detector.detect_command_repetition(user_profile) is True
    
    # Test unusual activity
    unusual_activity = {
        'messages_per_minute': 10.0,
        'commands_per_minute': 5.0
    }
    assert pattern_detector.detect_unusual_activity(user_profile, unusual_activity) is True
