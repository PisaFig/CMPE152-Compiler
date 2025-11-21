# Interactive Compiler Mode Guide

## Quick Start

Run the compiler in interactive mode to type and compile code dynamically!

### Option 1: Using the launcher script (Easiest)
```bash
python run_interactive.py
```

### Option 2: Using the main compiler
```bash
python src/compiler.py -i
```

### Option 3: Direct launch
```bash
python src/interactive.py
```

---

## 📖 How to Use

### Main Menu
When you launch interactive mode, you'll see 5 options:

1. **Multi-line mode** - Write complete programs with functions, loops, etc.
2. **Quick mode** - Test single expressions or statements
3. **Load from file** - Compile an existing .py file
4. **Show history** - View your compilation history
5. **Exit** - Quit the interactive compiler

---

## 💡 Examples

### Example 1: Quick Expression Mode
```
Choose mode: 2
>>> x = 10 + 5
COMPILATION SUCCESSFUL
```

### Example 2: Multi-line Program
```
Choose mode: 1
Enter your code (type :compile when done):
----------------------------------------------------------------------
  1 | def factorial(n):
  2 |     if n <= 1:
  3 |         return 1
  4 |     else:
  5 |         return n * factorial(n - 1)
  6 | 
  7 | result = factorial(5)
  8 | print(result)
  9 | :compile

COMPILATION SUCCESSFUL
```

### Example 3: If Statement
```
  1 | score = 85
  2 | if score >= 80:
  3 |     print("Good job!")
  4 | else:
  5 |     print("Keep trying")
  6 | :compile
```

---

## 🎯 Commands (Multi-line Mode)

While typing code in multi-line mode, you can use these commands:

- `:compile` - Finish typing and compile the code
- `:clear` - Clear the current code buffer and start over
- `:debug` - Toggle debug mode (shows detailed compiler output)
- `:help` - Show help message
- `:exit` - Exit to main menu

---

## Features

### Full Compilation Pipeline
- **Lexical Analysis**: See tokens generated from your code
- **Syntax Analysis**: Parse tree and AST generation
- **Semantic Analysis**: Type checking and scope resolution  
- **Code Generation**: Three-address intermediate code

### Real-time Feedback
- Instant compilation results
- Clear error messages with line numbers
- View generated instructions

### Debug Mode
Toggle debug mode with `:debug` to see:
- Complete token list
- AST structure
- Symbol table
- All generated instructions

### Compilation History
View all your previous compilation attempts with the "Show history" option.

---

## Supported Python Subset Features

### Data Types
- Integers: `42`, `-10`
- Floats: `3.14`, `-2.5`
- Strings: `"hello"`, `'world'`
- Booleans: `True`, `False`
- Lists: `[1, 2, 3]`

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical: `and`, `or`, `not`

### Control Flow
```python
# If/elif/else
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")

# While loops
while count > 0:
    print(count)
    count = count - 1

# For loops
for item in my_list:
    print(item)
```

### Functions
```python
def greet(name):
    message = "Hello, " + name
    return message

result = greet("Student")
```

### Built-in Functions
- `print()` - Output text
- `input()` - Read input (in full programs)
- `len()` - Get length
- `int()`, `float()`, `str()`, `bool()` - Type conversions

---

## Sample Session

```
======================================================================
   CMPE 152 Python Subset Compiler - Interactive Mode
======================================================================
Type your code below. Commands:
  :compile  - Compile the entered code
  :clear    - Clear current code buffer
  :debug    - Toggle debug mode
  :help     - Show this help message
  :exit     - Exit interactive mode
======================================================================

======================================================================
Choose mode:
  1. Multi-line mode (full programs)
  2. Quick mode (single expressions)
  3. Load from file
  4. Show history
  5. Exit
======================================================================

Enter choice (1-5): 1

Enter your code (type :compile when done):
----------------------------------------------------------------------
  1 | x = 10
  2 | y = 20
  3 | sum = x + y
  4 | print("Sum:", sum)
  5 | :compile

======================================================================
COMPILING...
======================================================================

Source Code:
----------------------------------------------------------------------
  1 | x = 10
  2 | y = 20
  3 | sum = x + y
  4 | print("Sum:", sum)
----------------------------------------------------------------------
Starting compilation process...
================================================================================
Phase 1: Lexical Analysis
----------------------------------------
✓ Tokenization successful: 18 tokens generated

Phase 2: Syntax Analysis (Parsing)
----------------------------------------
✓ Parsing successful: AST generated

Phase 3: Semantic Analysis
----------------------------------------
✓ Semantic analysis successful: No errors found

Phase 4: Code Generation
----------------------------------------
✓ Code generation successful: 10 instructions generated
Compilation completed successfully!

======================================================================
COMPILATION SUCCESSFUL
======================================================================

Compilation Summary:
  • Tokens generated: 18
  • AST nodes: Generated
  • Semantic errors: 0
  • Instructions generated: 10

Generated Code (first 10 instructions):
    1: x = 10
    2: y = 20
    3: t1 = x + y
    4: sum = t1
    5: PARAM sum
    6: PRINT sum
```

---

## 🛠️ Tips

1. **Start Simple**: Try quick mode first to test expressions
2. **Use Debug Mode**: Toggle `:debug` to see all compilation phases
3. **Check History**: Review past compilations to track your progress
4. **Clear Buffer**: Use `:clear` if you make a mistake while typing
5. **Load Files**: Use option 3 to test your existing Python files

---

## ❓ Troubleshooting

### "Python was not found"
Make sure Python 3 is installed and in your PATH.

### Import errors
Make sure you're running from the project root directory:
```bash
cd C:\Users\pfigu\CMPE152
python run_interactive.py
```

### Indentation errors
Python requires consistent indentation. Use spaces (not tabs), typically 4 spaces per level.

---

## 🎓 Perfect for Learning!

Interactive mode is ideal for:
- **Testing examples** from your textbook
- **Understanding compilation phases** step by step
- **Debugging code** before writing full programs
- **Demonstrating** compiler concepts in presentations
- **Experimenting** with language features

---

## Related Files

- `src/interactive.py` - Interactive compiler implementation
- `src/compiler.py` - Main compiler (use with `-i` flag)
- `run_interactive.py` - Quick launcher script
- `examples/` - Sample programs to try

Enjoy coding with your CMPE 152 compiler!

