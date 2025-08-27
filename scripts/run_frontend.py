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
        print(f"   Expected path: {frontend_dir}")
        sys.exit(1)

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found")
        print("📦 Please install Node.js and npm from: https://nodejs.org/")
        sys.exit(1)

    # Check if dependencies are installed
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)

    try:
        print("🚀 Starting frontend development server...")
        print("📍 Server will be available at: http://localhost:3000")
        subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
