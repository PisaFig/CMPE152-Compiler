# 🚀 Quick Start - Interactive Compiler

## Launch in 3 Seconds

```bash
python run_interactive.py
```

That's it! Now you can type code and compile it instantly.

---

## 🎯 Try These Examples

### Example 1: Simple Math (30 seconds)

1. Run: `python run_interactive.py`
2. Choose: `2` (Quick mode)
3. Type: `x = 10 + 20 * 2`
4. See compilation results instantly!

```
>>> x = 10 + 20 * 2
✅ COMPILATION SUCCESSFUL!
📊 Compilation Summary:
  • Tokens generated: 8
  • Instructions generated: 3

📝 Generated Code:
  1: t1 = 20 * 2
  2: t2 = 10 + t1
  3: x = t2
```

---

### Example 2: If Statement (1 minute)

1. Choose: `1` (Multi-line mode)
2. Type this code:

```python
  1 | score = 85
  2 | if score >= 80:
  3 |     grade = "B"
  4 | else:
  5 |     grade = "F"
  6 | :compile
```

3. Watch your code compile through all 4 phases!

---

### Example 3: Function (2 minutes)

```python
  1 | def add(a, b):
  2 |     result = a + b
  3 |     return result
  4 | 
  5 | x = add(5, 10)
  6 | print(x)
  7 | :compile
```

You'll see:
- ✅ Lexical analysis
- ✅ Syntax analysis (AST)
- ✅ Semantic analysis
- ✅ Code generation

---

## 🎮 Controls

### While Typing (Multi-line mode):
- **:compile** → Compile your code
- **:clear** → Start over
- **:debug** → See detailed output
- **:exit** → Return to menu

### Main Menu:
- **1** → Write full programs
- **2** → Test quick expressions
- **3** → Load .py files
- **4** → View history
- **5** → Exit

---

## 💡 Pro Tips

### Tip 1: Start with Quick Mode
Perfect for testing single lines:
```
>>> y = 5 + 3
>>> name = "CMPE 152"
>>> result = 10 ** 2
```

### Tip 2: Use Debug Mode
Type `:debug` to see:
- Every token generated
- Complete AST structure
- Symbol table contents
- All instructions

### Tip 3: Learn from Examples
Load the provided test files:
```
Choose mode: 3
Enter filename: examples/test1.py
```

---

## 🏆 What You Get

Every compilation shows:

✅ **Phase 1**: Tokens (Lexical Analysis)
```
INTEGER(10), PLUS(+), INTEGER(5) ...
```

✅ **Phase 2**: AST (Syntax Analysis)
```
Program:
  Assignment: x =
    Binary Op: PLUS
      Literal: 10
      Literal: 5
```

✅ **Phase 3**: Semantic Check
```
✓ No type errors
✓ All variables defined
✓ Scope resolution correct
```

✅ **Phase 4**: Generated Code
```
1: t1 = 10 + 5
2: x = t1
```

---

## 🎓 Perfect For

- ✏️ Testing homework examples
- 🔬 Understanding compiler phases
- 🐛 Debugging code snippets
- 📊 Demonstrating for presentations
- 🎯 Learning by experimentation

---

## ⚡ Common Use Cases

### Test an expression:
```bash
$ python run_interactive.py
Choose: 2
>>> (5 + 3) * 2
```

### Write a loop:
```bash
Choose: 1
counter = 5
while counter > 0:
    print(counter)
    counter = counter - 1
:compile
```

### Test a function:
```bash
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
        
result = factorial(5)
:compile
```

---

## 🚨 Need Help?

- **Can't find Python?** → Make sure Python 3 is installed
- **Import errors?** → Run from project root directory
- **Indentation errors?** → Use 4 spaces per indent level
- **Want more details?** → See [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md)

---

## 🎉 You're Ready!

Just run:
```bash
python run_interactive.py
```

And start compiling! 🚀

---

*Part of CMPE 152 Compiler Design Project - San José State University*

