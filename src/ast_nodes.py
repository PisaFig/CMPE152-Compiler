"""
Abstract Syntax Tree (AST) Node Definitions
Defines all node types for the parse tree and AST generation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union
from tokens import TokenType

class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
    
    @abstractmethod
    def accept(self, visitor):
        """Accept method for visitor pattern."""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

# Program and Statement Nodes
class ProgramNode(ASTNode):
    """Root node representing the entire program."""
    
    def __init__(self, statements: List['StatementNode']):
        super().__init__()
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_program(self)

class StatementNode(ASTNode):
    """Base class for all statement nodes."""
    pass

class ExpressionNode(ASTNode):
    """Base class for all expression nodes."""
    pass

# Statement Implementations
class AssignmentNode(StatementNode):
    """Assignment statement: variable = expression"""
    
    def __init__(self, variable: str, expression: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.variable = variable
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)
    
    def __repr__(self):
        return f"AssignmentNode({self.variable}, {self.expression})"

class IfNode(StatementNode):
    """If statement with optional elif and else clauses."""
    
    def __init__(self, condition: ExpressionNode, then_body: List[StatementNode], 
                 elif_clauses: List[tuple] = None, else_body: List[StatementNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_body = then_body
        self.elif_clauses = elif_clauses or []  # List of (condition, body) tuples
        self.else_body = else_body or []
    
    def accept(self, visitor):
        return visitor.visit_if(self)
    
    def __repr__(self):
        return f"IfNode({self.condition}, {len(self.then_body)} stmts)"

class WhileNode(StatementNode):
    """While loop statement."""
    
    def __init__(self, condition: ExpressionNode, body: List[StatementNode], 
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_while(self)
    
    def __repr__(self):
        return f"WhileNode({self.condition}, {len(self.body)} stmts)"

class ForNode(StatementNode):
    """For loop statement: for variable in iterable:"""
    
    def __init__(self, variable: str, iterable: ExpressionNode, body: List[StatementNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_for(self)
    
    def __repr__(self):
        return f"ForNode({self.variable}, {self.iterable}, {len(self.body)} stmts)"

class FunctionDefNode(StatementNode):
    """Function definition: def name(params): body"""
    
    def __init__(self, name: str, parameters: List[str], body: List[StatementNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.parameters = parameters
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_function_def(self)
    
    def __repr__(self):
        return f"FunctionDefNode({self.name}, {self.parameters})"

class ReturnNode(StatementNode):
    """Return statement with optional expression."""
    
    def __init__(self, expression: Optional[ExpressionNode] = None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_return(self)
    
    def __repr__(self):
        return f"ReturnNode({self.expression})"

class ExpressionStatementNode(StatementNode):
    """Statement that is just an expression (like function calls)."""
    
    def __init__(self, expression: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_statement(self)
    
    def __repr__(self):
        return f"ExpressionStatementNode({self.expression})"

# Expression Implementations
class LiteralNode(ExpressionNode):
    """Literal values: numbers, strings, booleans."""
    
    def __init__(self, value: Any, token_type: TokenType, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value
        self.token_type = token_type
    
    def accept(self, visitor):
        return visitor.visit_literal(self)
    
    def __repr__(self):
        return f"LiteralNode({self.value}, {self.token_type.name})"

class VariableNode(ExpressionNode):
    """Variable reference."""
    
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_variable(self)
    
    def __repr__(self):
        return f"VariableNode({self.name})"

class BinaryOpNode(ExpressionNode):
    """Binary operation: left operator right"""
    
    def __init__(self, left: ExpressionNode, operator: TokenType, right: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)
    
    def __repr__(self):
        return f"BinaryOpNode({self.left}, {self.operator.name}, {self.right})"

class UnaryOpNode(ExpressionNode):
    """Unary operation: operator operand"""
    
    def __init__(self, operator: TokenType, operand: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)
    
    def __repr__(self):
        return f"UnaryOpNode({self.operator.name}, {self.operand})"

class FunctionCallNode(ExpressionNode):
    """Function call: name(arguments)"""
    
    def __init__(self, name: str, arguments: List[ExpressionNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def __repr__(self):
        return f"FunctionCallNode({self.name}, {len(self.arguments)} args)"

class ListNode(ExpressionNode):
    """List literal: [elements]"""
    
    def __init__(self, elements: List[ExpressionNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_list(self)
    
    def __repr__(self):
        return f"ListNode({len(self.elements)} elements)"

class IndexNode(ExpressionNode):
    """List indexing: list[index]"""
    
    def __init__(self, list_expr: ExpressionNode, index: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.list_expr = list_expr
        self.index = index
    
    def accept(self, visitor):
        return visitor.visit_index(self)
    
    def __repr__(self):
        return f"IndexNode({self.list_expr}[{self.index}])"

# Visitor Interface for AST traversal
class ASTVisitor(ABC):
    """Abstract base class for AST visitors."""
    
    @abstractmethod
    def visit_program(self, node: ProgramNode): pass
    
    @abstractmethod
    def visit_assignment(self, node: AssignmentNode): pass
    
    @abstractmethod
    def visit_if(self, node: IfNode): pass
    
    @abstractmethod
    def visit_while(self, node: WhileNode): pass
    
    @abstractmethod
    def visit_for(self, node: ForNode): pass
    
    @abstractmethod
    def visit_function_def(self, node: FunctionDefNode): pass
    
    @abstractmethod
    def visit_return(self, node: ReturnNode): pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatementNode): pass
    
    @abstractmethod
    def visit_literal(self, node: LiteralNode): pass
    
    @abstractmethod
    def visit_variable(self, node: VariableNode): pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode): pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOpNode): pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCallNode): pass
    
    @abstractmethod
    def visit_list(self, node: ListNode): pass
    
    @abstractmethod
    def visit_index(self, node: IndexNode): pass

# AST Pretty Printer for debugging
class ASTPrinter(ASTVisitor):
    """Visitor that prints the AST structure."""
    
    def __init__(self):
        self.indent_level = 0
    
    def _indent(self):
        return "  " * self.indent_level
    
    def visit_program(self, node: ProgramNode):
        print(f"{self._indent()}Program:")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_assignment(self, node: AssignmentNode):
        print(f"{self._indent()}Assignment: {node.variable} =")
        self.indent_level += 1
        node.expression.accept(self)
        self.indent_level -= 1
    
    def visit_if(self, node: IfNode):
        print(f"{self._indent()}If:")
        self.indent_level += 1
        print(f"{self._indent()}Condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self.indent_level -= 1
        print(f"{self._indent()}Then:")
        self.indent_level += 1
        for stmt in node.then_body:
            stmt.accept(self)
        self.indent_level -= 1
        
        for condition, body in node.elif_clauses:
            print(f"{self._indent()}Elif:")
            self.indent_level += 1
            condition.accept(self)
            for stmt in body:
                stmt.accept(self)
            self.indent_level -= 1
        
        if node.else_body:
            print(f"{self._indent()}Else:")
            self.indent_level += 1
            for stmt in node.else_body:
                stmt.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_while(self, node: WhileNode):
        print(f"{self._indent()}While:")
        self.indent_level += 1
        node.condition.accept(self)
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_for(self, node: ForNode):
        print(f"{self._indent()}For: {node.variable} in")
        self.indent_level += 1
        node.iterable.accept(self)
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_function_def(self, node: FunctionDefNode):
        print(f"{self._indent()}Function: {node.name}({', '.join(node.parameters)})")
        self.indent_level += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_return(self, node: ReturnNode):
        print(f"{self._indent()}Return:")
        if node.expression:
            self.indent_level += 1
            node.expression.accept(self)
            self.indent_level -= 1
    
    def visit_expression_statement(self, node: ExpressionStatementNode):
        print(f"{self._indent()}Expression Statement:")
        self.indent_level += 1
        node.expression.accept(self)
        self.indent_level -= 1
    
    def visit_literal(self, node: LiteralNode):
        print(f"{self._indent()}Literal: {node.value} ({node.token_type.name})")
    
    def visit_variable(self, node: VariableNode):
        print(f"{self._indent()}Variable: {node.name}")
    
    def visit_binary_op(self, node: BinaryOpNode):
        print(f"{self._indent()}Binary Op: {node.operator.name}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1
    
    def visit_unary_op(self, node: UnaryOpNode):
        print(f"{self._indent()}Unary Op: {node.operator.name}")
        self.indent_level += 1
        node.operand.accept(self)
        self.indent_level -= 1
    
    def visit_function_call(self, node: FunctionCallNode):
        print(f"{self._indent()}Function Call: {node.name}")
        self.indent_level += 1
        for arg in node.arguments:
            arg.accept(self)
        self.indent_level -= 1
    
    def visit_list(self, node: ListNode):
        print(f"{self._indent()}List:")
        self.indent_level += 1
        for element in node.elements:
            element.accept(self)
        self.indent_level -= 1
    
    def visit_index(self, node: IndexNode):
        print(f"{self._indent()}Index:")
        self.indent_level += 1
        node.list_expr.accept(self)
        node.index.accept(self)
        self.indent_level -= 1