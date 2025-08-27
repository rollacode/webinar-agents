"""
Example usage of the Combat Agent.
This script demonstrates how to use the AI agent to control the game character.
"""

import os

from .combat_agent import CombatAgent
from .game_client import GameClient


def main():
    # Initialize the combat agent
    # Note: You'll need to set OPENAI_API_KEY environment variable for LLM features
    api_key = os.getenv("OPENAI_API_KEY")
    agent = CombatAgent(api_key=api_key)

    print("🎮 Starting Combat Agent Demo")
    print("=" * 40)

    # Test basic game connection
    print("Testing game connection...")
    scan_result = agent.game_client.scan_field()

    if not scan_result.get("success"):
        print(
            "❌ Failed to connect to game. Make sure the Next.js server is running on http://localhost:3000"
        )
        return

    print("✅ Connected to game successfully!")

    # Display initial game state
    if "data" in scan_result:
        data = scan_result["data"]
        player_pos = data.get("playerPosition", {})
        enemies = data.get("nearbyCharacters", [])

        print(
            f"📍 Player position: ({player_pos.get('x', 0)}, {player_pos.get('y', 0)})"
        )
        print(f"👹 Enemies nearby: {len(enemies)}")

        for i, enemy in enumerate(enemies):
            pos = enemy["position"]
            print(
                f"   Enemy {i + 1}: {enemy['name']} at ({pos['x']}, {pos['y']}) - HP: {enemy['health']}"
            )

    print("\n🤖 Running autonomous combat agent...")
    print("-" * 40)

    # Run the agent for a few turns
    results = agent.run_autonomous(max_turns=5)

    for result in results:
        print(f"Turn {result['turn']}: {result['action']}")
        if result["result"].get("success"):
            print(f"  ✅ {result['result'].get('data', {}).get('message', 'Success')}")
        else:
            print(f"  ❌ {result['result'].get('error', 'Unknown error')}")

    print("\n🏁 Demo completed!")


def test_manual_commands():
    """Test manual commands without the AI agent."""
    print("\n🕹️  Testing Manual Commands")
    print("=" * 40)

    client = GameClient()

    # Test scan
    print("Scanning field...")
    result = client.scan_field()
    print(f"Scan result: {result.get('success', False)}")

    # Test movement
    print("Moving right...")
    result = client.move_character("right")
    print(f"Move result: {result.get('success', False)}")

    # Test another scan to see position change
    print("Scanning after move...")
    result = client.scan_field()
    if result.get("success") and "data" in result:
        pos = result["data"].get("playerPosition", {})
        print(f"New position: ({pos.get('x', 0)}, {pos.get('y', 0)})")


if __name__ == "__main__":
    print("🚀 Combat Agent Example")
    print("Make sure to start the Next.js game server first:")
    print("  cd turn-based-game && npm run dev")
    print()

    # Test manual commands first
    test_manual_commands()

    # Then run the full AI agent demo
    main()
