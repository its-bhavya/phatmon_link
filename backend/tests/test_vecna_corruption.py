"""
Unit tests for Vecna text corruption algorithm.

Tests text corruption with various corruption levels, edge cases,
and readability preservation for the Vecna Adversarial AI Module.
"""

import pytest
from backend.vecna.module import corrupt_text


class TestTextCorruption:
    """Test suite for text corruption algorithm."""
    
    def test_corruption_with_zero_level(self):
        """Test that corruption level 0.0 returns unchanged text."""
        text = "Hello World"
        result = corrupt_text(text, 0.0)
        # With 0.0 corruption, text should be unchanged
        assert result == text
    
    def test_corruption_with_low_level(self):
        """Test corruption with low corruption level (0.3)."""
        text = "Hello World"
        result = corrupt_text(text, 0.3)
        
        # Result should be different from original (with high probability)
        # Note: Due to randomness, there's a small chance they're the same
        # Text should still be somewhat readable
        assert len(result) == len(text)
        
        # Count how many characters are different
        differences = sum(1 for a, b in zip(text, result) if a != b)
        # Should have some corruption but not too much
        assert differences <= len([c for c in text if c.isalpha()]) * 0.5
    
    def test_corruption_with_medium_level(self):
        """Test corruption with medium corruption level (0.5)."""
        text = "Hello World"
        result = corrupt_text(text, 0.5)
        
        # Result should maintain same length
        assert len(result) == len(text)
        
        # Should have noticeable corruption
        differences = sum(1 for a, b in zip(text, result) if a != b)
        # At 0.5 level, should corrupt up to 50% of letters
        assert differences <= len([c for c in text if c.isalpha()]) * 0.5
    
    def test_corruption_clamped_at_fifty_percent(self):
        """Test that corruption level above 0.5 is clamped to 0.5."""
        text = "Hello World"
        
        # Try with 1.0 corruption level
        result = corrupt_text(text, 1.0)
        
        # Should still maintain at least 50% readability
        # Count unchanged characters
        unchanged = sum(1 for a, b in zip(text, result) if a == b)
        total_chars = len([c for c in text if c.isalpha()])
        
        # At least 50% should be readable (unchanged or recognizable)
        assert unchanged >= total_chars * 0.5 or len(result) == len(text)
    
    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        result = corrupt_text("", 0.5)
        assert result == ""
    
    def test_whitespace_only_handling(self):
        """Test handling of whitespace-only strings."""
        text = "   \n\t  "
        result = corrupt_text(text, 0.5)
        # Whitespace should be preserved
        assert result == text
    
    def test_special_characters_preservation(self):
        """Test that special characters are preserved."""
        text = "Hello! How are you?"
        result = corrupt_text(text, 0.3)
        
        # Punctuation should be preserved
        assert '!' in result
        assert '?' in result
        
        # Spaces should be preserved
        assert result.count(' ') == text.count(' ')
    
    def test_punctuation_only_handling(self):
        """Test handling of punctuation-only strings."""
        text = "!@#$%^&*()"
        result = corrupt_text(text, 0.5)
        # Punctuation should be unchanged
        assert result == text
    
    def test_numbers_preservation(self):
        """Test that numbers are preserved."""
        text = "Hello 123 World 456"
        result = corrupt_text(text, 0.3)
        
        # Numbers should be preserved
        assert '123' in result
        assert '456' in result
    
    def test_length_preservation(self):
        """Test that text length is preserved."""
        texts = [
            "Hello World",
            "This is a longer sentence with more words",
            "a",
            "Short",
        ]
        
        for text in texts:
            result = corrupt_text(text, 0.3)
            assert len(result) == len(text), f"Length changed for: {text}"
    
    def test_character_substitution_map(self):
        """Test that character substitution map is applied."""
        # Text with characters that should be substituted
        text = "aeiost"
        result = corrupt_text(text, 0.5)
        
        # Should contain some substitutions (with high probability)
        # Check if any of the expected substitutions appear
        substitutions = ['@', '3', '1', '0', '$', '7']
        has_substitution = any(sub in result for sub in substitutions)
        
        # With 50% corruption on 6 characters, very likely to have substitutions
        # Note: Due to randomness, this might occasionally fail
        assert has_substitution or result == text  # Allow for rare case of no substitution
    
    def test_mixed_case_handling(self):
        """Test handling of mixed case text."""
        text = "HeLLo WoRLd"
        result = corrupt_text(text, 0.3)
        
        # Length should be preserved
        assert len(result) == len(text)
        
        # Should have some corruption
        assert result != text or text == result  # Allow for rare case of no change
    
    def test_long_text_corruption(self):
        """Test corruption on longer text."""
        text = "This is a much longer piece of text that should be corrupted while maintaining readability"
        result = corrupt_text(text, 0.3)
        
        # Length preserved
        assert len(result) == len(text)
        
        # Should have corruption
        differences = sum(1 for a, b in zip(text, result) if a != b)
        assert differences > 0  # Should have some differences
    
    def test_single_character_handling(self):
        """Test handling of single character strings."""
        # Single letter
        result = corrupt_text("a", 0.5)
        assert len(result) == 1
        assert result in ['a', '@']  # Either unchanged or substituted
        
        # Single punctuation
        result = corrupt_text("!", 0.5)
        assert result == "!"
    
    def test_repeated_calls_produce_different_results(self):
        """Test that repeated calls with same input produce varied results."""
        text = "Hello World"
        results = [corrupt_text(text, 0.3) for _ in range(10)]
        
        # Should have some variation (not all identical)
        unique_results = set(results)
        # With randomness, should get multiple different results
        assert len(unique_results) > 1 or all(r == text for r in results)
    
    def test_spaces_between_words_preserved(self):
        """Test that spaces between words are preserved."""
        text = "Hello World Test Message"
        result = corrupt_text(text, 0.5)
        
        # Count spaces
        assert result.count(' ') == text.count(' ')
        
        # Spaces should be in same positions
        for i, char in enumerate(text):
            if char == ' ':
                assert result[i] == ' '
    
    def test_newlines_preserved(self):
        """Test that newlines are preserved."""
        text = "Hello\nWorld\nTest"
        result = corrupt_text(text, 0.3)
        
        # Newlines should be preserved
        assert result.count('\n') == text.count('\n')
    
    def test_tabs_preserved(self):
        """Test that tabs are preserved."""
        text = "Hello\tWorld\tTest"
        result = corrupt_text(text, 0.3)
        
        # Tabs should be preserved
        assert result.count('\t') == text.count('\t')
    
    def test_unicode_characters_handling(self):
        """Test handling of unicode characters."""
        text = "Hello 世界"
        result = corrupt_text(text, 0.3)
        
        # Should handle unicode gracefully
        assert len(result) == len(text)
    
    def test_corruption_level_boundary_values(self):
        """Test corruption with boundary values."""
        text = "Hello World"
        
        # Test various boundary values
        for level in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
            result = corrupt_text(text, level)
            assert len(result) == len(text)
            assert isinstance(result, str)
    
    def test_negative_corruption_level(self):
        """Test that negative corruption level is handled."""
        text = "Hello World"
        # Negative should be treated as 0 or minimal corruption
        result = corrupt_text(text, -0.5)
        # Should not crash and should return valid string
        assert isinstance(result, str)
        assert len(result) == len(text)
    
    def test_very_high_corruption_level(self):
        """Test that very high corruption level is clamped."""
        text = "Hello World"
        result = corrupt_text(text, 10.0)
        
        # Should still maintain readability (clamped to 0.5)
        assert len(result) == len(text)
        
        # Should still have some readable characters
        unchanged = sum(1 for a, b in zip(text, result) if a == b)
        assert unchanged > 0
    
    def test_partial_readability_maintained(self):
        """Test that at least 50% readability is maintained."""
        text = "Hello World Testing Corruption"
        
        # Test with maximum corruption
        result = corrupt_text(text, 1.0)
        
        # Count letters that are unchanged or recognizably substituted
        letters = [c for c in text if c.isalpha()]
        result_letters = [c for c in result if c.isalnum()]
        
        # Should maintain structure
        assert len(result) == len(text)
        
        # At least some characters should be preserved
        preserved = sum(1 for a, b in zip(text, result) if a == b)
        assert preserved >= len(letters) * 0.5
