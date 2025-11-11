"""
Semantic Analyzer for Python Subset Compiler
Performs type checking, scope analysis, and variable usage validation.
"""

from typing import List, Optional, Dict, Any
from tokens import TokenType
from ast_nodes import *
from symbol_table import SymbolTable, SymbolType, DataType, SemanticError

class SemanticAnalyzer(ASTVisitor):
    """
    Semantic analyzer that performs:
    1. Variable declaration and usage validation
    2. Type checking and inference
    3. Scope resolution
    4. Function signature verification
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function = None
        self.return_type = None
        
    def analyze(self, ast: ProgramNode) -> bool:
        """Perform semantic analysis on the AST. Returns True if no errors."""
        try:
            ast.accept(self)
            return len(self.errors) == 0
        except Exception as e:
            if isinstance(e, SemanticError):
                self.errors.append(e)
            return False
    
    def error(self, message: str, line: int, column: int):
        """Record a semantic error."""
        error = SemanticError(message, line, column)
        self.errors.append(error)
    
    def infer_type(self, node: ExpressionNode) -> DataType:
        """Infer the data type of an expression."""
        if isinstance(node, LiteralNode):
            type_map = {
                TokenType.INTEGER: DataType.INTEGER,
                TokenType.FLOAT: DataType.FLOAT,
                TokenType.STRING: DataType.STRING,
                TokenType.BOOLEAN: DataType.BOOLEAN
            }
            return type_map.get(node.token_type, DataType.UNKNOWN)
        
        elif isinstance(node, VariableNode):
            symbol = self.symbol_table.lookup(node.name)
            return symbol.data_type if symbol else DataType.UNKNOWN
        
        elif isinstance(node, BinaryOpNode):
            return self._infer_binary_op_type(node)
        
        elif isinstance(node, UnaryOpNode):
            return self._infer_unary_op_type(node)
        
        elif isinstance(node, FunctionCallNode):
            return self._infer_function_call_type(node)
        
        elif isinstance(node, ListNode):
            return DataType.LIST
        
        elif isinstance(node, IndexNode):
            list_type = self.infer_type(node.list_expr)
            if list_type == DataType.LIST:
                return DataType.UNKNOWN  # Could be any type
            elif list_type == DataType.STRING:
                return DataType.STRING
            return DataType.UNKNOWN
        
        return DataType.UNKNOWN
    
    def _infer_binary_op_type(self, node: BinaryOpNode) -> DataType:
        """Infer type for binary operations."""
        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)
        
        # Arithmetic operations
        if node.operator in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, 
                           TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER]:
            if left_type == DataType.FLOAT or right_type == DataType.FLOAT:
                return DataType.FLOAT
            elif left_type == DataType.INTEGER and right_type == DataType.INTEGER:
                return DataType.INTEGER
            elif node.operator == TokenType.PLUS:
                # String concatenation
                if left_type == DataType.STRING or right_type == DataType.STRING:
                    return DataType.STRING
        
        # Comparison operations
        elif node.operator in [TokenType.LESS_THAN, TokenType.LESS_EQUAL,
                             TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                             TokenType.EQUAL, TokenType.NOT_EQUAL]:
            return DataType.BOOLEAN
        
        # Logical operations
        elif node.operator in [TokenType.AND, TokenType.OR]:
            return DataType.BOOLEAN
        
        return DataType.UNKNOWN
    
    def _infer_unary_op_type(self, node: UnaryOpNode) -> DataType:
        """Infer type for unary operations."""
        operand_type = self.infer_type(node.operand)
        
        if node.operator == TokenType.NOT:
            return DataType.BOOLEAN
        elif node.operator in [TokenType.PLUS, TokenType.MINUS]:
            return operand_type if operand_type in [DataType.INTEGER, DataType.FLOAT] else DataType.UNKNOWN
        
        return DataType.UNKNOWN
    
    def _infer_function_call_type(self, node: FunctionCallNode) -> DataType:
        """Infer return type for function calls."""
        # Built-in function return types
        builtin_returns = {
            'print': DataType.UNKNOWN,  # Returns None in Python
            'input': DataType.STRING,
            'len': DataType.INTEGER,
            'int': DataType.INTEGER,
            'float': DataType.FLOAT,
            'str': DataType.STRING,
            'bool': DataType.BOOLEAN
        }
        
        if node.name in builtin_returns:
            return builtin_returns[node.name]
        
        # User-defined functions - would need more sophisticated analysis
        return DataType.UNKNOWN
    
    def check_type_compatibility(self, expected: DataType, actual: DataType, 
                                operation: str, line: int, column: int) -> bool:
        """Check if types are compatible for an operation."""
        if expected == actual or expected == DataType.UNKNOWN or actual == DataType.UNKNOWN:
            return True
        
        # Numeric type promotion
        if expected == DataType.FLOAT and actual == DataType.INTEGER:
            return True
        
        self.error(f"Type mismatch in {operation}: expected {expected.name}, got {actual.name}",
                  line, column)
        return False
    
    # Visitor methods
    def visit_program(self, node: ProgramNode):
        """Visit program node and analyze all statements."""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_assignment(self, node: AssignmentNode):
        """Visit assignment node - handle variable declaration and type checking."""
        # Analyze the expression first
        node.expression.accept(self)
        expr_type = self.infer_type(node.expression)
        
        # Check if variable exists
        symbol = self.symbol_table.lookup_local(node.variable)
        
        if symbol is None:
            # New variable declaration
            if not self.symbol_table.define(node.variable, SymbolType.VARIABLE, 
                                          expr_type, node.line, node.column):
                self.error(f"Cannot define variable '{node.variable}'", node.line, node.column)
            else:
                self.symbol_table.set_initialized(node.variable)
        else:
            # Variable reassignment - check type compatibility
            if not self.check_type_compatibility(symbol.data_type, expr_type, 
                                               "assignment", node.line, node.column):
                pass  # Error already recorded
            self.symbol_table.set_initialized(node.variable)
    
    def visit_if(self, node: IfNode):
        """Visit if statement - check condition types and analyze blocks."""
        # Check condition type
        node.condition.accept(self)
        condition_type = self.infer_type(node.condition)
        
        if condition_type != DataType.BOOLEAN and condition_type != DataType.UNKNOWN:
            self.error(f"If condition must be boolean, got {condition_type.name}",
                      node.line, node.column)
        
        # Analyze then block
        self.symbol_table.enter_scope("if")
        for stmt in node.then_body:
            stmt.accept(self)
        self.symbol_table.exit_scope()
        
        # Analyze elif clauses
        for elif_condition, elif_body in node.elif_clauses:
            elif_condition.accept(self)
            elif_type = self.infer_type(elif_condition)
            if elif_type != DataType.BOOLEAN and elif_type != DataType.UNKNOWN:
                self.error(f"Elif condition must be boolean, got {elif_type.name}",
                          elif_condition.line, elif_condition.column)
            
            self.symbol_table.enter_scope("elif")
            for stmt in elif_body:
                stmt.accept(self)
            self.symbol_table.exit_scope()
        
        # Analyze else block
        if node.else_body:
            self.symbol_table.enter_scope("else")
            for stmt in node.else_body:
                stmt.accept(self)
            self.symbol_table.exit_scope()
    
    def visit_while(self, node: WhileNode):
        """Visit while statement - check condition and analyze body."""
        # Check condition type
        node.condition.accept(self)
        condition_type = self.infer_type(node.condition)
        
        if condition_type != DataType.BOOLEAN and condition_type != DataType.UNKNOWN:
            self.error(f"While condition must be boolean, got {condition_type.name}",
                      node.line, node.column)
        
        # Analyze body
        self.symbol_table.enter_scope("while")
        for stmt in node.body:
            stmt.accept(self)
        self.symbol_table.exit_scope()
    
    def visit_for(self, node: ForNode):
        """Visit for statement - check iterable and analyze body."""
        # Analyze iterable
        node.iterable.accept(self)
        iterable_type = self.infer_type(node.iterable)
        
        if iterable_type not in [DataType.LIST, DataType.STRING, DataType.UNKNOWN]:
            self.error(f"For loop iterable must be list or string, got {iterable_type.name}",
                      node.line, node.column)
        
        # Enter new scope and define loop variable
        self.symbol_table.enter_scope("for")
        
        # Determine loop variable type
        if iterable_type == DataType.STRING:
            var_type = DataType.STRING
        else:
            var_type = DataType.UNKNOWN  # Could be any type in a list
        
        if not self.symbol_table.define(node.variable, SymbolType.VARIABLE, 
                                      var_type, node.line, node.column):
            self.error(f"Cannot define loop variable '{node.variable}'", node.line, node.column)
        else:
            self.symbol_table.set_initialized(node.variable)
        
        # Analyze body
        for stmt in node.body:
            stmt.accept(self)
        
        self.symbol_table.exit_scope()
    
    def visit_function_def(self, node: FunctionDefNode):
        """Visit function definition - define function and analyze body."""
        # Define function in current scope
        if not self.symbol_table.define(node.name, SymbolType.FUNCTION, 
                                      DataType.FUNCTION, node.line, node.column, 
                                      node.parameters):
            self.error(f"Function '{node.name}' already defined", node.line, node.column)
            return
        
        # Enter function scope
        self.symbol_table.enter_scope(f"function_{node.name}")
        old_function = self.current_function
        self.current_function = node.name
        
        # Define parameters
        for param in node.parameters:
            if not self.symbol_table.define(param, SymbolType.PARAMETER, 
                                          DataType.UNKNOWN, node.line, node.column):
                self.error(f"Parameter '{param}' already defined", node.line, node.column)
            else:
                self.symbol_table.set_initialized(param)
        
        # Analyze function body
        for stmt in node.body:
            stmt.accept(self)
        
        # Exit function scope
        self.symbol_table.exit_scope()
        self.current_function = old_function
    
    def visit_return(self, node: ReturnNode):
        """Visit return statement - check if in function and analyze expression."""
        if self.current_function is None:
            self.error("Return statement outside function", node.line, node.column)
            return
        
        if node.expression:
            node.expression.accept(self)
    
    def visit_expression_statement(self, node: ExpressionStatementNode):
        """Visit expression statement."""
        node.expression.accept(self)
    
    def visit_literal(self, node: LiteralNode):
        """Visit literal node - no semantic analysis needed."""
        pass
    
    def visit_variable(self, node: VariableNode):
        """Visit variable node - check if variable is defined and initialized."""
        symbol = self.symbol_table.lookup(node.name)
        
        if symbol is None:
            self.error(f"Undefined variable '{node.name}'", node.line, node.column)
        elif not symbol.is_initialized:
            self.error(f"Variable '{node.name}' used before initialization", 
                      node.line, node.column)
    
    def visit_binary_op(self, node: BinaryOpNode):
        """Visit binary operation - analyze operands and check type compatibility."""
        node.left.accept(self)
        node.right.accept(self)
        
        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)
        
        # Type checking for operations
        if node.operator in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, 
                           TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER]:
            # Arithmetic operations
            if node.operator == TokenType.PLUS:
                # Allow string concatenation
                if not ((left_type in [DataType.INTEGER, DataType.FLOAT] and 
                        right_type in [DataType.INTEGER, DataType.FLOAT]) or
                       (left_type == DataType.STRING and right_type == DataType.STRING)):
                    if left_type != DataType.UNKNOWN and right_type != DataType.UNKNOWN:
                        self.error(f"Invalid operand types for +: {left_type.name} and {right_type.name}",
                                  node.line, node.column)
            else:
                # Other arithmetic operations require numeric types
                if (left_type not in [DataType.INTEGER, DataType.FLOAT, DataType.UNKNOWN] or
                    right_type not in [DataType.INTEGER, DataType.FLOAT, DataType.UNKNOWN]):
                    self.error(f"Invalid operand types for {node.operator.name}: "
                              f"{left_type.name} and {right_type.name}",
                              node.line, node.column)
    
    def visit_unary_op(self, node: UnaryOpNode):
        """Visit unary operation - analyze operand and check type compatibility."""
        node.operand.accept(self)
        
        operand_type = self.infer_type(node.operand)
        
        if node.operator == TokenType.NOT:
            # NOT operator should work on any type (Python truthy/falsy)
            pass
        elif node.operator in [TokenType.PLUS, TokenType.MINUS]:
            if operand_type not in [DataType.INTEGER, DataType.FLOAT, DataType.UNKNOWN]:
                self.error(f"Invalid operand type for {node.operator.name}: {operand_type.name}",
                          node.line, node.column)
    
    def visit_function_call(self, node: FunctionCallNode):
        """Visit function call - check if function exists and validate arguments."""
        symbol = self.symbol_table.lookup(node.name)
        
        if symbol is None:
            self.error(f"Undefined function '{node.name}'", node.line, node.column)
            return
        
        if symbol.symbol_type != SymbolType.FUNCTION:
            self.error(f"'{node.name}' is not a function", node.line, node.column)
            return
        
        # Check argument count for user-defined functions
        if (symbol.parameters and 
            len(symbol.parameters) > 0 and 
            symbol.parameters[0] != "*args"):  # Skip built-ins with *args
            if len(node.arguments) != len(symbol.parameters):
                self.error(f"Function '{node.name}' expects {len(symbol.parameters)} "
                          f"arguments, got {len(node.arguments)}", 
                          node.line, node.column)
        
        # Analyze arguments
        for arg in node.arguments:
            arg.accept(self)
    
    def visit_list(self, node: ListNode):
        """Visit list node - analyze all elements."""
        for element in node.elements:
            element.accept(self)
    
    def visit_index(self, node: IndexNode):
        """Visit index node - check list/string type and index type."""
        node.list_expr.accept(self)
        node.index.accept(self)
        
        list_type = self.infer_type(node.list_expr)
        index_type = self.infer_type(node.index)
        
        if list_type not in [DataType.LIST, DataType.STRING, DataType.UNKNOWN]:
            self.error(f"Cannot index into {list_type.name}", node.line, node.column)
        
        if index_type not in [DataType.INTEGER, DataType.UNKNOWN]:
            self.error(f"List index must be integer, got {index_type.name}",
                      node.line, node.column)
    
    def print_errors(self):
        """Print all semantic errors."""
        if not self.errors:
            print("No semantic errors found.")
            return
        
        print("=" * 60)
        print("SEMANTIC ANALYSIS ERRORS")
        print("=" * 60)
        for error in self.errors:
            print(f"Line {error.line}, Column {error.column}: {error.message}")
        print("=" * 60)
        print(f"Total errors: {len(self.errors)}")
    
    def print_symbol_table(self):
        """Print the symbol table."""
        self.symbol_table.print_table()

if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Test semantic analysis
    test_code = '''
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

x = 5
result = factorial(x)
print(result)

# Test error: undefined variable
y = undefined_var + 1
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        
        print("Semantic Analysis Results:")
        print("=" * 40)
        
        if success:
            print("✓ No semantic errors found")
        else:
            analyzer.print_errors()
        
        print("\nSymbol Table:")
        analyzer.print_symbol_table()
    else:
        parser.print_errors()