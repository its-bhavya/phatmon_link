"""
Tests for Vecna Rate Limiter.

This module tests the abuse prevention mechanisms for Vecna activations.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, VecnaActivation
from backend.vecna.rate_limiter import VecnaRateLimiter, VecnaRateLimitResult


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def rate_limiter(db_session):
    """Create a VecnaRateLimiter instance for testing."""
    return VecnaRateLimiter(
        db=db_session,
        max_activations_per_hour=5,
        cooldown_seconds=60,
        enabled=True
    )


def test_rate_limiter_initialization(rate_limiter):
    """Test that rate limiter initializes with correct configuration."""
    assert rate_limiter.max_activations_per_hour == 5
    assert rate_limiter.cooldown_seconds == 60
    assert rate_limiter.enabled is True


def test_rate_limiter_allows_first_activation(rate_limiter):
    """Test that first activation is allowed."""
    result = rate_limiter.check_rate_limit(user_id=1)
    
    assert result.allowed is True
    assert result.reason is None
    assert result.activations_remaining == 5


def test_rate_limiter_enforces_cooldown(rate_limiter):
    """Test that cooldown period is enforced between activations."""
    user_id = 1
    
    # Record first activation
    rate_limiter.record_activation(
        user_id=user_id,
        trigger_type="emotional",
        reason="Test trigger",
        intensity=0.8,
        response_content="Test response"
    )
    
    # Immediate second activation should be blocked
    result = rate_limiter.check_rate_limit(user_id)
    
    assert result.allowed is False
    assert "cooldown" in result.reason.lower()
    assert result.cooldown_remaining > 0


def test_rate_limiter_allows_after_cooldown(rate_limiter):
    """Test that activation is allowed after cooldown expires."""
    user_id = 1
    
    # Record activation with past timestamp
    past_time = datetime.utcnow() - timedelta(seconds=61)
    rate_limiter._last_activation[user_id] = past_time
    
    # Should be allowed now
    result = rate_limiter.check_rate_limit(user_id)
    
    assert result.allowed is True


def test_rate_limiter_enforces_hourly_limit(rate_limiter, db_session):
    """Test that hourly activation limit is enforced."""
    user_id = 1
    
    # Create 5 activations in the last hour
    for i in range(5):
        activation = VecnaActivation(
            user_id=user_id,
            trigger_type="emotional",
            reason=f"Test trigger {i}",
            intensity=0.8,
            response_content=f"Test response {i}",
            activated_at=datetime.utcnow() - timedelta(minutes=i * 10)
        )
        db_session.add(activation)
    db_session.commit()
    
    # Clear cooldown to test only hourly limit
    rate_limiter._last_activation.clear()
    
    # Next activation should be blocked
    result = rate_limiter.check_rate_limit(user_id)
    
    assert result.allowed is False
    assert "limit reached" in result.reason.lower()
    assert result.activations_remaining == 0


def test_rate_limiter_allows_after_hour_expires(rate_limiter, db_session):
    """Test that activations are allowed after the hour window expires."""
    user_id = 1
    
    # Create 5 activations more than 1 hour ago
    for i in range(5):
        activation = VecnaActivation(
            user_id=user_id,
            trigger_type="emotional",
            reason=f"Test trigger {i}",
            intensity=0.8,
            response_content=f"Test response {i}",
            activated_at=datetime.utcnow() - timedelta(hours=2)
        )
        db_session.add(activation)
    db_session.commit()
    
    # Should be allowed now
    result = rate_limiter.check_rate_limit(user_id)
    
    assert result.allowed is True


def test_rate_limiter_respects_global_disable(rate_limiter):
    """Test that global disable prevents all activations."""
    rate_limiter.set_enabled(False)
    
    result = rate_limiter.check_rate_limit(user_id=1)
    
    assert result.allowed is False
    assert "disabled" in result.reason.lower()


def test_rate_limiter_records_activation(rate_limiter, db_session):
    """Test that activations are properly recorded in database."""
    user_id = 1
    
    rate_limiter.record_activation(
        user_id=user_id,
        trigger_type="emotional",
        reason="Test trigger",
        intensity=0.8,
        response_content="Test response"
    )
    
    # Check database
    activation = db_session.query(VecnaActivation).filter_by(user_id=user_id).first()
    
    assert activation is not None
    assert activation.trigger_type == "emotional"
    assert activation.reason == "Test trigger"
    assert activation.intensity == 0.8
    assert activation.response_content == "Test response"


def test_rate_limiter_tracks_multiple_users(rate_limiter):
    """Test that rate limiter tracks different users independently."""
    # User 1 activates
    rate_limiter.record_activation(
        user_id=1,
        trigger_type="emotional",
        reason="Test",
        intensity=0.8,
        response_content="Test"
    )
    
    # User 1 should be in cooldown
    result1 = rate_limiter.check_rate_limit(user_id=1)
    assert result1.allowed is False
    
    # User 2 should be allowed
    result2 = rate_limiter.check_rate_limit(user_id=2)
    assert result2.allowed is True


def test_get_user_activation_stats(rate_limiter, db_session):
    """Test that user activation statistics are correctly calculated."""
    user_id = 1
    
    # Create some activations
    for i in range(3):
        activation = VecnaActivation(
            user_id=user_id,
            trigger_type="emotional",
            reason=f"Test {i}",
            intensity=0.8,
            response_content=f"Response {i}",
            activated_at=datetime.utcnow() - timedelta(minutes=i * 10)
        )
        db_session.add(activation)
    db_session.commit()
    
    stats = rate_limiter.get_user_activation_stats(user_id)
    
    assert stats["total_activations"] == 3
    assert stats["activations_last_hour"] == 3
    assert stats["activations_remaining"] == 2


def test_reset_user_cooldown(rate_limiter):
    """Test that admin can reset user cooldown."""
    user_id = 1
    
    # Record activation
    rate_limiter.record_activation(
        user_id=user_id,
        trigger_type="emotional",
        reason="Test",
        intensity=0.8,
        response_content="Test"
    )
    
    # Should be in cooldown
    result = rate_limiter.check_rate_limit(user_id)
    assert result.allowed is False
    
    # Reset cooldown
    rate_limiter.reset_user_cooldown(user_id)
    
    # Should be allowed now (if under hourly limit)
    result = rate_limiter.check_rate_limit(user_id)
    assert result.allowed is True


def test_cleanup_old_activations(rate_limiter, db_session):
    """Test that old activation records are cleaned up."""
    user_id = 1
    
    # Create old activations (35 days ago)
    for i in range(3):
        activation = VecnaActivation(
            user_id=user_id,
            trigger_type="emotional",
            reason=f"Old test {i}",
            intensity=0.8,
            response_content=f"Old response {i}",
            activated_at=datetime.utcnow() - timedelta(days=35)
        )
        db_session.add(activation)
    
    # Create recent activations
    for i in range(2):
        activation = VecnaActivation(
            user_id=user_id,
            trigger_type="emotional",
            reason=f"Recent test {i}",
            intensity=0.8,
            response_content=f"Recent response {i}",
            activated_at=datetime.utcnow() - timedelta(days=5)
        )
        db_session.add(activation)
    
    db_session.commit()
    
    # Cleanup old records (older than 30 days)
    deleted_count = rate_limiter.cleanup_old_activations(days=30)
    
    assert deleted_count == 3
    
    # Check that only recent records remain
    remaining = db_session.query(VecnaActivation).count()
    assert remaining == 2


def test_rate_limiter_with_zero_cooldown(db_session):
    """Test rate limiter with zero cooldown (only hourly limit)."""
    rate_limiter = VecnaRateLimiter(
        db=db_session,
        max_activations_per_hour=3,
        cooldown_seconds=0,
        enabled=True
    )
    
    # With zero cooldown, we need to manually clear the tracker after each check
    # to simulate immediate successive activations
    for i in range(3):
        # Clear cooldown tracker to simulate zero cooldown
        rate_limiter._last_activation.clear()
        
        result = rate_limiter.check_rate_limit(user_id=1)
        assert result.allowed is True
        
        rate_limiter.record_activation(
            user_id=1,
            trigger_type="emotional",
            reason=f"Test {i}",
            intensity=0.8,
            response_content=f"Response {i}"
        )
    
    # Clear cooldown for final check
    rate_limiter._last_activation.clear()
    
    # Fourth should be blocked by hourly limit
    result = rate_limiter.check_rate_limit(user_id=1)
    assert result.allowed is False
    assert "limit reached" in result.reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
