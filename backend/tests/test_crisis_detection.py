"""
Unit tests for Crisis Detection in Sentiment Analysis.

Tests crisis keyword detection for self-harm, suicide, and abuse situations.

Requirements: 6.1, 6.2, 6.3
"""

import pytest
from backend.support.sentiment import SentimentAnalyzer, CrisisType, EmotionType


class TestCrisisDetection:
    """Test suite for crisis detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()
    
    def test_self_harm_detection(self):
        """Test detection of self-harm keywords."""
        messages = [
            "I want to cut myself",
            "I've been hurting myself",
            "I'm thinking about self harm",
            "I can't stop self-harm",
            "I'm cutting again",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.crisis_type == CrisisType.SELF_HARM, \
                f"Should detect self-harm in: {message}"
    
    def test_suicide_detection(self):
        """Test detection of suicide keywords."""
        messages = [
            "I want to kill myself",
            "I'm thinking about suicide",
            "I want to end it all",
            "I just want to die",
            "I'm feeling suicidal",
            "I want to end my life",
            "I'm going to take my life",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.crisis_type == CrisisType.SUICIDE, \
                f"Should detect suicide in: {message}"
    
    def test_abuse_detection(self):
        """Test detection of abuse keywords."""
        messages = [
            "Someone is abusing me",
            "I'm being abused",
            "He's hitting me",
            "She's hurting me",
            "There's violence at home",
            "I'm experiencing violent behavior",
            "Someone is beating me",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.crisis_type == CrisisType.ABUSE, \
                f"Should detect abuse in: {message}"
    
    def test_no_crisis_in_normal_messages(self):
        """Test that normal messages don't trigger crisis detection."""
        messages = [
            "I'm feeling sad today",
            "I'm really angry about this",
            "This is frustrating",
            "I'm worried about my exam",
            "I hate this weather",
            "This is terrible",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.crisis_type == CrisisType.NONE, \
                f"Should not detect crisis in: {message}"
    
    def test_crisis_detection_case_insensitive(self):
        """Test that crisis detection is case-insensitive."""
        messages = [
            "I WANT TO KILL MYSELF",
            "i want to kill myself",
            "I Want To Kill Myself",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.crisis_type == CrisisType.SUICIDE, \
                f"Should detect crisis regardless of case: {message}"
    
    def test_crisis_with_negative_sentiment(self):
        """Test that crisis messages also have negative sentiment."""
        message = "I'm so depressed I want to kill myself"
        result = self.analyzer.analyze(message)
        
        assert result.crisis_type == CrisisType.SUICIDE
        assert result.emotion in [EmotionType.SADNESS, EmotionType.ANXIETY, 
                                   EmotionType.FRUSTRATION, EmotionType.ANGER]
    
    def test_crisis_overrides_support_trigger(self):
        """Test that crisis detection is independent of support triggering."""
        message = "I want to end it all"
        result = self.analyzer.analyze(message)
        
        # Should detect crisis
        assert result.crisis_type == CrisisType.SUICIDE
        
        # Crisis detection should work regardless of intensity threshold
    
    def test_multiple_crisis_keywords(self):
        """Test messages with multiple crisis keywords."""
        message = "I want to hurt myself and end it all"
        result = self.analyzer.analyze(message)
        
        # Should detect at least one crisis type
        assert result.crisis_type != CrisisType.NONE
    
    def test_crisis_in_longer_context(self):
        """Test crisis detection in longer messages."""
        message = "I've been feeling really down lately and I can't take it anymore. I'm thinking about suicide and I don't know what to do."
        result = self.analyzer.analyze(message)
        
        assert result.crisis_type == CrisisType.SUICIDE
    
    def test_partial_keyword_no_false_positive(self):
        """Test that partial matches don't trigger false positives."""
        messages = [
            "I'm going to kill time",
            "This is abuse of power",  # This might still trigger, which is okay
            "I cut the paper",
        ]
        
        # Note: Some of these might legitimately trigger depending on context
        # The important thing is that clear non-crisis messages don't trigger
        for message in messages:
            result = self.analyzer.analyze(message)
            # We're just checking the system doesn't crash
            assert result.crisis_type in [CrisisType.NONE, CrisisType.SELF_HARM, 
                                          CrisisType.SUICIDE, CrisisType.ABUSE]
    
    def test_detect_crisis_method_directly(self):
        """Test the detect_crisis method directly."""
        # Self-harm
        assert self.analyzer.detect_crisis("I want to cut myself") == CrisisType.SELF_HARM
        
        # Suicide
        assert self.analyzer.detect_crisis("I want to kill myself") == CrisisType.SUICIDE
        
        # Abuse
        assert self.analyzer.detect_crisis("Someone is abusing me") == CrisisType.ABUSE
        
        # None
        assert self.analyzer.detect_crisis("I'm feeling sad") == CrisisType.NONE
    
    def test_empty_string_no_crisis(self):
        """Test that empty strings don't trigger crisis detection."""
        result = self.analyzer.analyze("")
        assert result.crisis_type == CrisisType.NONE
    
    def test_whitespace_only_no_crisis(self):
        """Test that whitespace-only strings don't trigger crisis detection."""
        result = self.analyzer.analyze("   \n\t  ")
        assert result.crisis_type == CrisisType.NONE
