#!/usr/bin/env python3
"""
Power Systems IDS Demo (Deprecated - use demo_improved.py instead)
"""

import warnings
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

warnings.warn(
    "demo.py is deprecated. Please use demo_improved.py instead. "
    "This script will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and run demo_improved
from demo_improved import main

if __name__ == "__main__":
    main()
