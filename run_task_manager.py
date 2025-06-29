#!/usr/bin/env python3
"""Simple script to run the Task Manager CLI."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cli.task_manager_cli import main
    main()
except KeyboardInterrupt:
    print("\nGoodbye!")
except Exception as e:
    print(f"Error starting Task Manager CLI: {e}")
    sys.exit(1) 