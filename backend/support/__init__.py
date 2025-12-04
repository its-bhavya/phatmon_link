"""
Support Bot module for empathetic emotional support.

This module provides sentiment analysis, crisis detection, and empathetic
AI-powered support for users experiencing negative emotions.
"""

from backend.support.sentiment import (
    EmotionType,
    CrisisType,
    SentimentResult,
    SentimentAnalyzer
)
from backend.support.hotlines import (
    HotlineInfo,
    CrisisHotlineService
)

__all__ = [
    'EmotionType',
    'CrisisType',
    'SentimentResult',
    'SentimentAnalyzer',
    'HotlineInfo',
    'CrisisHotlineService',
]
