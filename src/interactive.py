"""1

Interactive Compiler Mode - REPL for Python Subset Compiler
Allows users to type code dynamically and see compilation results.
"""

import sys
from compiler import Compiler
from lexer import LexicalError
from parser import ParseError
from ast_nodes import ASTPrinter
from x86_codegen import X86CodeGenerator

class InteractiveCompiler:
    """
    Interactive REPL (Read-Eval-Print-Loop) for the compiler.
    Supports multi-line input with proper indentation handling.
    """
    
    def __init__(self):
        self.compiler = Compiler(debug_mode=False)
        self.history = []
        
    def print_banner(self):
        """Print welcome banner."""
        print("=" * 70)
        print("   CMPE 152 Python Subset Compiler - Interactive Mode")
        print("=" * 70)
        print("Type your code below. Commands:")
        print("  :compile  - Compile the entered code")
        print("  :clear    - Clear current code buffer")
        print("  :debug    - Toggle debug mode")
        print("  :help     - Show this help message")
        print("  :exit     - Exit interactive mode")
        print("=" * 70)
        print()
    
    def read_code(self):
        """Read multi-line code from user."""
        print("Enter your code (type :compile when done):")
        print("-" * 70)
        
        lines = []
        line_num = 1
        
        while True:
            try:
                prompt = f"{line_num:3d} | "
                line = input(prompt)
                
                # Check for commands
                if line.strip().startswith(':'):
                    command = line.strip().lower()
                    
                    if command == ':compile':
                        break
                    elif command == ':clear':
                        lines = []
                        line_num = 1
                        print("Code buffer cleared.")
                        continue
                    elif command == ':debug':
                        self.compiler.debug_mode = not self.compiler.debug_mode
                        status = "ON" if self.compiler.debug_mode else "OFF"
                        print(f"Debug mode: {status}")
                        continue
                    elif command == ':help':
                        self.print_banner()
                        continue
                    elif command == ':exit':
                        return None
                    else:
                        print(f"Unknown command: {command}")
                        continue
                
                lines.append(line)
                line_num += 1
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type :exit to quit or :clear to start over.")
                return None
        
        return '\n'.join(lines)
    
    def compile_code(self, source_code):
        """Compile the source code and display results."""
        if not source_code or not source_code.strip():
            print("No code to compile!")
            return False
        
        # Ensure source code ends with newline (required by parser)
        if not source_code.endswith('\n'):
            source_code = source_code + '\n'
        
        print("\n" + "=" * 70)
        print("COMPILING...")
        print("=" * 70)
        
        # Show the code being compiled
        print("\nSource Code:")
        print("-" * 70)
        for i, line in enumerate(source_code.split('\n'), 1):
            if line or i == 1:  # Don't print empty trailing newline
                print(f"{i:3d} | {line}")
        print("-" * 70)
        
        # Compile
        try:
            success = self.compiler.compile_source(source_code)
        except Exception as e:
            print(f"\nCompilation error: {e}")
            import traceback
            if self.compiler.debug_mode:
                traceback.print_exc()
            return False
        
        if success:
            print("\n" + "=" * 70)
            print("COMPILATION SUCCESSFUL")
            print("=" * 70)
            
            # Show summary
            self.show_summary()
            
            # Store in history
            self.history.append((source_code, True))
            return True
        else:
            print("\n" + "=" * 70)
            print("COMPILATION FAILED")
            print("=" * 70)
            self.history.append((source_code, False))
            return False
    
    def show_summary(self):
        """Show an end-to-end view of the compilation, similar to the slide example."""
        comp = self.compiler

        print("\n" + "=" * 70)
        print("End-to-End Compilation Example")
        print("=" * 70)

        # Source Program
        print("\nSource Program\n")
        print("```python")
        if comp.source_code:
            for line in comp.source_code.splitlines():
                print(line)
        print("```")

        # Phase 1 – Tokens
        print("\nPhase 1 – Tokens (Lexer)\n")
        print("```text")
        if comp.tokens:
            # Simple flat list of tokens
            for token in comp.tokens:
                # Avoid trailing comma after EOF for cleanliness
                if token.type.name == "EOF":
                    print(f"{token.type.name}({repr(token.value)})", end="")
                else:
                    print(f"{token.type.name}({repr(token.value)}), ", end="")
        print("\n```")

        # Phase 2 – AST
        print("\nPhase 2 – AST (Parser)\n")
        print("```text")
        if comp.ast:
            printer = ASTPrinter()
            comp.ast.accept(printer)
        else:
            print("No AST (parsing failed).")
        print("```")

        # Phase 3 – Semantics
        print("\nPhase 3 – Semantics\n")
        if comp.semantic_analyzer and len(comp.semantic_analyzer.errors) == 0:
            print("* All variables are declared and initialized before use.")
            print("* All expressions have type-compatible operands.")
            print("* Built-in and user-defined functions are called correctly.")
        elif comp.semantic_analyzer:
            print("* Semantic errors were detected:")
            comp.semantic_analyzer.print_errors()
        else:
            print("* Semantic analysis did not run.")

        # Phase 4 – Generated TAC
        print("\nPhase 4 – Generated TAC\n")
        print("```text")
        if comp.instructions:
            for i, instr in enumerate(comp.instructions, 1):
                print(f"{i}:  {instr}")
        else:
            print("No code generated.")
        print("```")

        # Phase 5 – Approximate x86-64 Assembly
        print("\nPhase 5 – Approximate x86-64 Assembly\n")
        print("```text")
        if comp.instructions:
            x86_gen = X86CodeGenerator(comp.instructions)
            for line in x86_gen.generate():
                print(line)
        else:
            print("No instructions to translate to x86.")
        print("```")
    
    def run_single_expression(self):
        """Quick mode - compile a single expression or statement."""
        print("\n" + "=" * 70)
        print("Quick Mode - Enter a single line of code")
        print("=" * 70)
        
        try:
            code = input(">>> ")
            if not code.strip():
                return
            
            if code.strip().startswith(':'):
                print("Use multi-line mode for commands. Type :exit to quit.")
                return
            
            self.compile_code(code)
            
        except (EOFError, KeyboardInterrupt):
            print("\n")
    
    def run(self):
        """Main REPL loop."""
        self.print_banner()
        
        while True:
            print("\n" + "=" * 70)
            print("Choose mode:")
            print("  1. Multi-line mode (full programs)")
            print("  2. Quick mode (single expressions)")
            print("  3. Load from file")
            print("  4. Show history")
            print("  5. Exit")
            print("=" * 70)
            
            try:
                choice = input("\nEnter choice (1-5): ").strip()
                
                if choice == '1':
                    # Multi-line mode
                    source_code = self.read_code()
                    if source_code is None:
                        continue
                    self.compile_code(source_code)
                
                elif choice == '2':
                    # Quick mode
                    self.run_single_expression()
                
                elif choice == '3':
                    # Load from file
                    filename = input("Enter filename: ").strip()
                    try:
                        with open(filename, 'r') as f:
                            source_code = f.read()
                        print(f"\n✓ Loaded {len(source_code)} characters from {filename}")
                        self.compile_code(source_code)
                    except FileNotFoundError:
                        print(f"File not found: {filename}")
                    except Exception as e:
                        print(f"Error reading file: {e}")
                
                elif choice == '4':
                    # Show history
                    if not self.history:
                        print("\nNo compilation history yet.")
                    else:
                        print("\nCompilation History:")
                        print("-" * 70)
                        for i, (code, success) in enumerate(self.history, 1):
                            status = "SUCCESS" if success else "FAILED"
                            preview = code[:50].replace('\n', ' ')
                            if len(code) > 50:
                                preview += "..."
                            print(f"  {i}. [{status}] {preview}")
                
                elif choice == '5' or choice.lower() == 'exit':
                    # Exit
                    print("\nThanks for using CMPE 152 Compiler!")
                    print("=" * 70)
                    break

                else:
                    print("Invalid choice. Please enter 1-5.")

            except (EOFError, KeyboardInterrupt):
                print("\n\nThanks for using CMPE 152 Compiler!")
                print("=" * 70)
                break
            except Exception as e:
                print(f"\nUnexpected error: {e}")
                import traceback
                traceback.print_exc()

def main():
    """Entry point for interactive compiler."""
    repl = InteractiveCompiler()
    repl.run()

if __name__ == "__main__":
    main()

