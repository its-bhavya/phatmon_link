"""
Tests for sentiment analysis error handling.

This module tests that the sentiment analyzer handles errors gracefully
and returns neutral sentiment on failure.

Requirements: 1.1
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.support.sentiment import SentimentAnalyzer, EmotionType, CrisisType


class TestSentimentErrorHandling:
    """Test error handling in sentiment analysis."""
    
    def test_analyze_handles_regex_error_gracefully(self):
        """Test that analyze returns neutral sentiment when regex fails."""
        analyzer = SentimentAnalyzer()
        
        # Mock re.findall to raise an exception
        with patch('backend.support.sentiment.re.findall', side_effect=Exception("Regex error")):
            result = analyzer.analyze("This should fail")
            
            # Should return neutral sentiment
            assert result.emotion == EmotionType.NEUTRAL
            assert result.intensity == 0.0
            assert result.requires_support is False
            assert result.crisis_type == CrisisType.NONE
            assert result.keywords == []
    
    def test_analyze_handles_none_input(self):
        """Test that analyze handles None input gracefully."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze(None)
        
        # Should return neutral sentiment
        assert result.emotion == EmotionType.NEUTRAL
        assert result.intensity == 0.0
        assert result.requires_support is False
        assert result.crisis_type == CrisisType.NONE
        assert result.keywords == []
    
    def test_analyze_handles_empty_string(self):
        """Test that analyze handles empty string gracefully."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("")
        
        # Should return neutral sentiment
        assert result.emotion == EmotionType.NEUTRAL
        assert result.intensity == 0.0
        assert result.requires_support is False
        assert result.crisis_type == CrisisType.NONE
        assert result.keywords == []
    
    def test_detect_crisis_handles_error_gracefully(self):
        """Test that detect_crisis returns NONE when error occurs."""
        analyzer = SentimentAnalyzer()
        
        # Mock the crisis_keywords to raise an exception
        with patch.object(analyzer, 'crisis_keywords', side_effect=Exception("Crisis detection error")):
            result = analyzer.detect_crisis("This should fail")
            
            # Should return no crisis
            assert result == CrisisType.NONE
    
    def test_detect_crisis_handles_none_input(self):
        """Test that detect_crisis handles None input gracefully."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.detect_crisis(None)
        
        # Should return no crisis
        assert result == CrisisType.NONE
    
    def test_analyze_continues_after_crisis_detection_error(self):
        """Test that analyze continues even if crisis detection fails."""
        analyzer = SentimentAnalyzer()
        
        # Mock detect_crisis to raise an exception
        with patch.object(analyzer, 'detect_crisis', side_effect=Exception("Crisis detection error")):
            # This should still work because the exception is caught
            result = analyzer.analyze("I am sad")
            
            # Should return neutral sentiment due to error
            assert result.emotion == EmotionType.NEUTRAL
            assert result.intensity == 0.0
            assert result.requires_support is False
    
    def test_analyze_handles_malformed_keywords_dict(self):
        """Test that analyze handles malformed keyword dictionaries."""
        analyzer = SentimentAnalyzer()
        
        # Replace keywords with something that will cause an error
        original_keywords = analyzer.negative_keywords
        analyzer.negative_keywords = "not a dict"
        
        result = analyzer.analyze("I am sad")
        
        # Should return neutral sentiment
        assert result.emotion == EmotionType.NEUTRAL
        assert result.intensity == 0.0
        assert result.requires_support is False
        
        # Restore original keywords
        analyzer.negative_keywords = original_keywords
    
    def test_analyze_logs_error_on_failure(self, caplog):
        """Test that analyze logs errors when they occur."""
        analyzer = SentimentAnalyzer()
        
        # Mock re.findall to raise an exception
        with patch('backend.support.sentiment.re.findall', side_effect=Exception("Test error")):
            result = analyzer.analyze("This should fail")
            
            # Should log the error
            assert "Sentiment analysis error" in caplog.text
            assert "Test error" in caplog.text
    
    def test_detect_crisis_logs_error_on_failure(self, caplog):
        """Test that detect_crisis logs errors when they occur."""
        import logging
        caplog.set_level(logging.ERROR)
        
        analyzer = SentimentAnalyzer()
        
        # Mock the items() method to raise an exception
        original_keywords = analyzer.crisis_keywords
        mock_dict = MagicMock()
        mock_dict.items.side_effect = Exception("Test crisis error")
        analyzer.crisis_keywords = mock_dict
        
        result = analyzer.detect_crisis("This should fail")
        
        # Should log the error
        assert "Crisis detection error" in caplog.text
        assert "Test crisis error" in caplog.text
        
        # Restore original
        analyzer.crisis_keywords = original_keywords
