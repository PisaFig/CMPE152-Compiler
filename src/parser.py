"""
Recursive Descent Parser for Python Subset Compiler
Implements Context-Free Grammar with error recovery and AST generation.
"""

from typing import List, Optional, Union
from tokens import Token, TokenType
from ast_nodes import *

class ParseError(Exception):
    """Exception raised for parsing errors."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        self.line = token.line
        self.column = token.column
        super().__init__(f"Line {token.line}, Column {token.column}: {message}")

class Parser:
    """
    Recursive descent parser implementing the following CFG for Python subset:
    
    program         → statement_list EOF
    statement_list  → statement (NEWLINE statement)*
    statement       → assignment | if_stmt | while_stmt | for_stmt | 
                      function_def | return_stmt | expression_stmt
    
    assignment      → IDENTIFIER ASSIGN expression
    if_stmt         → IF expression COLON NEWLINE INDENT statement_list DEDENT
                      (ELIF expression COLON NEWLINE INDENT statement_list DEDENT)*
                      (ELSE COLON NEWLINE INDENT statement_list DEDENT)?
    while_stmt      → WHILE expression COLON NEWLINE INDENT statement_list DEDENT
    for_stmt        → FOR IDENTIFIER IN expression COLON NEWLINE INDENT statement_list DEDENT
    function_def    → DEF IDENTIFIER LPAREN parameter_list? RPAREN COLON NEWLINE 
                      INDENT statement_list DEDENT
    return_stmt     → RETURN expression?
    expression_stmt → expression
    
    expression      → logical_or
    logical_or      → logical_and (OR logical_and)*
    logical_and     → equality (AND equality)*
    equality        → comparison ((EQUAL | NOT_EQUAL) comparison)*
    comparison      → term ((LESS_THAN | LESS_EQUAL | GREATER_THAN | GREATER_EQUAL) term)*
    term            → factor ((PLUS | MINUS) factor)*
    factor          → unary ((MULTIPLY | DIVIDE | MODULO) unary)*
    unary           → (NOT | MINUS | PLUS) unary | power
    power           → primary (POWER primary)*
    primary         → literal | IDENTIFIER | function_call | list_expr | 
                      LPAREN expression RPAREN | index_expr
    
    function_call   → IDENTIFIER LPAREN argument_list? RPAREN
    list_expr       → LBRACKET (expression (COMMA expression)*)? RBRACKET
    index_expr      → primary LBRACKET expression RBRACKET
    
    parameter_list  → IDENTIFIER (COMMA IDENTIFIER)*
    argument_list   → expression (COMMA expression)*
    literal         → INTEGER | FLOAT | STRING | BOOLEAN
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        
    def current_token(self) -> Token:
        """Get the current token."""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Peek at token ahead by offset."""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consume token of expected type or raise error."""
        if self.match(token_type):
            return self.advance()
        
        if message is None:
            message = f"Expected {token_type.name}"
        
        error = ParseError(message, self.current_token())
        self.errors.append(error)
        raise error
    
    def skip_newlines(self):
        """Skip optional newline tokens."""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def synchronize(self):
        """Error recovery: skip to next statement boundary."""
        self.advance()
        
        while not self.match(TokenType.EOF):
            if self.tokens[self.current - 1].type == TokenType.NEWLINE:
                return
            
            if self.match(TokenType.IF, TokenType.WHILE, TokenType.FOR, 
                         TokenType.DEF, TokenType.RETURN):
                return
            
            self.advance()
    
    def parse(self) -> Optional[ProgramNode]:
        """Main parsing method - returns AST root or None if errors."""
        try:
            return self.program()
        except ParseError:
            return None
    
    def program(self) -> ProgramNode:
        """Parse the entire program."""
        statements = []
        self.skip_newlines()
        
        # Safety counter to prevent infinite loops
        max_iterations = len(self.tokens) * 2
        iteration_count = 0
        last_position = -1
        
        while not self.match(TokenType.EOF):
            iteration_count += 1
            
            # Prevent infinite loop - if we're stuck at same position
            if self.current == last_position:
                # Force advance to prevent infinite loop
                self.advance()
                continue
            
            if iteration_count > max_iterations:
                error = ParseError(f"Parser stuck in infinite loop", self.current_token())
                self.errors.append(error)
                break
            
            last_position = self.current
            
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
                self.skip_newlines()
            except ParseError as e:
                self.errors.append(e)
                self.synchronize()
        
        return ProgramNode(statements)
    
    def statement(self) -> Optional[StatementNode]:
        """Parse a single statement."""
        try:
            if self.match(TokenType.IDENTIFIER) and self.peek_token().type == TokenType.ASSIGN:
                return self.assignment()
            elif self.match(TokenType.IF):
                return self.if_statement()
            elif self.match(TokenType.WHILE):
                return self.while_statement()
            elif self.match(TokenType.FOR):
                return self.for_statement()
            elif self.match(TokenType.DEF):
                return self.function_definition()
            elif self.match(TokenType.RETURN):
                return self.return_statement()
            else:
                return self.expression_statement()
        except ParseError:
            return None
    
    def assignment(self) -> AssignmentNode:
        """Parse assignment statement: IDENTIFIER = expression"""
        token = self.consume(TokenType.IDENTIFIER)
        variable = token.value
        self.consume(TokenType.ASSIGN)
        expression = self.expression()
        
        return AssignmentNode(variable, expression, token.line, token.column)
    
    def if_statement(self) -> IfNode:
        """Parse if statement with elif and else clauses."""
        if_token = self.consume(TokenType.IF)
        condition = self.expression()
        self.consume(TokenType.COLON)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        
        then_body = self.statement_block()
        self.consume(TokenType.DEDENT)
        
        elif_clauses = []
        while self.match(TokenType.ELIF):
            self.advance()  # consume ELIF
            elif_condition = self.expression()
            self.consume(TokenType.COLON)
            self.consume(TokenType.NEWLINE)
            self.consume(TokenType.INDENT)
            elif_body = self.statement_block()
            self.consume(TokenType.DEDENT)
            elif_clauses.append((elif_condition, elif_body))
        
        else_body = []
        if self.match(TokenType.ELSE):
            self.advance()  # consume ELSE
            self.consume(TokenType.COLON)
            self.consume(TokenType.NEWLINE)
            self.consume(TokenType.INDENT)
            else_body = self.statement_block()
            self.consume(TokenType.DEDENT)
        
        return IfNode(condition, then_body, elif_clauses, else_body, 
                     if_token.line, if_token.column)
    
    def while_statement(self) -> WhileNode:
        """Parse while statement."""
        while_token = self.consume(TokenType.WHILE)
        condition = self.expression()
        self.consume(TokenType.COLON)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = self.statement_block()
        self.consume(TokenType.DEDENT)
        
        return WhileNode(condition, body, while_token.line, while_token.column)
    
    def for_statement(self) -> ForNode:
        """Parse for statement."""
        for_token = self.consume(TokenType.FOR)
        variable_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.IN)
        iterable = self.expression()
        self.consume(TokenType.COLON)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = self.statement_block()
        self.consume(TokenType.DEDENT)
        
        return ForNode(variable_token.value, iterable, body, 
                      for_token.line, for_token.column)
    
    def function_definition(self) -> FunctionDefNode:
        """Parse function definition."""
        def_token = self.consume(TokenType.DEF)
        name_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LPAREN)
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()  # consume comma
                parameters.append(self.consume(TokenType.IDENTIFIER).value)
        
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.COLON)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = self.statement_block()
        self.consume(TokenType.DEDENT)
        
        return FunctionDefNode(name_token.value, parameters, body,
                              def_token.line, def_token.column)
    
    def return_statement(self) -> ReturnNode:
        """Parse return statement."""
        return_token = self.consume(TokenType.RETURN)
        expression = None
        
        if not self.match(TokenType.NEWLINE, TokenType.EOF):
            expression = self.expression()
        
        return ReturnNode(expression, return_token.line, return_token.column)
    
    def expression_statement(self) -> ExpressionStatementNode:
        """Parse expression statement."""
        expr = self.expression()
        return ExpressionStatementNode(expr, expr.line, expr.column)
    
    def statement_block(self) -> List[StatementNode]:
        """Parse a block of statements (used in if, while, for, functions)."""
        statements = []
        
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.DEDENT, TokenType.EOF):
                break
            
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return statements
    
    # Expression parsing with operator precedence
    def expression(self) -> ExpressionNode:
        """Parse expression (lowest precedence)."""
        return self.logical_or()
    
    def logical_or(self) -> ExpressionNode:
        """Parse logical OR expressions."""
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator = self.advance().type
            right = self.logical_and()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def logical_and(self) -> ExpressionNode:
        """Parse logical AND expressions."""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.advance().type
            right = self.equality()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def equality(self) -> ExpressionNode:
        """Parse equality expressions."""
        expr = self.comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.advance().type
            right = self.comparison()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def comparison(self) -> ExpressionNode:
        """Parse comparison expressions."""
        expr = self.term()
        
        while self.match(TokenType.LESS_THAN, TokenType.LESS_EQUAL,
                         TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            operator = self.advance().type
            right = self.term()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def term(self) -> ExpressionNode:
        """Parse addition and subtraction."""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().type
            right = self.factor()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def factor(self) -> ExpressionNode:
        """Parse multiplication, division, and modulo."""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().type
            right = self.unary()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def unary(self) -> ExpressionNode:
        """Parse unary expressions."""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            operator = self.advance().type
            expr = self.unary()
            return UnaryOpNode(operator, expr, expr.line, expr.column)
        
        return self.power()
    
    def power(self) -> ExpressionNode:
        """Parse power expressions (right associative)."""
        expr = self.primary()
        
        if self.match(TokenType.POWER):
            operator = self.advance().type
            right = self.power()  # Right associative
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)
        
        return expr
    
    def primary(self) -> ExpressionNode:
        """Parse primary expressions."""
        token = self.current_token()
        
        # Literals
        if self.match(TokenType.INTEGER):
            self.advance()
            return LiteralNode(token.value, TokenType.INTEGER, token.line, token.column)
        
        if self.match(TokenType.FLOAT):
            self.advance()
            return LiteralNode(token.value, TokenType.FLOAT, token.line, token.column)
        
        if self.match(TokenType.STRING):
            self.advance()
            return LiteralNode(token.value, TokenType.STRING, token.line, token.column)
        
        if self.match(TokenType.BOOLEAN):
            self.advance()
            return LiteralNode(token.value, TokenType.BOOLEAN, token.line, token.column)
        
        # Identifier or function call
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()  # consume LPAREN
                arguments = []
                
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.expression())
                    while self.match(TokenType.COMMA):
                        self.advance()  # consume comma
                        arguments.append(self.expression())
                
                self.consume(TokenType.RPAREN)
                return FunctionCallNode(name, arguments, token.line, token.column)
            
            # Index expression
            elif self.match(TokenType.LBRACKET):
                var_node = VariableNode(name, token.line, token.column)
                self.advance()  # consume LBRACKET
                index = self.expression()
                self.consume(TokenType.RBRACKET)
                return IndexNode(var_node, index, token.line, token.column)
            
            # Simple variable
            else:
                return VariableNode(name, token.line, token.column)
        
        # List expression
        if self.match(TokenType.LBRACKET):
            self.advance()  # consume LBRACKET
            elements = []
            
            if not self.match(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    self.advance()  # consume comma
                    elements.append(self.expression())
            
            self.consume(TokenType.RBRACKET)
            return ListNode(elements, token.line, token.column)
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()  # consume LPAREN
            expr = self.expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        # Error case
        raise ParseError(f"Unexpected token: {token.type.name}", token)
    
    def print_errors(self):
        """Print all parsing errors."""
        if not self.errors:
            print("No parsing errors found.")
            return
        
        print("=" * 60)
        print("PARSING ERRORS")
        print("=" * 60)
        for error in self.errors:
            print(f"Line {error.line}, Column {error.column}: {error.message}")
        print("=" * 60)
        print(f"Total errors: {len(self.errors)}")

if __name__ == "__main__":
    from lexer import Lexer
    
    # Test the parser
    test_code = '''
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

result = factorial(5)
print(result)
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        print("Parsing successful!")
        printer = ASTPrinter()
        ast.accept(printer)
    else:
        parser.print_errors()