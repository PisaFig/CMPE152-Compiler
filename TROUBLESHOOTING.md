# 🔧 Troubleshooting Interactive Mode

## Issue: Compiler Gets Stuck at Phase 2

If the compiler hangs during Phase 2 (Syntax Analysis), here's how to fix it:

---

## ✅ **FIXED - New Safeguards Added**

I've added several fixes to prevent the parser from getting stuck:

1. **Infinite loop detection** - Parser now detects if it's stuck
2. **Better error handling** - Shows exactly where it fails
3. **Automatic newline handling** - Ensures proper token stream
4. **Debug output** - See what's happening in real-time

---

## 🧪 **Test Your Compiler**

Run this debug script to identify the issue:

```bash
python test_interactive.py
```

This will test:
- ✅ Lexer (tokenization)
- ✅ Parser (syntax analysis)
- ✅ Simple expressions
- ✅ Operators
- ✅ Print statements
- ✅ If statements

---

## 🔍 **Debug Mode**

Use debug mode to see exactly what's happening:

```bash
python src/compiler.py -i
```

Then in interactive mode:
1. Type `:debug` to enable debug mode
2. Try your code again
3. Watch the detailed output

You'll see:
```
Starting parser with 8 tokens...
Parser finished. Errors: 0
AST has 1 statements
✓ Parsing successful
```

---

## 🐛 **Common Issues & Solutions**

### Problem: Stuck on simple expression
**Example:** `x = 10`

**Solution:** Make sure code ends with newline
```python
# Now automatically added!
code = "x = 10\n"  # <-- newline is added for you
```

### Problem: Stuck on if statement
**Example:** 
```python
if x > 5:
    print("yes")
```

**Solution:** Check indentation (use 4 spaces)
```python
# Correct:
if x > 5:
    print("yes")  # 4 spaces

# Wrong:
if x > 5:
  print("yes")  # 2 spaces - might cause issues
```

### Problem: Stuck on function
**Example:**
```python
def test():
    return 1
```

**Solution:** Ensure proper structure with newlines
```python
def test():
    return 1

# Call it:
result = test()
```

---

## 💡 **Workarounds**

### Workaround 1: Add explicit newline
If Quick Mode hangs, try Multi-line mode instead:

**Quick Mode (might hang):**
```
>>> x = 10
```

**Multi-line Mode (more reliable):**
```
  1 | x = 10
  2 | :compile
```

### Workaround 2: Use file mode
Save your code to a file and compile it:

```bash
# Save to test.py
echo "x = 10" > test.py

# Compile
python src/compiler.py test.py
```

### Workaround 3: Run the debug test
```bash
python test_interactive.py
```

This will show you exactly which types of code work.

---

## 🎯 **What Was Fixed**

### Fix 1: Parser Infinite Loop Protection
```python
# Added safety counter
while not self.match(TokenType.EOF):
    iteration_count += 1
    
    # Prevent infinite loop
    if self.current == last_position:
        self.advance()  # Force forward progress
        continue
```

### Fix 2: Automatic Newline Addition
```python
# Ensure source code ends with newline
if not source_code.endswith('\n'):
    source_code = source_code + '\n'
```

### Fix 3: Better Error Handling
```python
try:
    success = self.compiler.compile_source(source_code)
except Exception as e:
    print(f"\n❌ Compilation error: {e}")
    # Shows stack trace in debug mode
```

### Fix 4: Debug Output
```python
if self.debug_mode:
    print(f"Starting parser with {len(self.tokens)} tokens...")
    print(f"Parser finished. Errors: {len(self.parser.errors)}")
```

---

## 📋 **Step-by-Step Debugging**

### Step 1: Test the Lexer
```bash
python test_interactive.py
```

Look for "TEST 5: Lexer Only" - should pass.

### Step 2: Test the Parser
Look for "TEST 6: Parser Only" - should pass.

### Step 3: Test Simple Expression
Look for "TEST 1: Simple Expression" - should pass.

### Step 4: Identify the Problem
If any test fails, that's where the issue is.

---

## 🚨 **Still Having Issues?**

### Option 1: Check Python Version
```bash
python --version
# Should be Python 3.7 or higher
```

### Option 2: Verify File Paths
Make sure you're in the project root:
```bash
cd C:\Users\pfigu\CMPE152
python run_interactive.py
```

### Option 3: Check Dependencies
```bash
# No external dependencies needed!
# Uses only Python standard library
```

### Option 4: Try File Mode
Instead of interactive mode:
```bash
python src/compiler.py examples/test1.py
```

This should work without any issues.

---

## 📊 **Expected Behavior**

### ✅ Successful Compilation
```
🔄 Starting compilation process...
================================================================================
📝 Phase 1: Lexical Analysis
----------------------------------------
✓ Tokenization successful: 5 tokens generated

🌳 Phase 2: Syntax Analysis (Parsing)
----------------------------------------
✓ Parsing successful: AST generated

🔍 Phase 3: Semantic Analysis
----------------------------------------
✓ Semantic analysis successful: No errors found

⚙️ Phase 4: Code Generation
----------------------------------------
✓ Code generation successful: 2 instructions generated
✅ Compilation completed successfully!
```

### ⏱️ Should be Fast
- Lexer: < 0.1 seconds
- Parser: < 0.2 seconds
- Semantic: < 0.1 seconds
- CodeGen: < 0.1 seconds
- **Total: < 0.5 seconds for most programs**

If it takes longer than 2 seconds, something is wrong!

---

## 🆘 **Emergency Bypass**

If interactive mode doesn't work at all, you can still use the compiler:

### Method 1: Direct File Compilation
```bash
python src/compiler.py examples/test1.py
```

### Method 2: Python REPL
```python
python
>>> import sys
>>> sys.path.append('src')
>>> from compiler import Compiler
>>> c = Compiler(debug_mode=True)
>>> c.compile_source("x = 10\n")
```

### Method 3: Create a Test File
```python
# test.py
import sys
sys.path.append('src')
from compiler import Compiler

code = """
x = 10
y = 20
print(x + y)
"""

compiler = Compiler(debug_mode=True)
compiler.compile_source(code)
```

---

## 📞 **Report the Issue**

If you're still stuck, gather this info:

1. **Python version:** `python --version`
2. **Operating system:** Windows/Mac/Linux
3. **Code that causes hang:** The exact input
4. **Output before hang:** Last message you see
5. **Debug test results:** Output from `python test_interactive.py`

---

## ✨ **Updates Applied**

Your compiler now has:
- ✅ Infinite loop detection
- ✅ Better error messages
- ✅ Automatic fixes for common issues
- ✅ Debug mode with detailed output
- ✅ Test script for diagnostics

Try it again - it should work much better now! 🚀

---

*Last updated: After adding parser safeguards and debug features*

