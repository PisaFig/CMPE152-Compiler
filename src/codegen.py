"""
Code Generator for Python Subset Compiler
Generates three-address intermediate code from AST.
"""

from typing import List, Dict, Optional, Any
from ast_nodes import *
from tokens import TokenType

class Instruction:
    """Represents a single three-address code instruction."""
    
    def __init__(self, op: str, arg1: Any = None, arg2: Any = None, result: Any = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        
    def __str__(self):
        if self.op in ['LABEL', 'GOTO', 'CALL', 'RETURN', 'PRINT']:
            if self.arg1 is not None:
                return f"{self.op} {self.arg1}"
            return self.op
        elif self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'PARAM':
            return f"PARAM {self.arg1}"
        elif self.op == 'FUNCTION':
            return f"FUNCTION {self.arg1}"
        elif self.op == 'END_FUNCTION':
            return f"END_FUNCTION {self.arg1}"
        elif self.op in ['IF_FALSE', 'IF_TRUE']:
            return f"{self.op} {self.arg1} GOTO {self.result}"
        elif self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        else:
            return f"{self.result} = {self.op} {self.arg1}"

class CodeGenerator(ASTVisitor):
    """
    Code generator that produces three-address intermediate code.
    Implements visitor pattern for AST traversal.
    """
    
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function = None
        
    def generate(self, ast: ProgramNode) -> List[Instruction]:
        """Generate code for the entire program."""
        ast.accept(self)
        return self.instructions
    
    def new_temp(self) -> str:
        """Generate a new temporary variable."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        """Generate a new label."""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def emit(self, op: str, arg1: Any = None, arg2: Any = None, result: Any = None):
        """Emit a new instruction."""
        instr = Instruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr
    
    def emit_label(self, label: str):
        """Emit a label."""
        self.emit('LABEL', label)
    
    def emit_goto(self, label: str):
        """Emit an unconditional jump."""
        self.emit('GOTO', label)
    
    def emit_conditional(self, condition: str, label: str, jump_if_false: bool = True):
        """Emit a conditional jump."""
        op = 'IF_FALSE' if jump_if_false else 'IF_TRUE'
        self.emit(op, condition, result=label)
    
    # Visitor methods
    def visit_program(self, node: ProgramNode):
        """Generate code for the entire program."""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_assignment(self, node: AssignmentNode):
        """Generate code for assignment statement."""
        # Generate code for the expression
        expr_result = node.expression.accept(self)
        
        # Emit assignment instruction
        self.emit('ASSIGN', expr_result, result=node.variable)
    
    def visit_if(self, node: IfNode):
        """Generate code for if statement with elif/else support."""
        end_label = self.new_label()
        
        # Main if condition
        condition_result = node.condition.accept(self)
        else_label = self.new_label()
        self.emit_conditional(condition_result, else_label, jump_if_false=True)
        
        # Then body
        for stmt in node.then_body:
            stmt.accept(self)
        self.emit_goto(end_label)
        
        # Handle elif clauses
        for elif_condition, elif_body in node.elif_clauses:
            self.emit_label(else_label)
            elif_condition_result = elif_condition.accept(self)
            else_label = self.new_label()  # New label for next elif/else
            self.emit_conditional(elif_condition_result, else_label, jump_if_false=True)
            
            for stmt in elif_body:
                stmt.accept(self)
            self.emit_goto(end_label)
        
        # Else body
        if node.else_body:
            self.emit_label(else_label)
            for stmt in node.else_body:
                stmt.accept(self)
        else:
            self.emit_label(else_label)
        
        self.emit_label(end_label)
    
    def visit_while(self, node: WhileNode):
        """Generate code for while loop."""
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit_label(start_label)
        
        # Check condition
        condition_result = node.condition.accept(self)
        self.emit_conditional(condition_result, end_label, jump_if_false=True)
        
        # Loop body
        for stmt in node.body:
            stmt.accept(self)
        
        # Jump back to start
        self.emit_goto(start_label)
        self.emit_label(end_label)
    
    def visit_for(self, node: ForNode):
        """Generate code for for loop."""
        # For simplicity, we'll generate basic iteration code
        # In a full implementation, this would handle iterators properly
        
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Initialize iterator (simplified)
        iterable_result = node.iterable.accept(self)
        index_var = self.new_temp()
        length_var = self.new_temp()
        
        self.emit('ASSIGN', 0, result=index_var)
        self.emit('LEN', iterable_result, result=length_var)
        
        self.emit_label(start_label)
        
        # Check if index < length
        condition_temp = self.new_temp()
        self.emit('<', index_var, length_var, condition_temp)
        self.emit_conditional(condition_temp, end_label, jump_if_false=True)
        
        # Get current element
        self.emit('INDEX', iterable_result, index_var, node.variable)
        
        # Loop body
        for stmt in node.body:
            stmt.accept(self)
        
        # Increment index
        temp_inc = self.new_temp()
        self.emit('+', index_var, 1, temp_inc)
        self.emit('ASSIGN', temp_inc, result=index_var)
        
        self.emit_goto(start_label)
        self.emit_label(end_label)
    
    def visit_function_def(self, node: FunctionDefNode):
        """Generate code for function definition."""
        old_function = self.current_function
        self.current_function = node.name
        
        # Function header
        self.emit('FUNCTION', node.name)
        
        # Parameters are already in the symbol table
        # Function body
        for stmt in node.body:
            stmt.accept(self)
        
        # End function
        self.emit('END_FUNCTION', node.name)
        self.current_function = old_function
    
    def visit_return(self, node: ReturnNode):
        """Generate code for return statement."""
        if node.expression:
            result = node.expression.accept(self)
            self.emit('RETURN', result)
        else:
            self.emit('RETURN')
    
    def visit_expression_statement(self, node: ExpressionStatementNode):
        """Generate code for expression statement."""
        node.expression.accept(self)
    
    def visit_literal(self, node: LiteralNode):
        """Generate code for literal values."""
        # Literals are used directly in instructions
        return node.value
    
    def visit_variable(self, node: VariableNode):
        """Generate code for variable reference."""
        # Variables are used directly by name
        return node.name
    
    def visit_binary_op(self, node: BinaryOpNode):
        """Generate code for binary operations."""
        left_result = node.left.accept(self)
        right_result = node.right.accept(self)
        
        # Map token types to operation strings
        op_map = {
            TokenType.PLUS: '+',
            TokenType.MINUS: '-',
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.MODULO: '%',
            TokenType.POWER: '**',
            TokenType.EQUAL: '==',
            TokenType.NOT_EQUAL: '!=',
            TokenType.LESS_THAN: '<',
            TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_THAN: '>',
            TokenType.GREATER_EQUAL: '>=',
            TokenType.AND: 'AND',
            TokenType.OR: 'OR'
        }
        
        op_str = op_map.get(node.operator, str(node.operator))
        result_temp = self.new_temp()
        
        self.emit(op_str, left_result, right_result, result_temp)
        return result_temp
    
    def visit_unary_op(self, node: UnaryOpNode):
        """Generate code for unary operations."""
        operand_result = node.operand.accept(self)
        
        op_map = {
            TokenType.MINUS: 'NEG',
            TokenType.PLUS: 'POS',
            TokenType.NOT: 'NOT'
        }
        
        op_str = op_map.get(node.operator, str(node.operator))
        result_temp = self.new_temp()
        
        self.emit(op_str, operand_result, result=result_temp)
        return result_temp
    
    def visit_function_call(self, node: FunctionCallNode):
        """Generate code for function calls."""
        # Generate code for arguments
        for arg in node.arguments:
            arg_result = arg.accept(self)
            self.emit('PARAM', arg_result)
        
        # Generate function call
        if node.name in ['print', 'input', 'len']:
            # Built-in functions
            if node.name == 'print':
                # Special handling for print
                if node.arguments:
                    arg_result = node.arguments[0].accept(self)
                    self.emit('PRINT', arg_result)
                else:
                    self.emit('PRINT', '""')
                return None
            else:
                result_temp = self.new_temp()
                self.emit('CALL', f"builtin_{node.name}", len(node.arguments), result_temp)
                return result_temp
        else:
            # User-defined function
            result_temp = self.new_temp()
            self.emit('CALL', node.name, len(node.arguments), result_temp)
            return result_temp
    
    def visit_list(self, node: ListNode):
        """Generate code for list literals."""
        result_temp = self.new_temp()
        self.emit('CREATE_LIST', result=result_temp)
        
        for element in node.elements:
            element_result = element.accept(self)
            self.emit('APPEND', result_temp, element_result)
        
        return result_temp
    
    def visit_index(self, node: IndexNode):
        """Generate code for list/string indexing."""
        list_result = node.list_expr.accept(self)
        index_result = node.index.accept(self)
        
        result_temp = self.new_temp()
        self.emit('INDEX', list_result, index_result, result_temp)
        return result_temp
    
    def print_code(self):
        """Print the generated three-address code."""
        print("=" * 60)
        print("GENERATED THREE-ADDRESS CODE")
        print("=" * 60)
        
        for i, instr in enumerate(self.instructions):
            print(f"{i+1:3d}: {instr}")
        
        print("=" * 60)
        print(f"Total instructions: {len(self.instructions)}")
    
    def save_code(self, filename: str):
        """Save the generated code to a file."""
        with open(filename, 'w') as f:
            f.write("# Generated Three-Address Code\n")
            f.write("# Python Subset Compiler\n\n")
            
            for i, instr in enumerate(self.instructions):
                f.write(f"{i+1:3d}: {instr}\n")

if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Test code generation
    test_code = '''
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

x = 5
result = factorial(x)
print(result)
'''
    
    print("Compiling test program...")
    print("Source code:")
    print("-" * 40)
    print(test_code)
    print("-" * 40)
    
    # Lexical analysis
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        # Code generation
        generator = CodeGenerator()
        instructions = generator.generate(ast)
        
        print("\nCode generation successful!")
        generator.print_code()
    else:
        print("Parsing failed!")
        parser.print_errors()