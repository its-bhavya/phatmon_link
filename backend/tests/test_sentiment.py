"""
Unit tests for Sentiment Analysis Service.

Tests sentiment detection, intensity calculation, and trigger evaluation
for the Vecna Adversarial AI Module.
"""

import pytest
from backend.vecna.sentiment import SentimentAnalyzer, SentimentResult


class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer(intensity_threshold=0.7)
    
    def test_high_negative_sentiment_detection(self):
        """Test detection of high-intensity negative sentiment."""
        # High-intensity negative messages
        messages = [
            "I hate this terrible system",
            "This is the worst garbage I've ever seen",
            "Absolutely awful and useless",
            "I'm so frustrated with this broken stupid code",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.polarity < 0, f"Expected negative polarity for: {message}"
            assert result.intensity >= 0.7, f"Expected high intensity for: {message}"
            assert result.is_trigger, f"Expected trigger for: {message}"
            assert len(result.keywords) > 0, f"Expected keywords for: {message}"
    
    def test_neutral_sentiment_handling(self):
        """Test handling of neutral sentiment."""
        messages = [
            "Hello, how are you?",
            "I need help with this feature",
            "Can you explain this to me?",
            "What does this function do?",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert not result.is_trigger, f"Should not trigger for neutral: {message}"
            assert abs(result.polarity) < 0.5, f"Expected near-neutral polarity for: {message}"
    
    def test_positive_sentiment_handling(self):
        """Test handling of positive sentiment."""
        messages = [
            "This is great, thank you!",
            "I love this amazing feature",
            "Excellent work, very helpful",
            "Perfect, exactly what I needed",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert result.polarity > 0, f"Expected positive polarity for: {message}"
            assert not result.is_trigger, f"Should not trigger for positive: {message}"
    
    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        result = self.analyzer.analyze("")
        assert result.polarity == 0.0
        assert result.intensity == 0.0
        assert not result.is_trigger
        assert len(result.keywords) == 0
    
    def test_whitespace_only_handling(self):
        """Test handling of whitespace-only strings."""
        result = self.analyzer.analyze("   \n\t  ")
        assert result.polarity == 0.0
        assert result.intensity == 0.0
        assert not result.is_trigger
        assert len(result.keywords) == 0
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        messages = [
            "!@#$%^&*()",
            "...",
            "???",
            "---",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert not result.is_trigger, f"Should not trigger for special chars: {message}"
    
    def test_intensifier_amplification(self):
        """Test that intensifiers amplify sentiment."""
        # Without intensifier
        result_without = self.analyzer.analyze("This is bad")
        
        # With intensifier
        result_with = self.analyzer.analyze("This is very bad")
        
        # Intensified version should have higher intensity
        assert result_with.intensity > result_without.intensity
    
    def test_multiple_negative_keywords(self):
        """Test messages with multiple negative keywords."""
        message = "This terrible awful broken system is the worst"
        result = self.analyzer.analyze(message)
        
        assert result.polarity < 0
        assert result.is_trigger
        assert len(result.keywords) >= 3
    
    def test_mixed_sentiment(self):
        """Test messages with mixed positive and negative sentiment."""
        message = "This is great but also terrible"
        result = self.analyzer.analyze(message)
        
        # Should detect both positive and negative keywords
        # Polarity should be somewhere in between
        assert -1.0 <= result.polarity <= 1.0
    
    def test_threshold_boundary(self):
        """Test behavior at intensity threshold boundary."""
        # Create analyzer with specific threshold
        analyzer = SentimentAnalyzer(intensity_threshold=0.5)
        
        # Message that should be just above threshold
        result = analyzer.analyze("This is really bad and broken")
        
        if result.intensity >= 0.5:
            assert result.is_trigger
        else:
            assert not result.is_trigger
    
    def test_is_high_negative_intensity_convenience_method(self):
        """Test the convenience method for quick trigger checking."""
        # Should trigger
        assert self.analyzer.is_high_negative_intensity("I hate this terrible system")
        
        # Should not trigger
        assert not self.analyzer.is_high_negative_intensity("This is okay")
        assert not self.analyzer.is_high_negative_intensity("I love this")
    
    def test_case_insensitivity(self):
        """Test that analysis is case-insensitive."""
        messages = [
            "I HATE THIS",
            "i hate this",
            "I Hate This",
        ]
        
        results = [self.analyzer.analyze(msg) for msg in messages]
        
        # All should have similar results
        for result in results:
            assert result.is_trigger
            assert result.polarity < 0
    
    def test_keyword_detection(self):
        """Test that detected keywords are returned."""
        message = "This is terrible and awful"
        result = self.analyzer.analyze(message)
        
        assert "terrible" in result.keywords
        assert "awful" in result.keywords
    
    def test_intensity_normalization_by_length(self):
        """Test that intensity is normalized by message length."""
        # Short message with one negative word
        short_result = self.analyzer.analyze("hate")
        
        # Long message with one negative word
        long_result = self.analyzer.analyze(
            "I just wanted to say that I really hate this one particular thing"
        )
        
        # Short message should have higher intensity
        assert short_result.intensity > long_result.intensity
    
    def test_polarity_range(self):
        """Test that polarity is always in valid range."""
        messages = [
            "I hate this terrible awful garbage",
            "I love this amazing wonderful feature",
            "This is okay",
            "",
            "!@#$",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert -1.0 <= result.polarity <= 1.0, f"Invalid polarity for: {message}"
    
    def test_intensity_range(self):
        """Test that intensity is always in valid range."""
        messages = [
            "I hate this terrible awful garbage",
            "I love this amazing wonderful feature",
            "This is okay",
            "",
            "!@#$",
        ]
        
        for message in messages:
            result = self.analyzer.analyze(message)
            assert 0.0 <= result.intensity <= 1.0, f"Invalid intensity for: {message}"
    
    def test_custom_threshold(self):
        """Test analyzer with custom threshold."""
        # Low threshold - more sensitive
        sensitive_analyzer = SentimentAnalyzer(intensity_threshold=0.3)
        
        # High threshold - less sensitive
        strict_analyzer = SentimentAnalyzer(intensity_threshold=0.9)
        
        message = "This is bad"
        
        sensitive_result = sensitive_analyzer.analyze(message)
        strict_result = strict_analyzer.analyze(message)
        
        # Sensitive analyzer more likely to trigger
        if sensitive_result.intensity >= 0.3:
            assert sensitive_result.is_trigger
        if strict_result.intensity < 0.9:
            assert not strict_result.is_trigger
