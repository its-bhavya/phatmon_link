"""
Demonstration of the text corruption algorithm.

This script shows examples of text corruption at various levels.
"""

from backend.vecna.module import corrupt_text


def demonstrate_corruption():
    """Demonstrate text corruption with various examples."""
    
    test_messages = [
        "Hello World",
        "Why can't you figure this out, human?",
        "This system is broken and terrible",
        "I need help with this feature",
        "The Archives hold many secrets",
    ]
    
    corruption_levels = [0.0, 0.2, 0.3, 0.5]
    
    print("=" * 80)
    print("TEXT CORRUPTION DEMONSTRATION")
    print("=" * 80)
    print()
    
    for message in test_messages:
        print(f"Original: {message}")
        print("-" * 80)
        
        for level in corruption_levels:
            corrupted = corrupt_text(message, level)
            print(f"  Level {level:.1f}: {corrupted}")
        
        print()
    
    print("=" * 80)
    print("EDGE CASES")
    print("=" * 80)
    print()
    
    edge_cases = [
        ("Empty string", ""),
        ("Whitespace only", "   \n\t  "),
        ("Punctuation only", "!@#$%^&*()"),
        ("Numbers", "123 456 789"),
        ("Single character", "a"),
        ("Mixed content", "Hello! 123 World?"),
    ]
    
    for name, text in edge_cases:
        corrupted = corrupt_text(text, 0.5)
        print(f"{name}:")
        print(f"  Original:  '{text}'")
        print(f"  Corrupted: '{corrupted}'")
        print()


if __name__ == "__main__":
    demonstrate_corruption()
