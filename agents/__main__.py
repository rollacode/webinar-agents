"""
Main entry point for the agents package.
"""

import asyncio
import os
import sys

from .simple_agent import SimpleAgent


def main():
    """Main entry point for running the agent."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("💡 Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   Or create a .env file with: OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)

    print("🤖 Starting SimpleAgent...")
    print("🎮 Make sure your game is running at: http://localhost:3000")

    agent = SimpleAgent(api_key=api_key)

    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
        agent.stop()
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
