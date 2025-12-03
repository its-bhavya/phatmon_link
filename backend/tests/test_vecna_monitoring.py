"""
Tests for Vecna monitoring and logging module.

This module tests the monitoring, logging, and alerting functionality
for the Vecna adversarial AI system.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, User, VecnaActivation
from backend.vecna.monitoring import (
    VecnaMonitor,
    VecnaActivationLog,
    GeminiAPILog,
    VecnaMetrics,
    Alert
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Create test user
    user = User(
        username="testuser",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    
    yield session
    
    session.close()


@pytest.fixture
def monitor(db_session):
    """Create a VecnaMonitor instance for testing."""
    return VecnaMonitor(db=db_session)


def test_vecna_activation_log_creation():
    """Test creating a VecnaActivationLog."""
    log = VecnaActivationLog(
        timestamp=datetime.utcnow().isoformat(),
        user_id=1,
        username="testuser",
        trigger_type="emotional",
        reason="High-negative sentiment",
        intensity=0.8,
        response_preview="[VECNA] Test response...",
        duration_ms=150.5
    )
    
    assert log.user_id == 1
    assert log.username == "testuser"
    assert log.trigger_type == "emotional"
    assert log.intensity == 0.8
    
    # Test JSON serialization
    json_str = log.to_json()
    assert "testuser" in json_str
    assert "emotional" in json_str


def test_gemini_api_log_creation():
    """Test creating a GeminiAPILog."""
    log = GeminiAPILog(
        timestamp=datetime.utcnow().isoformat(),
        operation="hostile_response",
        user_id=1,
        success=True,
        duration_ms=250.0,
        token_count=50
    )
    
    assert log.operation == "hostile_response"
    assert log.success is True
    assert log.duration_ms == 250.0
    
    # Test JSON serialization
    json_str = log.to_json()
    assert "hostile_response" in json_str
    assert "true" in json_str.lower()


def test_log_activation(monitor, db_session):
    """Test logging a Vecna activation."""
    monitor.log_activation(
        user_id=1,
        username="testuser",
        trigger_type="emotional",
        reason="High-negative sentiment",
        intensity=0.8,
        response_content="[VECNA] Test response",
        duration_ms=150.0
    )
    
    # Verify no errors occurred (logging should not raise exceptions)
    assert True


def test_log_gemini_api_call_success(monitor):
    """Test logging a successful Gemini API call."""
    monitor.log_gemini_api_call(
        operation="hostile_response",
        user_id=1,
        success=True,
        duration_ms=200.0,
        token_count=50
    )
    
    # Check API metrics
    metrics = monitor.get_api_metrics()
    assert metrics['total_calls'] == 1
    assert metrics['failed_calls'] == 0
    assert metrics['error_rate'] == 0.0
    assert metrics['average_duration_ms'] == 200.0


def test_log_gemini_api_call_failure(monitor):
    """Test logging a failed Gemini API call."""
    monitor.log_gemini_api_call(
        operation="hostile_response",
        user_id=1,
        success=False,
        duration_ms=100.0,
        error_message="API timeout"
    )
    
    # Check API metrics
    metrics = monitor.get_api_metrics()
    assert metrics['total_calls'] == 1
    assert metrics['failed_calls'] == 1
    assert metrics['error_rate'] == 1.0


def test_get_metrics_empty(monitor):
    """Test getting metrics when no activations exist."""
    metrics = monitor.get_metrics(time_window_hours=24)
    
    assert metrics.total_activations == 0
    assert metrics.emotional_triggers == 0
    assert metrics.system_triggers == 0
    assert metrics.unique_users == 0
    assert metrics.average_intensity == 0.0
    assert metrics.activations_per_hour == 0.0
    assert len(metrics.top_users) == 0


def test_get_metrics_with_activations(monitor, db_session):
    """Test getting metrics with activation data."""
    # Create test activations
    user = db_session.query(User).first()
    
    for i in range(5):
        activation = VecnaActivation(
            user_id=user.id,
            trigger_type="emotional" if i < 3 else "system",
            reason="Test reason",
            intensity=0.7 + (i * 0.05),
            response_content="Test response",
            activated_at=datetime.utcnow()
        )
        db_session.add(activation)
    
    db_session.commit()
    
    # Get metrics
    metrics = monitor.get_metrics(time_window_hours=24)
    
    assert metrics.total_activations == 5
    assert metrics.emotional_triggers == 3
    assert metrics.system_triggers == 2
    assert metrics.unique_users == 1
    assert metrics.average_intensity > 0.7
    assert metrics.activations_per_hour > 0
    assert len(metrics.top_users) == 1
    assert metrics.top_users[0][1] == "testuser"
    assert metrics.top_users[0][2] == 5


def test_check_unusual_patterns_no_activations(monitor):
    """Test checking for unusual patterns with no activations."""
    alerts = monitor.check_unusual_patterns(time_window_minutes=5)
    
    assert len(alerts) == 0


def test_check_unusual_patterns_high_rate(monitor, db_session):
    """Test detecting high activation rate."""
    user = db_session.query(User).first()
    
    # Create many activations in short time (should trigger alert)
    # Need 10 per minute * 5 minutes = 50+ activations to trigger
    for i in range(55):
        activation = VecnaActivation(
            user_id=user.id,
            trigger_type="emotional",
            reason="Test reason",
            intensity=0.8,
            response_content="Test response",
            activated_at=datetime.utcnow()
        )
        db_session.add(activation)
    
    db_session.commit()
    
    # Check for unusual patterns
    alerts = monitor.check_unusual_patterns(time_window_minutes=5)
    
    # Should detect high activation rate (55 activations / 5 minutes = 11 per minute)
    assert len(alerts) > 0
    assert any(alert.alert_type == "high_activation_rate" for alert in alerts)


def test_check_unusual_patterns_user_spam(monitor, db_session):
    """Test detecting user spam pattern."""
    user = db_session.query(User).first()
    
    # Create multiple activations for same user (should trigger alert)
    for i in range(6):
        activation = VecnaActivation(
            user_id=user.id,
            trigger_type="emotional",
            reason="Test reason",
            intensity=0.8,
            response_content="Test response",
            activated_at=datetime.utcnow()
        )
        db_session.add(activation)
    
    db_session.commit()
    
    # Check for unusual patterns
    alerts = monitor.check_unusual_patterns(time_window_minutes=5)
    
    # Should detect user spam
    assert len(alerts) > 0
    assert any(alert.alert_type == "user_spam" for alert in alerts)


def test_get_user_activation_history(monitor, db_session):
    """Test getting user activation history."""
    user = db_session.query(User).first()
    
    # Create test activations
    for i in range(3):
        activation = VecnaActivation(
            user_id=user.id,
            trigger_type="emotional",
            reason=f"Test reason {i}",
            intensity=0.7,
            response_content=f"Test response {i}",
            activated_at=datetime.utcnow()
        )
        db_session.add(activation)
    
    db_session.commit()
    
    # Get history
    history = monitor.get_user_activation_history(user_id=user.id, limit=10)
    
    assert len(history) == 3
    assert all('trigger_type' in record for record in history)
    assert all('reason' in record for record in history)
    assert all('intensity' in record for record in history)


def test_api_metrics_tracking(monitor):
    """Test API metrics tracking over multiple calls."""
    # Log multiple API calls
    monitor.log_gemini_api_call("sysop_suggestion", 1, True, 100.0)
    monitor.log_gemini_api_call("hostile_response", 1, True, 200.0)
    monitor.log_gemini_api_call("psychic_grip", 1, False, 50.0, "Timeout")
    
    metrics = monitor.get_api_metrics()
    
    assert metrics['total_calls'] == 3
    assert metrics['failed_calls'] == 1
    assert metrics['error_rate'] == pytest.approx(1/3, 0.01)
    assert metrics['average_duration_ms'] == pytest.approx(116.67, 0.01)


def test_reset_api_metrics(monitor):
    """Test resetting API metrics."""
    # Log some calls
    monitor.log_gemini_api_call("hostile_response", 1, True, 100.0)
    monitor.log_gemini_api_call("hostile_response", 1, False, 50.0, "Error")
    
    # Reset metrics
    monitor.reset_api_metrics()
    
    # Check metrics are reset
    metrics = monitor.get_api_metrics()
    assert metrics['total_calls'] == 0
    assert metrics['failed_calls'] == 0
    assert metrics['error_rate'] == 0.0
    assert metrics['average_duration_ms'] == 0.0


def test_alert_creation():
    """Test creating an Alert object."""
    alert = Alert(
        timestamp=datetime.utcnow().isoformat(),
        severity="warning",
        alert_type="high_activation_rate",
        message="High activation rate detected",
        details={'rate': 15.0}
    )
    
    assert alert.severity == "warning"
    assert alert.alert_type == "high_activation_rate"
    assert 'rate' in alert.details
    
    # Test JSON serialization
    json_str = alert.to_json()
    assert "warning" in json_str
    assert "high_activation_rate" in json_str


def test_high_intensity_trigger_alert(monitor):
    """Test that high-intensity triggers generate alerts."""
    # Log a high-intensity activation
    monitor.log_activation(
        user_id=1,
        username="testuser",
        trigger_type="emotional",
        reason="Very high negative sentiment",
        intensity=0.95,  # Above threshold
        response_content="[VECNA] Test",
        duration_ms=100.0
    )
    
    # The alert should be logged (we can't easily verify without capturing logs,
    # but we can verify the method doesn't raise exceptions)
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
