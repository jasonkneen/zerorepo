#!/usr/bin/env python3
"""
ZeroRepo CLI Entry Point

Usage:
    python zerorepo_cli.py plan --goal "Generate ML toolkit"
    python zerorepo_cli.py generate --goal "Build web app"
    python zerorepo_cli.py --help
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zerorepo.cli.main import app

if __name__ == "__main__":
    app()