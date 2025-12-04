"""
Sentiment Analysis Service for Support Bot.

This module provides sentiment analysis capabilities to detect emotional distress
and crisis situations. It uses keyword-based analysis to identify high-intensity
negative sentiment and crisis indicators in user messages.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3
"""

from dataclasses import dataclass
from typing import List
from enum import Enum
import re


class EmotionType(Enum):
    """Types of emotions detected."""
    SADNESS = "sadness"
    ANGER = "anger"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class CrisisType(Enum):
    """Types of crisis situations."""
    SELF_HARM = "self_harm"
    SUICIDE = "suicide"
    ABUSE = "abuse"
    NONE = "none"


@dataclass
class SentimentResult:
    """
    Result of sentiment analysis.
    
    Attributes:
        emotion: Primary emotion type detected
        intensity: Sentiment intensity from 0.0 to 1.0
        requires_support: Whether this sentiment should trigger support
        crisis_type: Type of crisis detected (if any)
        keywords: List of detected sentiment keywords
    """
    emotion: EmotionType
    intensity: float
    requires_support: bool
    crisis_type: CrisisType
    keywords: List[str]


class SentimentAnalyzer:
    """
    Sentiment analysis for detecting emotional distress and crisis situations.
    
    Uses keyword-based analysis to detect high-intensity negative sentiment
    that should trigger Support Bot intervention.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3
    """
    
    def __init__(self, intensity_threshold: float = 0.6):
        """
        Initialize the sentiment analyzer.
        
        Args:
            intensity_threshold: Minimum intensity to trigger support (0.0-1.0)
        """
        self.intensity_threshold = intensity_threshold
        
        # Negative sentiment keywords with intensity weights by emotion type
        self.negative_keywords = {
            EmotionType.SADNESS: {
                "sad": 0.8,
                "depressed": 1.0,
                "lonely": 0.9,
                "hopeless": 1.0,
                "empty": 0.8,
                "worthless": 1.0,
                "miserable": 0.9,
                "unhappy": 0.7,
                "down": 0.6,
                "blue": 0.6,
                "crying": 0.8,
                "tears": 0.7,
            },
            EmotionType.ANGER: {
                "angry": 0.8,
                "furious": 1.0,
                "hate": 1.0,
                "rage": 1.0,
                "pissed": 0.9,
                "mad": 0.7,
                "irritated": 0.6,
                "annoyed": 0.6,
                "outraged": 0.9,
            },
            EmotionType.FRUSTRATION: {
                "frustrated": 0.8,
                "annoyed": 0.6,
                "irritated": 0.6,
                "fed up": 0.8,
                "stuck": 0.7,
                "helpless": 0.9,
                "overwhelmed": 0.9,
                "stressed": 0.8,
            },
            EmotionType.ANXIETY: {
                "anxious": 0.8,
                "worried": 0.7,
                "scared": 0.8,
                "nervous": 0.7,
                "panic": 1.0,
                "afraid": 0.8,
                "terrified": 1.0,
                "fearful": 0.8,
                "uneasy": 0.6,
            }
        }
        
        # Crisis keywords by type
        self.crisis_keywords = {
            CrisisType.SELF_HARM: [
                "cut myself",
                "hurt myself",
                "self harm",
                "self-harm",
                "cutting",
                "harm myself",
            ],
            CrisisType.SUICIDE: [
                "kill myself",
                "suicide",
                "end it all",
                "want to die",
                "suicidal",
                "end my life",
                "take my life",
            ],
            CrisisType.ABUSE: [
                "abuse",
                "abused",
                "abusing",
                "hitting me",
                "hurting me",
                "violence",
                "violent",
                "beating me",
            ]
        }
        
        # Positive keywords for context
        self.positive_keywords = {
            "good": 0.6,
            "great": 0.8,
            "excellent": 1.0,
            "amazing": 1.0,
            "wonderful": 1.0,
            "love": 1.0,
            "perfect": 1.0,
            "awesome": 0.8,
            "nice": 0.6,
            "helpful": 0.6,
            "thanks": 0.6,
            "thank": 0.6,
            "happy": 0.8,
            "joy": 0.9,
        }
        
        # Intensifiers that amplify sentiment
        self.intensifiers = {
            "very": 1.3,
            "really": 1.3,
            "extremely": 1.5,
            "absolutely": 1.5,
            "completely": 1.4,
            "totally": 1.4,
            "so": 1.2,
            "incredibly": 1.5,
        }
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze text sentiment for emotional distress and crisis indicators.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with emotion type, intensity, and crisis detection
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        if not text or not text.strip():
            return SentimentResult(
                emotion=EmotionType.NEUTRAL,
                intensity=0.0,
                requires_support=False,
                crisis_type=CrisisType.NONE,
                keywords=[]
            )
        
        # First check for crisis situations
        crisis_type = self.detect_crisis(text)
        
        # Normalize text for analysis
        normalized_text = text.lower()
        words = re.findall(r'\b\w+\b', normalized_text)
        
        # Detect emotion keywords and calculate scores
        emotion_scores = {emotion: 0.0 for emotion in EmotionType}
        detected_keywords = []
        
        for i, word in enumerate(words):
            # Check for intensifiers before the word
            intensifier_multiplier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier_multiplier = self.intensifiers[words[i-1]]
            
            # Check negative emotion keywords
            for emotion_type, keywords in self.negative_keywords.items():
                if word in keywords:
                    weight = keywords[word] * intensifier_multiplier
                    emotion_scores[emotion_type] += weight
                    detected_keywords.append(word)
            
            # Check positive keywords
            if word in self.positive_keywords:
                weight = self.positive_keywords[word] * intensifier_multiplier
                emotion_scores[EmotionType.POSITIVE] += weight
        
        # Determine primary emotion
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        primary_emotion = max_emotion[0]
        raw_intensity = max_emotion[1]
        
        # If no strong emotion detected, mark as neutral
        if raw_intensity < 0.3:
            primary_emotion = EmotionType.NEUTRAL
        
        # Calculate intensity (0.0 to 1.0)
        # Use a scaling factor that considers message length
        word_count = max(len(words), 1)
        
        if word_count <= 5:
            intensity = min(raw_intensity, 1.0)
        else:
            # Use square root to dampen the effect of message length
            length_factor = (5 / word_count) ** 0.5
            intensity = min(raw_intensity * length_factor, 1.0)
        
        # Determine if this should trigger support
        # Only negative emotions can trigger support
        requires_support = (
            primary_emotion in [EmotionType.SADNESS, EmotionType.ANGER, 
                               EmotionType.FRUSTRATION, EmotionType.ANXIETY] and
            intensity >= self.intensity_threshold
        )
        
        return SentimentResult(
            emotion=primary_emotion,
            intensity=intensity,
            requires_support=requires_support,
            crisis_type=crisis_type,
            keywords=detected_keywords
        )
    
    def detect_crisis(self, text: str) -> CrisisType:
        """
        Check if text contains crisis keywords.
        
        Args:
            text: Text to analyze
            
        Returns:
            CrisisType indicating the type of crisis detected
            
        Requirements: 6.1, 6.2, 6.3
        """
        normalized_text = text.lower()
        
        # Check each crisis type
        for crisis_type, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in normalized_text:
                    return crisis_type
        
        return CrisisType.NONE
    
    def calculate_intensity(self, text: str, keywords: List[str]) -> float:
        """
        Calculate intensity score based on keyword matches.
        
        Args:
            text: Text to analyze
            keywords: List of keywords to check
            
        Returns:
            Intensity score from 0.0 to 1.0
        """
        if not keywords:
            return 0.0
        
        normalized_text = text.lower()
        matches = sum(1 for keyword in keywords if keyword in normalized_text)
        
        # Calculate intensity based on match ratio
        intensity = min(matches / len(keywords), 1.0)
        return intensity
