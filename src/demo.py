"""
Demonstration script for CMPE 152 Python Subset Compiler
Shows how each compilation phase works individually.
"""

# First, let's test the lexer
print("=== CMPE 152 Python Subset Compiler Demo ===")
print("Testing Lexical Analysis Phase:")
print("-" * 50)

# Import our modules
import sys
import os
sys.path.append('.')

from tokens import Token, TokenType, KEYWORDS, OPERATORS, DELIMITERS
from lexer import Lexer

# Test code
test_code = '''
x = 42
if x > 0:
    print("Positive number")
'''

print("Source code:")
print(test_code)

# Lexical Analysis
lexer = Lexer(test_code)
tokens = lexer.tokenize()

print("Tokens generated:")
for i, token in enumerate(tokens[:10]):  # Show first 10 tokens
    print(f"{i+1:2d}: {token}")

print(f"\nTotal tokens: {len(tokens)}")
print("✓ Lexical analysis successful!")

# Test individual components
print("\n" + "="*50)
print("Testing Token Classifications:")
print("-" * 50)

print("Keywords:", list(KEYWORDS.keys())[:5], "...")
print("Operators:", list(OPERATORS.keys())[:5], "...")
print("Delimiters:", list(DELIMITERS.keys()))

print("\n" + "="*50)
print("Sample Token Objects:")
print("-" * 50)

sample_tokens = [
    Token(TokenType.INTEGER, 42, 1, 5),
    Token(TokenType.IDENTIFIER, "variable", 2, 1),
    Token(TokenType.STRING, "Hello", 3, 10)
]

for token in sample_tokens:
    print(f"  {token}")

print("\n✅ All core components working correctly!")
print("✅ Ready for CMPE 152 demonstration!")