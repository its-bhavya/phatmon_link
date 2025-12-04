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
from backend.instant_answer.tagger import (
    MessageTags,
    AutoTagger
)

__all__ = [
    "MessageType",
    "MessageClassification",
    "MessageClassifier",
    "InstantAnswerConfig",
    "MessageTags",
    "AutoTagger",
]
