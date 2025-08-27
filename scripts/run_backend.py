#!/usr/bin/env python3
"""
Simple script to run the backend.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.game_client import GameClient


def main():
    """Simple backend test."""
    print("🚀 Starting Backend Test")
    print("=" * 40)

    # Test basic game connection
    print("Testing game connection...")
    client = GameClient()
    scan_result = client.scan_field()

    if not scan_result.get("success"):
        print(
            "❌ Failed to connect to game. Make sure the Next.js server is running on http://localhost:3000"
        )
        print("💡 Run: poetry run frontend")
        return

    print("✅ Connected to game successfully!")

    # Display initial game state
    if "data" in scan_result:
        data = scan_result["data"]
        position = data.get("position", {})
        agents = data.get("agents", [])
        available_actions = data.get("available_actions", [])

        print(f"📍 Player position: ({position.get('x', 0)}, {position.get('y', 0)})")
        print(f"🤖 Agents: {len(agents)}")
        print(f"🎯 Available actions: {', '.join(available_actions)}")

        for i, agent in enumerate(agents):
            if isinstance(agent, dict) and "position" in agent:
                pos = agent["position"]
                print(f"   Agent {i + 1}: at ({pos['x']}, {pos['y']})")
            else:
                print(f"   Agent {i + 1}: {agent}")

    print("\n🏁 Backend test completed!")


if __name__ == "__main__":
    main()
