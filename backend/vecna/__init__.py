"""
Vecna Adversarial AI Module.

This module provides adversarial AI functionality for the Phantom Link BBS,
including user profile tracking, sentiment analysis, pattern detection, and
conditional hostile interactions.
"""

from backend.vecna.module import (
    VecnaModule,
    TriggerType,
    VecnaTrigger,
    VecnaResponse,
    corrupt_text
)
from backend.vecna.sentiment import SentimentAnalyzer, SentimentResult
from backend.vecna.pattern_detector import PatternDetector
from backend.vecna.gemini_service import GeminiService, GeminiServiceError
from backend.vecna.user_profile import UserProfile, UserProfileService

__all__ = [
    # Core module
    'VecnaModule',
    'TriggerType',
    'VecnaTrigger',
    'VecnaResponse',
    'corrupt_text',
    
    # Sentiment analysis
    'SentimentAnalyzer',
    'SentimentResult',
    
    # Pattern detection
    'PatternDetector',
    
    # Gemini service
    'GeminiService',
    'GeminiServiceError',
    
    # User profile
    'UserProfile',
    'UserProfileService',
]
