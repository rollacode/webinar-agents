#!/usr/bin/env python3
"""
Script to run the AI agent server.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Run the AI agent server."""
    try:
        from agents.server import app

        print("🤖 Starting AI Agent Server...")
        print("📍 Server will be available at: http://localhost:5001")
        print("🎮 Make sure your game is running at: http://localhost:3000")
        print("📋 Available endpoints:")
        print("   POST /api/agent/start - Start the AI agent")
        print("   POST /api/agent/stop - Stop the AI agent")
        print("   GET  /api/agent/status - Get agent status")
        print("   GET  /api/agent/test - Test connection to game")
        print("   POST /api/agent/move - Make a single move")
        print()

        app.run(host="0.0.0.0", port=5001, debug=True)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running with: poetry run agents")
        print("   Or install dependencies with: poetry install")
        sys.exit(1)


if __name__ == "__main__":
    main()
