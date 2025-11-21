"""
Lexical Analyzer for Python Subset Compiler
Implements DFA-based token recognition with indentation handling.
"""

import re
import string
from typing import List, Optional, Iterator
from tokens import Token, TokenType, KEYWORDS, OPERATORS, DELIMITERS

class LexicalError(Exception):
    """Exception raised for lexical analysis errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")

class Lexer:
    """
    Lexical analyzer implementing DFA for token recognition.
    Handles Python's indentation-based syntax.
    """
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.indent_stack = [0]  # Stack to track indentation levels
        self.at_line_start = True
        
    def current_char(self) -> Optional[str]:
        """Get the current character or None if at end."""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character ahead by offset positions."""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Advance position and return current character."""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
            self.at_line_start = True
        else:
            self.column += 1
            
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def handle_indentation(self):
        """Handle Python's indentation-based syntax."""
        if not self.at_line_start:
            return
        
        # Count indentation level
        indent_level = 0
        while self.current_char() in ' \t':
            if self.current_char() == ' ':
                indent_level += 1
            else:  # tab
                indent_level += 8  # Treat tab as 8 spaces
            self.advance()
        
        # Skip empty lines and comment-only lines, but avoid infinite loops
        # Let the main tokenize loop handle the newline/comment characters.
        if self.current_char() in ['\n', '#', None]:
            self.at_line_start = False
            return
        
        self.at_line_start = False
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            # Increased indentation - INDENT token
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, indent_level, self.line, self.column))
        elif indent_level < current_indent:
            # Decreased indentation - may need multiple DEDENT tokens
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, indent_level, self.line, self.column))
            
            if not self.indent_stack or self.indent_stack[-1] != indent_level:
                raise LexicalError("Indentation error", self.line, self.column)
    
    def read_number(self) -> Token:
        """Read integer or float using DFA."""
        start_line, start_col = self.line, self.column
        num_str = ""
        is_float = False
        
        # State 0: Reading digits
        while self.current_char() and self.current_char().isdigit():
            num_str += self.advance()
        
        # State 1: Check for decimal point
        if self.current_char() == '.':
            is_float = True
            num_str += self.advance()
            
            # State 2: Reading decimal digits
            if not self.current_char() or not self.current_char().isdigit():
                raise LexicalError("Invalid float literal", start_line, start_col)
            
            while self.current_char() and self.current_char().isdigit():
                num_str += self.advance()
        
        # Convert to appropriate type
        if is_float:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_col)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_col)
    
    def read_string(self) -> Token:
        """Read string literal (single or double quotes)."""
        start_line, start_col = self.line, self.column
        quote_char = self.advance()  # Skip opening quote
        value = ""
        
        while self.current_char() and self.current_char() != quote_char:
            char = self.current_char()
            if char == '\\':
                # Handle escape sequences
                self.advance()
                next_char = self.current_char()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote_char:
                    value += quote_char
                else:
                    value += next_char
                self.advance()
            else:
                value += self.advance()
        
        if not self.current_char():
            raise LexicalError("Unterminated string", start_line, start_col)
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read identifier or keyword using DFA."""
        start_line, start_col = self.line, self.column
        value = ""
        
        # First character must be letter or underscore
        if self.current_char().isalpha() or self.current_char() == '_':
            value += self.advance()
        
        # Subsequent characters can be letters, digits, or underscores
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            value += self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
        
        # Handle boolean literals
        if token_type == TokenType.TRUE:
            return Token(TokenType.BOOLEAN, True, start_line, start_col)
        elif token_type == TokenType.FALSE:
            return Token(TokenType.BOOLEAN, False, start_line, start_col)
        
        return Token(token_type, value, start_line, start_col)
    
    def read_operator(self) -> Token:
        """Read operator tokens (handles multi-character operators)."""
        start_line, start_col = self.line, self.column
        char = self.current_char()
        
        # Check for two-character operators first
        if char in ['*', '=', '!', '<', '>']:
            next_char = self.peek_char()
            two_char = char + (next_char or '')
            
            if two_char in OPERATORS:
                self.advance()  # First char
                self.advance()  # Second char
                return Token(OPERATORS[two_char], two_char, start_line, start_col)
        
        # Single character operator
        if char in OPERATORS:
            self.advance()
            return Token(OPERATORS[char], char, start_line, start_col)
        
        raise LexicalError(f"Unknown operator: {char}", start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """
        Main tokenization method implementing the lexical analyzer.
        Returns list of tokens with proper indentation handling.
        """
        self.tokens = []
        
        while self.position < len(self.source):
            # Handle indentation at start of line
            if self.at_line_start:
                self.handle_indentation()
                continue
            
            char = self.current_char()
            
            if char is None:
                break
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
            elif char in ' \t\r':
                self.skip_whitespace()
            elif char == '#':
                # Skip comments
                while self.current_char() and self.current_char() != '\n':
                    self.advance()
            elif char.isdigit():
                self.tokens.append(self.read_number())
            elif char in ['"', "'"]:
                self.tokens.append(self.read_string())
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            elif char in DELIMITERS:
                self.tokens.append(Token(DELIMITERS[char], char, self.line, self.column))
                self.advance()
            elif char in OPERATORS or char in ['*', '=', '!', '<', '>']:
                self.tokens.append(self.read_operator())
            else:
                raise LexicalError(f"Unexpected character: {char}", self.line, self.column)
        
        # Add remaining DEDENT tokens
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, 0, self.line, self.column))
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def print_tokens(self):
        """Print all tokens for debugging."""
        print("=" * 60)
        print("LEXICAL ANALYSIS RESULTS")
        print("=" * 60)
        print(f"{'Token Type':<15} {'Value':<15} {'Line':<6} {'Column':<6}")
        print("-" * 60)
        
        for token in self.tokens:
            print(f"{token.type.name:<15} {str(token.value):<15} {token.line:<6} {token.column:<6}")
        
        print("=" * 60)
        print(f"Total tokens: {len(self.tokens)}")

if __name__ == "__main__":
    # Test the lexer
    test_code = '''
x = 42
if x > 0:
    print("Positive")
    y = x * 2
else:
    print("Non-positive")
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    lexer.print_tokens()