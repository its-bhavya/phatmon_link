"""
Support Bot Module for Empathetic Support Bot.

This module provides emotional support functionality including:
- Sentiment analysis for detecting emotional distress
- Crisis detection and hotline information
- Empathetic AI bot for supportive conversations
- Support room management

Components:
- SupportBot: Main bot class for generating empathetic responses
- SentimentAnalyzer: Analyzes messages for emotional content
- CrisisHotlineService: Provides crisis hotline information
- SupportRoomService: Manages dedicated support rooms
"""

from backend.support.bot import SupportBot
from backend.support.sentiment import (
    SentimentAnalyzer,
    SentimentResult,
    EmotionType,
    CrisisType
)
from backend.support.hotlines import CrisisHotlineService, HotlineInfo
from backend.support.room_service import SupportRoomService

__all__ = [
    'SupportBot',
    'SentimentAnalyzer',
    'SentimentResult',
    'EmotionType',
    'CrisisType',
    'CrisisHotlineService',
    'HotlineInfo',
    'SupportRoomService'
]
