"""
Symbol Table Management for Python Subset Compiler
Handles scope resolution, variable tracking, and semantic analysis support.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
from dataclasses import dataclass

class SymbolType(Enum):
    """Types of symbols in the symbol table."""
    VARIABLE = auto()
    FUNCTION = auto()
    PARAMETER = auto()

class DataType(Enum):
    """Data types supported by the compiler."""
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    LIST = auto()
    FUNCTION = auto()
    UNKNOWN = auto()

@dataclass
class Symbol:
    """Represents a symbol in the symbol table."""
    name: str
    symbol_type: SymbolType
    data_type: DataType
    line: int
    column: int
    scope_level: int
    is_initialized: bool = False
    value: Any = None
    parameters: List[str] = None  # For functions
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

class Scope:
    """Represents a single scope with its symbols."""
    
    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        
    def define(self, symbol: Symbol) -> bool:
        """Define a symbol in this scope. Returns True if successful."""
        if symbol.name in self.symbols:
            return False  # Symbol already exists
        
        symbol.scope_level = self.level
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only."""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope and parent scopes."""
        symbol = self.symbols.get(name)
        if symbol:
            return symbol
        
        if self.parent:
            return self.parent.lookup(name)
        
        return None
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols in this scope."""
        return self.symbols.copy()

class SymbolTable:
    """
    Symbol table with scope management.
    Supports nested scopes for functions and control structures.
    """
    
    def __init__(self):
        self.global_scope = Scope("global", 0)
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]
        self.scope_counter = 0
        
        # Built-in functions
        self._add_builtin_functions()
    
    def _add_builtin_functions(self):
        """Add built-in functions to global scope."""
        builtins = [
            ("print", ["*args"]),
            ("input", ["prompt"]),
            ("len", ["obj"]),
            ("int", ["value"]),
            ("float", ["value"]),
            ("str", ["value"]),
            ("bool", ["value"])
        ]
        
        for name, params in builtins:
            symbol = Symbol(
                name=name,
                symbol_type=SymbolType.FUNCTION,
                data_type=DataType.FUNCTION,
                line=0,
                column=0,
                scope_level=0,
                is_initialized=True,
                parameters=params
            )
            self.global_scope.define(symbol)
    
    def enter_scope(self, name: str = "block") -> Scope:
        """Enter a new scope."""
        self.scope_counter += 1
        new_scope = Scope(f"{name}_{self.scope_counter}", 
                         self.current_scope.level + 1, 
                         self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self) -> Optional[Scope]:
        """Exit the current scope and return to parent."""
        if len(self.scope_stack) <= 1:
            return None  # Cannot exit global scope
        
        exited_scope = self.scope_stack.pop()
        self.current_scope = self.scope_stack[-1]
        return exited_scope
    
    def define(self, name: str, symbol_type: SymbolType, data_type: DataType,
               line: int, column: int, parameters: List[str] = None) -> bool:
        """Define a new symbol in the current scope."""
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            data_type=data_type,
            line=line,
            column=column,
            scope_level=self.current_scope.level,
            parameters=parameters or []
        )
        
        return self.current_scope.define(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol starting from current scope."""
        return self.current_scope.lookup(name)
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in current scope only."""
        return self.current_scope.lookup_local(name)
    
    def set_initialized(self, name: str) -> bool:
        """Mark a symbol as initialized."""
        symbol = self.lookup(name)
        if symbol:
            symbol.is_initialized = True
            return True
        return False
    
    def is_initialized(self, name: str) -> bool:
        """Check if a symbol is initialized."""
        symbol = self.lookup(name)
        return symbol.is_initialized if symbol else False
    
    def get_current_scope_level(self) -> int:
        """Get the current scope level."""
        return self.current_scope.level
    
    def print_table(self):
        """Print the entire symbol table for debugging."""
        print("=" * 80)
        print("SYMBOL TABLE")
        print("=" * 80)
        
        def print_scope(scope: Scope, indent: int = 0):
            prefix = "  " * indent
            print(f"{prefix}Scope: {scope.name} (Level {scope.level})")
            print(f"{prefix}{'Name':<15} {'Type':<10} {'Data Type':<10} {'Line':<6} {'Init':<6} {'Params'}")
            print(f"{prefix}{'-' * 65}")
            
            for symbol in scope.symbols.values():
                params_str = ", ".join(symbol.parameters) if symbol.parameters else ""
                if len(params_str) > 20:
                    params_str = params_str[:17] + "..."
                
                print(f"{prefix}{symbol.name:<15} {symbol.symbol_type.name:<10} "
                      f"{symbol.data_type.name:<10} {symbol.line:<6} "
                      f"{'Yes' if symbol.is_initialized else 'No':<6} {params_str}")
            
            print()
        
        # Print all scopes
        visited = set()
        
        def traverse_scopes(scope: Scope, indent: int = 0):
            if scope in visited:
                return
            visited.add(scope)
            print_scope(scope, indent)
        
        traverse_scopes(self.global_scope)
        for scope in self.scope_stack[1:]:
            if scope not in visited:
                traverse_scopes(scope, 1)
        
        print("=" * 80)

class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")

if __name__ == "__main__":
    # Test the symbol table
    st = SymbolTable()
    
    # Test global scope
    st.define("x", SymbolType.VARIABLE, DataType.INTEGER, 1, 1)
    st.define("factorial", SymbolType.FUNCTION, DataType.FUNCTION, 3, 1, ["n"])
    
    # Test nested scope
    st.enter_scope("function")
    st.define("n", SymbolType.PARAMETER, DataType.INTEGER, 3, 15)
    st.define("result", SymbolType.VARIABLE, DataType.INTEGER, 5, 5)
    
    # Test lookups
    print("Looking up 'x':", st.lookup("x"))
    print("Looking up 'n':", st.lookup("n"))
    print("Looking up 'print':", st.lookup("print"))
    print("Looking up 'nonexistent':", st.lookup("nonexistent"))
    
    st.print_table()