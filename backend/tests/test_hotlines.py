"""
Unit tests for Crisis Hotline Service.

Tests hotline information retrieval and message formatting for crisis situations.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
from backend.support.hotlines import CrisisHotlineService, HotlineInfo
from backend.support.sentiment import CrisisType


class TestCrisisHotlineService:
    """Test suite for CrisisHotlineService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CrisisHotlineService()
    
    def test_get_hotlines_self_harm(self):
        """Test retrieval of self-harm hotlines."""
        hotlines = self.service.get_hotlines(CrisisType.SELF_HARM)
        
        assert len(hotlines) > 0, "Should return hotlines for self-harm"
        assert all(isinstance(h, HotlineInfo) for h in hotlines)
        
        # Check that AASRA is included (common for self-harm)
        hotline_names = [h.name for h in hotlines]
        assert "AASRA" in hotline_names
    
    def test_get_hotlines_suicide(self):
        """Test retrieval of suicide prevention hotlines."""
        hotlines = self.service.get_hotlines(CrisisType.SUICIDE)
        
        assert len(hotlines) > 0, "Should return hotlines for suicide"
        assert all(isinstance(h, HotlineInfo) for h in hotlines)
        
        # Check that suicide-specific hotlines are included
        hotline_names = [h.name for h in hotlines]
        assert any("Sneha" in name or "AASRA" in name for name in hotline_names)
    
    def test_get_hotlines_abuse(self):
        """Test retrieval of abuse hotlines."""
        hotlines = self.service.get_hotlines(CrisisType.ABUSE)
        
        assert len(hotlines) > 0, "Should return hotlines for abuse"
        assert all(isinstance(h, HotlineInfo) for h in hotlines)
        
        # Check that abuse-specific hotlines are included
        hotline_names = [h.name for h in hotlines]
        assert any("Women" in name or "Child" in name for name in hotline_names)
    
    def test_get_hotlines_none(self):
        """Test that no hotlines are returned for NONE crisis type."""
        hotlines = self.service.get_hotlines(CrisisType.NONE)
        
        assert len(hotlines) == 0, "Should return empty list for NONE crisis type"
    
    def test_hotline_info_structure(self):
        """Test that hotline info has required fields."""
        hotlines = self.service.get_hotlines(CrisisType.SELF_HARM)
        
        for hotline in hotlines:
            assert hotline.name, "Hotline should have a name"
            assert hotline.number, "Hotline should have a number"
            assert hotline.description, "Hotline should have a description"
    
    def test_format_hotline_message_self_harm(self):
        """Test formatting of self-harm crisis message."""
        message = self.service.format_hotline_message(CrisisType.SELF_HARM)
        
        assert message, "Should return non-empty message"
        assert "concerned" in message.lower(), "Should express concern"
        assert "professional" in message.lower(), "Should mention professionals"
        
        # Check that hotline numbers are included
        hotlines = self.service.get_hotlines(CrisisType.SELF_HARM)
        for hotline in hotlines:
            assert hotline.number in message, f"Should include {hotline.name} number"
    
    def test_format_hotline_message_suicide(self):
        """Test formatting of suicide crisis message."""
        message = self.service.format_hotline_message(CrisisType.SUICIDE)
        
        assert message, "Should return non-empty message"
        assert "concerned" in message.lower(), "Should express concern"
        assert "professional" in message.lower(), "Should mention professionals"
        
        # Check that hotline numbers are included
        hotlines = self.service.get_hotlines(CrisisType.SUICIDE)
        for hotline in hotlines:
            assert hotline.number in message, f"Should include {hotline.name} number"
    
    def test_format_hotline_message_abuse(self):
        """Test formatting of abuse crisis message."""
        message = self.service.format_hotline_message(CrisisType.ABUSE)
        
        assert message, "Should return non-empty message"
        assert "concerned" in message.lower() or "safety" in message.lower(), "Should express concern"
        assert "professional" in message.lower(), "Should mention professionals"
        
        # Check that hotline numbers are included
        hotlines = self.service.get_hotlines(CrisisType.ABUSE)
        for hotline in hotlines:
            assert hotline.number in message, f"Should include {hotline.name} number"
    
    def test_format_hotline_message_none(self):
        """Test that no message is returned for NONE crisis type."""
        message = self.service.format_hotline_message(CrisisType.NONE)
        
        assert message == "", "Should return empty string for NONE crisis type"
    
    def test_message_includes_encouragement(self):
        """Test that crisis messages include encouragement to seek help."""
        for crisis_type in [CrisisType.SELF_HARM, CrisisType.SUICIDE, CrisisType.ABUSE]:
            message = self.service.format_hotline_message(crisis_type)
            
            # Should include encouraging language
            encouraging_phrases = [
                "don't have to face this alone",
                "trained to help",
                "want to support you",
                "can help"
            ]
            
            assert any(phrase in message.lower() for phrase in encouraging_phrases), \
                f"Message should include encouragement for {crisis_type}"
    
    def test_message_formatting_clarity(self):
        """Test that messages are formatted clearly with service names and numbers."""
        message = self.service.format_hotline_message(CrisisType.SELF_HARM)
        
        # Should have bullet points or clear formatting
        assert "•" in message or "-" in message or "\n" in message, \
            "Message should have clear formatting"
        
        # Should include both name and number for each hotline
        hotlines = self.service.get_hotlines(CrisisType.SELF_HARM)
        for hotline in hotlines:
            assert hotline.name in message, f"Should include service name {hotline.name}"
            assert hotline.number in message, f"Should include number {hotline.number}"
    
    def test_indian_hotline_numbers(self):
        """Test that hotlines are Indian numbers."""
        for crisis_type in [CrisisType.SELF_HARM, CrisisType.SUICIDE, CrisisType.ABUSE]:
            hotlines = self.service.get_hotlines(crisis_type)
            
            for hotline in hotlines:
                # Indian numbers should have specific patterns
                # Either start with 91- or be short codes like 1091, 1098
                number = hotline.number
                is_indian = (
                    number.startswith("91-") or 
                    number.startswith("1860-") or
                    number.startswith("1091") or
                    number.startswith("1098") or
                    number.startswith("7827-")
                )
                assert is_indian, f"Number {number} should be an Indian hotline"
    
    def test_no_advice_beyond_hotlines(self):
        """Test that crisis messages don't include advice beyond hotline info."""
        for crisis_type in [CrisisType.SELF_HARM, CrisisType.SUICIDE, CrisisType.ABUSE]:
            message = self.service.format_hotline_message(crisis_type)
            
            # Should not include therapeutic advice
            inappropriate_phrases = [
                "try to",
                "you should",
                "just",
                "calm down",
                "think positive",
                "it will get better"
            ]
            
            message_lower = message.lower()
            for phrase in inappropriate_phrases:
                assert phrase not in message_lower, \
                    f"Message should not include advice like '{phrase}'"
    
    def test_all_crisis_types_have_hotlines(self):
        """Test that all crisis types (except NONE) have hotlines configured."""
        crisis_types = [CrisisType.SELF_HARM, CrisisType.SUICIDE, CrisisType.ABUSE]
        
        for crisis_type in crisis_types:
            hotlines = self.service.get_hotlines(crisis_type)
            assert len(hotlines) > 0, f"Should have hotlines for {crisis_type}"
            
            # Should have at least 2 hotlines for redundancy
            assert len(hotlines) >= 2, f"Should have multiple hotlines for {crisis_type}"
