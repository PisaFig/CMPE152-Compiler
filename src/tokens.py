"""
Token definitions for the Python subset compiler.
Defines all token types and their classifications.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Any

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    DEF = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **
    
    # Comparison operators
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS_THAN = auto()      # <
    LESS_EQUAL = auto()     # <=
    GREATER_THAN = auto()   # >
    GREATER_EQUAL = auto()  # >=
    
    # Assignment
    ASSIGN = auto()         # =
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COMMA = auto()          # ,
    COLON = auto()          # :
    
    # Special tokens
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    
    # Error token
    ERROR = auto()

@dataclass
class Token:
    """Represents a single token with its type, value, and position."""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"

# Keywords mapping
KEYWORDS = {
    'if': TokenType.IF,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'in': TokenType.IN,
    'def': TokenType.DEF,
    'return': TokenType.RETURN,
    'True': TokenType.TRUE,
    'False': TokenType.FALSE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
}

# Operator mappings
OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '**': TokenType.POWER,
    '==': TokenType.EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '<': TokenType.LESS_THAN,
    '<=': TokenType.LESS_EQUAL,
    '>': TokenType.GREATER_THAN,
    '>=': TokenType.GREATER_EQUAL,
    '=': TokenType.ASSIGN,
}

# Delimiter mappings
DELIMITERS = {
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
}