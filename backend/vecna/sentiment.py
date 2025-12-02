"""
Sentiment Analysis Service for Vecna Adversarial AI Module.

This module provides sentiment analysis capabilities to detect emotional triggers
for Vecna activation. It uses keyword-based analysis to identify high-intensity
negative sentiment in user messages.
"""

from dataclasses import dataclass
from typing import List
import re


@dataclass
class SentimentResult:
    """
    Result of sentiment analysis.
    
    Attributes:
        polarity: Sentiment polarity from -1.0 (negative) to 1.0 (positive)
        intensity: Sentiment intensity from 0.0 to 1.0
        is_trigger: Whether this sentiment should trigger Vecna
        keywords: List of detected sentiment keywords
    """
    polarity: float
    intensity: float
    is_trigger: bool
    keywords: List[str]


class SentimentAnalyzer:
    """
    Sentiment analysis for detecting emotional triggers.
    
    Uses keyword-based analysis to detect high-intensity negative sentiment
    that should trigger Vecna's emotional response mode.
    """
    
    def __init__(self, intensity_threshold: float = 0.7):
        """
        Initialize the sentiment analyzer.
        
        Args:
            intensity_threshold: Minimum intensity to trigger Vecna (0.0-1.0)
        """
        self.intensity_threshold = intensity_threshold
        
        # Negative sentiment keywords with intensity weights
        self.negative_keywords = {
            # High intensity (1.0)
            "hate": 1.0,
            "worst": 1.0,
            "terrible": 1.0,
            "awful": 1.0,
            "horrible": 1.0,
            "disgusting": 1.0,
            "pathetic": 1.0,
            "useless": 1.0,
            "garbage": 1.0,
            "trash": 1.0,
            
            # Medium-high intensity (0.8)
            "angry": 0.8,
            "frustrated": 0.8,
            "annoyed": 0.8,
            "broken": 0.8,
            "stupid": 0.8,
            "dumb": 0.8,
            "fail": 0.8,
            "failed": 0.8,
            "failing": 0.8,
            "sucks": 0.8,
            
            # Medium intensity (0.6)
            "bad": 0.6,
            "wrong": 0.6,
            "error": 0.6,
            "problem": 0.6,
            "issue": 0.6,
            "difficult": 0.6,
            "hard": 0.6,
            "confusing": 0.6,
            "confused": 0.6,
            "lost": 0.6,
        }
        
        # Positive keywords for polarity calculation
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
        Analyze text sentiment.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with polarity, intensity, and trigger status
        """
        if not text or not text.strip():
            return SentimentResult(
                polarity=0.0,
                intensity=0.0,
                is_trigger=False,
                keywords=[]
            )
        
        # Normalize text for analysis
        normalized_text = text.lower()
        words = re.findall(r'\b\w+\b', normalized_text)
        
        # Detect keywords and calculate sentiment
        negative_score = 0.0
        positive_score = 0.0
        detected_keywords = []
        
        for i, word in enumerate(words):
            # Check for intensifiers before the word
            intensifier_multiplier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier_multiplier = self.intensifiers[words[i-1]]
            
            # Check negative keywords
            if word in self.negative_keywords:
                weight = self.negative_keywords[word] * intensifier_multiplier
                negative_score += weight
                detected_keywords.append(word)
            
            # Check positive keywords
            elif word in self.positive_keywords:
                weight = self.positive_keywords[word] * intensifier_multiplier
                positive_score += weight
        
        # Calculate polarity (-1.0 to 1.0)
        total_score = negative_score + positive_score
        if total_score > 0:
            polarity = (positive_score - negative_score) / total_score
        else:
            polarity = 0.0
        
        # Calculate intensity (0.0 to 1.0)
        # Use a logarithmic scale to balance short and long messages
        # This allows multiple keywords to accumulate intensity
        word_count = max(len(words), 1)
        raw_intensity = max(negative_score, positive_score)
        
        # Apply a scaling factor that considers message length
        # Short messages get full intensity, longer messages get diminishing returns
        if word_count <= 5:
            intensity = min(raw_intensity, 1.0)
        else:
            # Use square root to dampen the effect of message length
            length_factor = (5 / word_count) ** 0.5
            intensity = min(raw_intensity * length_factor, 1.0)
        
        # Determine if this should trigger Vecna
        # Only negative sentiment can trigger
        is_trigger = (
            polarity < 0 and 
            intensity >= self.intensity_threshold
        )
        
        return SentimentResult(
            polarity=polarity,
            intensity=intensity,
            is_trigger=is_trigger,
            keywords=detected_keywords
        )
    
    def is_high_negative_intensity(self, text: str) -> bool:
        """
        Check if text contains high-intensity negative sentiment.
        
        This is a convenience method for quick trigger checking.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text should trigger Vecna emotional response
        """
        result = self.analyze(text)
        return result.is_trigger
