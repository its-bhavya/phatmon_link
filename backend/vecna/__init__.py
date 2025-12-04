"""
Vecna Module - Shared Services.

This module provides shared services for the Phantom Link BBS,
including Gemini AI service, sentiment analysis, and user profile tracking.
These services are used by SysOp Brain and will be used by the Support Bot.
"""

from backend.vecna.sentiment import SentimentAnalyzer, SentimentResult
from backend.vecna.gemini_service import GeminiService, GeminiServiceError
from backend.vecna.user_profile import UserProfile, UserProfileService

__all__ = [
    # Sentiment analysis
    'SentimentAnalyzer',
    'SentimentResult',
    
    # Gemini service
    'GeminiService',
    'GeminiServiceError',
    
    # User profile
    'UserProfile',
    'UserProfileService',
]
