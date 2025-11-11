# Context-Free Grammar for Python Subset Compiler

## CMPE 152 - Compiler Design Project

This document describes the Context-Free Grammar (CFG) used by our Python subset compiler. The grammar follows standard compiler design principles and demonstrates proper handling of operator precedence, associativity, and Python's indentation-based syntax.

## Grammar Productions

### Program Structure
```
program         → statement_list EOF
statement_list  → statement (NEWLINE statement)*
statement       → assignment | if_stmt | while_stmt | for_stmt | 
                  function_def | return_stmt | expression_stmt
```

### Statements
```
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
```

### Expressions (with Precedence)
```
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
```

### Complex Constructs
```
function_call   → IDENTIFIER LPAREN argument_list? RPAREN
list_expr       → LBRACKET (expression (COMMA expression)*)? RBRACKET
index_expr      → primary LBRACKET expression RBRACKET
parameter_list  → IDENTIFIER (COMMA IDENTIFIER)*
argument_list   → expression (COMMA expression)*
literal         → INTEGER | FLOAT | STRING | BOOLEAN
```

## Operator Precedence (Highest to Lowest)

1. **Primary expressions**: literals, identifiers, parentheses, function calls
2. **Power**: `**` (right associative)
3. **Unary**: `+`, `-`, `not`
4. **Multiplicative**: `*`, `/`, `%`
5. **Additive**: `+`, `-`
6. **Comparison**: `<`, `<=`, `>`, `>=`
7. **Equality**: `==`, `!=`
8. **Logical AND**: `and`
9. **Logical OR**: `or`

## Key Design Features

### Indentation Handling
The grammar uses special INDENT and DEDENT tokens to handle Python's indentation-based block structure:
- INDENT: Signals the start of an indented block
- DEDENT: Signals the end of an indented block
- Multiple DEDENT tokens may be generated for nested block endings

### Error Recovery
The parser implements error recovery mechanisms:
- Synchronization at statement boundaries
- Continuation after syntax errors
- Detailed error reporting with line/column information

### Left/Right Derivations

#### Example: Assignment Statement
**Left Derivation** for `x = 5 + 3`:
```
program → statement_list EOF
statement_list → statement
statement → assignment
assignment → IDENTIFIER ASSIGN expression
assignment → x ASSIGN expression
assignment → x ASSIGN logical_or
assignment → x ASSIGN logical_and
assignment → x ASSIGN equality
assignment → x ASSIGN comparison
assignment → x ASSIGN term
assignment → x ASSIGN factor PLUS factor
assignment → x ASSIGN unary PLUS unary
assignment → x ASSIGN power PLUS power
assignment → x ASSIGN primary PLUS primary
assignment → x ASSIGN literal PLUS literal
assignment → x ASSIGN 5 PLUS 3
```

**Right Derivation** for `x = 5 + 3`:
```
program → statement_list EOF
statement_list → statement
statement → assignment
assignment → IDENTIFIER ASSIGN expression
assignment → IDENTIFIER ASSIGN logical_or
assignment → IDENTIFIER ASSIGN logical_and
assignment → IDENTIFIER ASSIGN equality
assignment → IDENTIFIER ASSIGN comparison
assignment → IDENTIFIER ASSIGN term
assignment → IDENTIFIER ASSIGN factor PLUS factor
assignment → IDENTIFIER ASSIGN unary PLUS unary
assignment → IDENTIFIER ASSIGN power PLUS power
assignment → IDENTIFIER ASSIGN primary PLUS primary
assignment → IDENTIFIER ASSIGN literal PLUS literal
assignment → IDENTIFIER ASSIGN literal PLUS 3
assignment → IDENTIFIER ASSIGN 5 PLUS 3
assignment → x ASSIGN 5 PLUS 3
```

### Parse Tree vs Abstract Syntax Tree

**Parse Tree**: Contains all grammar symbols including intermediate non-terminals
**AST**: Simplified tree with only semantically significant nodes

Example for `x = 5 + 3`:
- Parse tree includes all intermediate expression levels
- AST contains: AssignmentNode(variable="x", expression=BinaryOpNode(left=5, op=PLUS, right=3))

## Chomsky Normal Form Considerations

Our grammar can be converted to CNF for theoretical analysis:
- All productions would be of the form A → BC or A → a
- Useful for parsing complexity analysis
- Our recursive descent parser doesn't require CNF

## Grammar Properties

- **LL(1)**: Can be parsed with 1 token lookahead
- **Unambiguous**: Each valid string has exactly one parse tree
- **Left-recursive**: Eliminated in expression rules for recursive descent
- **Precedence**: Properly encoded in grammar structure