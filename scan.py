#!/usr/bin/env python3
import sys
import os

# Add the current directory to sys.path so we can import the 'src' package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.main import main
except ImportError as e:
    print(f"Error: Could not import application modules. {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
