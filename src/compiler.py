"""
Main Compiler Driver for Python Subset Compiler
Coordinates all compilation phases: lexical analysis, parsing, semantic analysis, and code generation.
"""

import sys
import os
from typing import Optional, List
from lexer import Lexer, LexicalError
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
from codegen import CodeGenerator
from ast_nodes import ASTPrinter

class CompilerError(Exception):
    """Base exception for compiler errors."""
    pass

class Compiler:
    """
    Main compiler class that orchestrates all compilation phases.
    Demonstrates the complete compilation pipeline for CMPE 152.
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.source_file = None
        self.source_code = None
        
        # Compilation phases
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = None
        self.code_generator = None
        
        # Results
        self.tokens = []
        self.ast = None
        self.instructions = []
        
    def compile_file(self, filename: str) -> bool:
        """Compile a source file through all phases."""
        try:
            # Read source file
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' not found.")
                return False
            
            with open(filename, 'r') as f:
                self.source_code = f.read()
            
            self.source_file = filename
            return self.compile_source(self.source_code)
            
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            return False
    
    def compile_source(self, source_code: str) -> bool:
        """Compile source code through all phases."""
        self.source_code = source_code
        
        print("🔄 Starting compilation process...")
        print("=" * 80)
        
        # Phase 1: Lexical Analysis
        if not self._lexical_analysis():
            return False
        
        # Phase 2: Syntax Analysis (Parsing)
        if not self._syntax_analysis():
            return False
        
        # Phase 3: Semantic Analysis
        if not self._semantic_analysis():
            return False
        
        # Phase 4: Code Generation
        if not self._code_generation():
            return False
        
        print("✅ Compilation completed successfully!")
        return True
    
    def _lexical_analysis(self) -> bool:
        """Perform lexical analysis."""
        print("📝 Phase 1: Lexical Analysis")
        print("-" * 40)
        
        try:
            self.lexer = Lexer(self.source_code)
            self.tokens = self.lexer.tokenize()
            
            print(f"✓ Tokenization successful: {len(self.tokens)} tokens generated")
            
            if self.debug_mode:
                self.lexer.print_tokens()
            
            return True
            
        except LexicalError as e:
            print(f"❌ Lexical Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error in lexical analysis: {e}")
            return False
    
    def _syntax_analysis(self) -> bool:
        """Perform syntax analysis (parsing)."""
        print("\n🌳 Phase 2: Syntax Analysis (Parsing)")
        print("-" * 40)
        
        try:
            self.parser = Parser(self.tokens)
            
            if self.debug_mode:
                print(f"Starting parser with {len(self.tokens)} tokens...")
            
            self.ast = self.parser.parse()
            
            if self.debug_mode:
                print(f"Parser finished. Errors: {len(self.parser.errors)}")
            
            if self.ast and len(self.parser.errors) == 0:
                print("✓ Parsing successful: AST generated")
                
                if self.debug_mode:
                    print(f"AST has {len(self.ast.statements)} statements")
                    print("\nAbstract Syntax Tree:")
                    printer = ASTPrinter()
                    self.ast.accept(printer)
                
                return True
            else:
                print("❌ Parsing failed:")
                if self.parser.errors:
                    self.parser.print_errors()
                else:
                    print("Parser returned None without specific errors")
                return False
                
        except ParseError as e:
            print(f"❌ Parse Error: {e}")
            import traceback
            if self.debug_mode:
                traceback.print_exc()
            return False
        except Exception as e:
            print(f"❌ Unexpected error in syntax analysis: {e}")
            import traceback
            if self.debug_mode:
                traceback.print_exc()
            return False
    
    def _semantic_analysis(self) -> bool:
        """Perform semantic analysis."""
        print("\n🔍 Phase 3: Semantic Analysis")
        print("-" * 40)
        
        try:
            self.semantic_analyzer = SemanticAnalyzer()
            success = self.semantic_analyzer.analyze(self.ast)
            
            if success:
                print("✓ Semantic analysis successful: No errors found")
                
                if self.debug_mode:
                    print("\nSymbol Table:")
                    self.semantic_analyzer.print_symbol_table()
                
                return True
            else:
                print("❌ Semantic analysis failed:")
                self.semantic_analyzer.print_errors()
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error in semantic analysis: {e}")
            return False
    
    def _code_generation(self) -> bool:
        """Perform code generation."""
        print("\n⚙️ Phase 4: Code Generation")
        print("-" * 40)
        
        try:
            self.code_generator = CodeGenerator()
            self.instructions = self.code_generator.generate(self.ast)
            
            print(f"✓ Code generation successful: {len(self.instructions)} instructions generated")
            
            if self.debug_mode:
                self.code_generator.print_code()
            
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error in code generation: {e}")
            return False
    
    def save_output(self, output_dir: str = "output"):
        """Save compilation results to output directory."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(self.source_file))[0] if self.source_file else "output"
        
        # Save tokens
        if self.tokens:
            token_file = os.path.join(output_dir, f"{base_name}_tokens.txt")
            with open(token_file, 'w') as f:
                f.write("LEXICAL ANALYSIS RESULTS\n")
                f.write("=" * 60 + "\n")
                f.write(f"{'Token Type':<15} {'Value':<15} {'Line':<6} {'Column':<6}\n")
                f.write("-" * 60 + "\n")
                
                for token in self.tokens:
                    f.write(f"{token.type.name:<15} {str(token.value):<15} {token.line:<6} {token.column:<6}\n")
                
                f.write("=" * 60 + "\n")
                f.write(f"Total tokens: {len(self.tokens)}\n")
        
        # Save AST
        if self.ast:
            ast_file = os.path.join(output_dir, f"{base_name}_ast.txt")
            with open(ast_file, 'w') as f:
                import io
                from contextlib import redirect_stdout
                
                f.write("ABSTRACT SYNTAX TREE\n")
                f.write("=" * 60 + "\n")
                
                # Capture AST printer output
                ast_output = io.StringIO()
                with redirect_stdout(ast_output):
                    printer = ASTPrinter()
                    self.ast.accept(printer)
                
                f.write(ast_output.getvalue())
        
        # Save symbol table
        if self.semantic_analyzer:
            symbol_file = os.path.join(output_dir, f"{base_name}_symbols.txt")
            with open(symbol_file, 'w') as f:
                import io
                from contextlib import redirect_stdout
                
                symbol_output = io.StringIO()
                with redirect_stdout(symbol_output):
                    self.semantic_analyzer.print_symbol_table()
                
                f.write(symbol_output.getvalue())
        
        # Save generated code
        if self.code_generator:
            code_file = os.path.join(output_dir, f"{base_name}_code.txt")
            self.code_generator.save_code(code_file)
        
        print(f"\n📁 Output files saved to '{output_dir}/' directory")
    
    def print_summary(self):
        """Print compilation summary."""
        print("\n" + "=" * 80)
        print("COMPILATION SUMMARY")
        print("=" * 80)
        
        if self.source_file:
            print(f"Source file: {self.source_file}")
        
        print(f"Lexical Analysis: {'✓ PASSED' if self.tokens else '❌ FAILED'}")
        print(f"Syntax Analysis:  {'✓ PASSED' if self.ast else '❌ FAILED'}")
        print(f"Semantic Analysis: {'✓ PASSED' if self.semantic_analyzer and len(self.semantic_analyzer.errors) == 0 else '❌ FAILED'}")
        print(f"Code Generation:  {'✓ PASSED' if self.instructions else '❌ FAILED'}")
        
        if self.tokens:
            print(f"\nStatistics:")
            print(f"  Tokens generated: {len(self.tokens)}")
        
        if self.instructions:
            print(f"  Instructions generated: {len(self.instructions)}")
        
        if self.semantic_analyzer:
            print(f"  Semantic errors: {len(self.semantic_analyzer.errors)}")
        
        print("=" * 80)

def print_usage():
    """Print usage instructions."""
    print("Python Subset Compiler - CMPE 152 Project")
    print("=" * 50)
    print("Usage:")
    print("  python compiler.py <source_file> [options]")
    print("  python compiler.py -i                     (interactive mode)")
    print("\nOptions:")
    print("  -i, --interactive  Launch interactive REPL mode")
    print("  -d, --debug        Enable debug mode (verbose output)")
    print("  -o, --output       Specify output directory (default: output/)")
    print("  -h, --help         Show this help message")
    print("\nExamples:")
    print("  python compiler.py examples/test1.py")
    print("  python compiler.py examples/test2.py --debug")
    print("  python compiler.py examples/test3.py -o results/")
    print("  python compiler.py -i                    # Interactive mode")

def main():
    """Main function for command-line interface."""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    # Parse command line arguments
    source_file = None
    debug_mode = False
    output_dir = "output"
    interactive_mode = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-h', '--help']:
            print_usage()
            return 0
        elif arg in ['-i', '--interactive']:
            interactive_mode = True
        elif arg in ['-d', '--debug']:
            debug_mode = True
        elif arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_dir = sys.argv[i + 1]
                i += 1
            else:
                print("Error: --output requires a directory name")
                return 1
        elif not arg.startswith('-'):
            source_file = arg
        else:
            print(f"Error: Unknown option '{arg}'")
            print_usage()
            return 1
        
        i += 1
    
    # Check for interactive mode
    if interactive_mode:
        try:
            from interactive import InteractiveCompiler
            repl = InteractiveCompiler()
            repl.run()
            return 0
        except ImportError:
            print("Error: Interactive mode not available. Missing interactive.py")
            return 1
        except Exception as e:
            print(f"Error in interactive mode: {e}")
            return 1
    
    if not source_file:
        print("Error: No source file specified")
        print_usage()
        return 1
    
    # Create and run compiler
    compiler = Compiler(debug_mode=debug_mode)
    
    if compiler.compile_file(source_file):
        compiler.save_output(output_dir)
        compiler.print_summary()
        return 0
    else:
        print("\n❌ Compilation failed!")
        compiler.print_summary()
        return 1

if __name__ == "__main__":
    sys.exit(main())