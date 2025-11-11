# CMPE 152 Python Subset Compiler Project

## Project Overview
A comprehensive compiler for a subset of Python, implementing all phases of compilation from lexical analysis to code generation.

## Target Language: Python Subset
Our compiler will handle:
- **Variables**: Assignment and usage
- **Data Types**: integers, floats, strings, booleans
- **Expressions**: Arithmetic, logical, comparison operators
- **Control Flow**: if/elif/else statements, while loops, for loops
- **Functions**: Definition and calls with parameters
- **Built-ins**: print(), input(), len()
- **Data Structures**: Lists (basic operations)

## Compiler Architecture

### Phase 1: Lexical Analysis (Scanner)
- Token recognition and classification
- Symbol table construction
- DFA/NFA implementation for token patterns
- Error detection for invalid tokens

### Phase 2: Syntax Analysis (Parser)
- Context-Free Grammar (CFG) implementation
- Parse tree and Abstract Syntax Tree (AST) generation
- Error recovery mechanisms
- Support for Python's indentation-based syntax

### Phase 3: Semantic Analysis
- Type checking and inference
- Scope resolution
- Variable declaration/usage validation
- Function signature verification

### Phase 4: Code Generation
- Three-address code generation
- Basic optimization
- Assembly-like intermediate representation

## Project Structure
```
src/
├── lexer.py          # Lexical analyzer
├── parser.py         # Syntax analyzer
├── ast_nodes.py      # AST node definitions
├── semantic.py       # Semantic analyzer
├── codegen.py        # Code generator
├── symbol_table.py   # Symbol table management
├── errors.py         # Error handling
└── compiler.py       # Main compiler driver

tests/
├── test_lexer.py     # Lexer unit tests
├── test_parser.py    # Parser unit tests
└── test_integration.py # Integration tests

examples/
├── test1.py          # Basic expressions
├── test2.py          # Control flow
└── test3.py          # Functions

docs/
├── grammar.md        # CFG specification
├── presentation.md   # Project presentation
└── report.md         # Technical report
```

## Getting Started

### Interactive Mode
Type and compile code dynamically:
```bash
python run_interactive.py
```
Or use:
```bash
python src/compiler.py -i
```

See [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md) for complete interactive mode documentation.

### File Mode
1. Run the compiler: `python src/compiler.py examples/test1.py`
2. Run with debug: `python src/compiler.py examples/test1.py --debug`
3. View generated code: Check `output/` directory

## CMPE 152 Requirements Checklist
- [x] Lexical analysis with token classification
- [x] Context-free grammar and parsing
- [x] Parse trees and AST generation
- [x] Semantic analysis with symbol table
- [x] Code generation
- [x] Error recovery and reporting
- [x] Three comprehensive test cases
- [x] Technical documentation
- [x] Presentation materials
