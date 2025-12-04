"""
Tests for Support Interaction Logger.

Tests the logging functionality for support activations, crisis detections,
and bot interactions with privacy protection.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, SupportActivation, CrisisDetection, SupportInteraction
from backend.support.logger import SupportInteractionLogger
from backend.support.sentiment import SentimentResult, EmotionType, CrisisType


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def logger(db_session):
    """Create a SupportInteractionLogger instance."""
    return SupportInteractionLogger(db_session)


def test_log_support_activation(logger, db_session):
    """Test logging support activation."""
    # Create sentiment result
    sentiment = SentimentResult(
        emotion=EmotionType.SADNESS,
        intensity=0.8,
        requires_support=True,
        crisis_type=CrisisType.NONE,
        keywords=["sad", "lonely"]
    )
    
    # Log activation
    logger.log_support_activation(
        user_id=1,
        sentiment=sentiment,
        trigger_message="I feel so sad and lonely"
    )
    
    # Verify record was created
    activation = db_session.query(SupportActivation).first()
    assert activation is not None
    assert activation.user_id == 1
    assert activation.emotion_type == "sadness"
    assert activation.intensity == 0.8
    assert activation.trigger_message_hash is not None
    assert len(activation.trigger_message_hash) == 64  # SHA-256 hex length


def test_log_crisis_detection(logger, db_session):
    """Test logging crisis detection."""
    # Log crisis
    logger.log_crisis_detection(
        user_id=2,
        crisis_type=CrisisType.SUICIDE,
        message="I want to end it all",
        hotlines_provided=["AASRA", "Sneha India"]
    )
    
    # Verify record was created
    detection = db_session.query(CrisisDetection).first()
    assert detection is not None
    assert detection.user_id == 2
    assert detection.crisis_type == "suicide"
    assert detection.message_hash is not None
    assert len(detection.message_hash) == 64
    assert "AASRA" in detection.hotlines_provided
    assert "Sneha India" in detection.hotlines_provided


def test_log_bot_interaction(logger, db_session):
    """Test logging bot interaction."""
    # Log interaction
    logger.log_bot_interaction(
        user_id=3,
        user_message="I'm feeling really down today",
        bot_response="I hear you. Can you tell me more about what's making you feel down?"
    )
    
    # Verify record was created
    interaction = db_session.query(SupportInteraction).first()
    assert interaction is not None
    assert interaction.user_id == 3
    assert interaction.user_message_hash is not None
    assert interaction.bot_response_hash is not None
    assert len(interaction.user_message_hash) == 64
    assert len(interaction.bot_response_hash) == 64


def test_anonymize_content(logger):
    """Test content anonymization."""
    # Same content should produce same hash
    content = "This is sensitive content"
    hash1 = logger._anonymize_content(content)
    hash2 = logger._anonymize_content(content)
    assert hash1 == hash2
    assert len(hash1) == 64
    
    # Different content should produce different hash
    hash3 = logger._anonymize_content("Different content")
    assert hash3 != hash1
    
    # Empty content should return empty string
    hash4 = logger._anonymize_content("")
    assert hash4 == ""


def test_log_crisis_without_hotlines(logger, db_session):
    """Test logging crisis detection without hotlines."""
    logger.log_crisis_detection(
        user_id=4,
        crisis_type=CrisisType.SELF_HARM,
        message="I want to hurt myself",
        hotlines_provided=None
    )
    
    detection = db_session.query(CrisisDetection).first()
    assert detection is not None
    assert detection.hotlines_provided is None


def test_multiple_activations_same_user(logger, db_session):
    """Test logging multiple activations for the same user."""
    sentiment = SentimentResult(
        emotion=EmotionType.ANXIETY,
        intensity=0.7,
        requires_support=True,
        crisis_type=CrisisType.NONE,
        keywords=["anxious", "worried"]
    )
    
    # Log two activations
    logger.log_support_activation(1, sentiment, "I'm so anxious")
    logger.log_support_activation(1, sentiment, "I'm really worried")
    
    # Verify both records exist
    activations = db_session.query(SupportActivation).filter_by(user_id=1).all()
    assert len(activations) == 2
    # Hashes should be different for different messages
    assert activations[0].trigger_message_hash != activations[1].trigger_message_hash


def test_logging_handles_database_errors_gracefully(logger, db_session):
    """Test that logging errors don't crash the application."""
    # Close the session to simulate database error
    db_session.close()
    
    sentiment = SentimentResult(
        emotion=EmotionType.SADNESS,
        intensity=0.8,
        requires_support=True,
        crisis_type=CrisisType.NONE,
        keywords=["sad"]
    )
    
    # These should not raise exceptions
    logger.log_support_activation(1, sentiment, "test")
    logger.log_crisis_detection(1, CrisisType.SUICIDE, "test")
    logger.log_bot_interaction(1, "test", "test")
