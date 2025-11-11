#!/usr/bin/env python3
"""
Quick launcher for Interactive Compiler Mode
Run this file to start typing and compiling code dynamically!
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interactive import InteractiveCompiler

if __name__ == "__main__":
    print("🚀 Launching CMPE 152 Interactive Compiler...\n")
    repl = InteractiveCompiler()
    repl.run()

