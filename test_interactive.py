"""
Debug script for testing interactive compiler issues
Run this to test the compiler with various inputs
"""

import sys
sys.path.insert(0, 'src')

from compiler import Compiler

def test_simple_expression():
    """Test a simple expression"""
    print("=" * 70)
    print("TEST 1: Simple Expression")
    print("=" * 70)
    
    code = "x = 10\n"
    compiler = Compiler(debug_mode=True)
    
    print(f"Testing code: {repr(code)}")
    result = compiler.compile_source(code)
    
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    print("=" * 70)
    return result

def test_expression_with_operator():
    """Test expression with operators"""
    print("\n" + "=" * 70)
    print("TEST 2: Expression with Operators")
    print("=" * 70)
    
    code = "x = 5 + 10\n"
    compiler = Compiler(debug_mode=True)
    
    print(f"Testing code: {repr(code)}")
    result = compiler.compile_source(code)
    
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    print("=" * 70)
    return result

def test_print_statement():
    """Test print statement"""
    print("\n" + "=" * 70)
    print("TEST 3: Print Statement")
    print("=" * 70)
    
    code = 'print("hello")\n'
    compiler = Compiler(debug_mode=True)
    
    print(f"Testing code: {repr(code)}")
    result = compiler.compile_source(code)
    
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    print("=" * 70)
    return result

def test_if_statement():
    """Test if statement"""
    print("\n" + "=" * 70)
    print("TEST 4: If Statement")
    print("=" * 70)
    
    code = """x = 10
if x > 5:
    print("big")
"""
    compiler = Compiler(debug_mode=True)
    
    print(f"Testing code: {repr(code)}")
    result = compiler.compile_source(code)
    
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    print("=" * 70)
    return result

def test_tokens_only():
    """Test just the lexer"""
    print("\n" + "=" * 70)
    print("TEST 5: Lexer Only")
    print("=" * 70)
    
    from lexer import Lexer
    
    code = "x = 5 + 10\n"
    print(f"Testing code: {repr(code)}")
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        print(f"\nTokens generated: {len(tokens)}")
        for i, token in enumerate(tokens, 1):
            print(f"  {i:2d}. {token.type.name:15s} {repr(token.value):15s} Line {token.line}:{token.column}")
        
        print("\nLexer: SUCCESS")
        return True
    except Exception as e:
        print(f"\nLexer: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parser_only():
    """Test just the parser"""
    print("\n" + "=" * 70)
    print("TEST 6: Parser Only")
    print("=" * 70)
    
    from lexer import Lexer
    from parser import Parser
    
    code = "x = 5 + 10\n"
    print(f"Testing code: {repr(code)}")
    
    try:
        # Tokenize
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print(f"Tokens: {len(tokens)} generated")
        
        # Parse
        parser = Parser(tokens)
        print("Starting parse...")
        ast = parser.parse()
        
        if ast:
            print(f"AST generated with {len(ast.statements)} statements")
            print("Parser: SUCCESS")
            return True
        else:
            print("Parser returned None")
            parser.print_errors()
            return False
    except Exception as e:
        print(f"\nParser: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Interactive Compiler Debug Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Lexer Only", test_tokens_only),
        ("Parser Only", test_parser_only),
        ("Simple Expression", test_simple_expression),
        ("Expression with Operators", test_expression_with_operator),
        ("Print Statement", test_print_statement),
        ("If Statement", test_if_statement),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print("=" * 70)

if __name__ == "__main__":
    main()

