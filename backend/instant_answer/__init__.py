"""
Instant Answer Recall System

This package provides AI-powered instant answers by searching historical conversations.
"""

from backend.instant_answer.classifier import (
    MessageType,
    MessageClassification,
    MessageClassifier
)
from backend.instant_answer.config import InstantAnswerConfig

__all__ = [
    "MessageType",
    "MessageClassification",
    "MessageClassifier",
    "InstantAnswerConfig",
]
