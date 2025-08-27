#!/usr/bin/env python3
"""
Script to run the frontend development server.
"""

import os
import subprocess
import sys


def main():
    """Run the frontend development server."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "turn-based-game")

    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found!")
        sys.exit(1)

    try:
        print("🚀 Starting frontend development server...")
        subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm.")
        sys.exit(1)


if __name__ == "__main__":
    main()
