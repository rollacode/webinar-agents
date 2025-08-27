#!/usr/bin/env python3
"""
Flask server for the AI agent that can be controlled from the web game.
Uses the SimpleAgent with LangChain/LangGraph for intelligent gameplay.
"""

import asyncio
import json
import logging
import os
import threading
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

from .game_client import GameClient
from .simple_agent import SimpleAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend

# Global state
agent_thread = None
agent_results: list = []


class AgentRunner:
    def __init__(self):
        self.game_client = GameClient()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.agent = SimpleAgent(api_key=self.api_key) if self.api_key else None
        self.results = []

    def start_agent(self):
        """Start the AI agent in a separate thread."""
        if not self.agent:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not set. Cannot start AI agent.",
            }

        self.results = []

        thread = threading.Thread(target=self._run_agent)
        thread.daemon = True
        thread.start()

        return {"success": True, "message": "AI Agent started successfully"}

    def stop_agent(self):
        """Stop the AI agent."""
        self.agent.stop()
        return {"success": True, "message": "Agent stopped"}

    def get_status(self):
        """Get current agent status."""
        return {
            "running": self.agent.running,
            "results": self.results[-10:] if self.results else [],  # Last 10 results
            "has_ai": self.agent is not None,
        }

    def _run_agent(self):
        logger.info("✅ [AI_AGENT] Connected to game successfully!")
        self.results.append(
            {
                "timestamp": time.time(),
                "type": "info",
                "message": "Connected to game successfully. AI Agent is ready!",
            }
        )

        asyncio.run(self.agent.run())
        self.results.append(
            {
                "timestamp": time.time(),
                "type": "info",
                "message": "AI Agent execution completed",
            }
        )


agent_runner = AgentRunner()


@app.route("/api/agent/start", methods=["POST"])
def start_agent():
    """Start the AI agent."""
    logger.info("📡 [API] Received request to start AI agent")
    result = agent_runner.start_agent()
    logger.info(f"📡 [API] Start agent response: {json.dumps(result, indent=2)}")
    return jsonify(result)


@app.route("/api/agent/stop", methods=["POST"])
def stop_agent():
    """Stop the AI agent."""
    logger.info("📡 [API] Received request to stop AI agent")
    result = agent_runner.stop_agent()
    logger.info(f"📡 [API] Stop agent response: {json.dumps(result, indent=2)}")
    return jsonify(result)


@app.route("/api/agent/status", methods=["GET"])
def get_agent_status():
    """Get the current agent status."""
    result = agent_runner.get_status()
    return jsonify(result)


@app.route("/api/agent/test", methods=["GET"])
def test_connection():
    """Test connection to the game."""
    try:
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/agent/move", methods=["POST"])
def make_move():
    """Make a single move."""
    try:
        data = request.get_json()
        direction = data.get("direction")
        logger.info(f"📡 [API] Received manual move request: direction='{direction}'")

        if not direction:
            logger.warning("📡 [API] Move request missing direction parameter")
            return jsonify({"success": False, "error": "Direction required"})

        client = GameClient()
        result = client.move_character(direction)

        response_data = {"success": True, "move_result": result}
        logger.info(f"📡 [API] Move response: {json.dumps(response_data, indent=2)}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"📡 [API] Move error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/agent/ai-turn", methods=["POST"])
def ai_single_turn():
    """Run a single AI agent turn."""
    logger.info("📡 [API] Received request for single AI turn")
    try:
        if not agent_runner.agent:
            logger.warning("📡 [API] AI agent not available - missing OPENAI_API_KEY")
            return jsonify(
                {
                    "success": False,
                    "error": "AI Agent not available. Set OPENAI_API_KEY.",
                }
            )

        turn_result = agent_runner.agent.run_turn()
        response_data = {
            "success": True,
            "turn_result": turn_result,
            "action": turn_result.get("action"),
            "result": turn_result.get("result"),
            "objective": turn_result.get("objective"),
        }
        logger.info(
            f"📡 [API] AI turn response: Action='{turn_result.get('action')}', Objective='{turn_result.get('objective')}'"
        )
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"📡 [API] AI turn error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/agent/run-autonomous", methods=["POST"])
def run_autonomous():
    """Run the AI agent autonomously until level completion."""
    logger.info("📡 [API] Received request for autonomous run")
    try:
        if not agent_runner.agent:
            logger.warning("📡 [API] AI agent not available - missing OPENAI_API_KEY")
            return jsonify(
                {
                    "success": False,
                    "error": "AI Agent not available. Set OPENAI_API_KEY.",
                }
            )

        # Get max_turns from request, default to 20
        data = request.get_json() or {}
        max_turns = data.get("max_turns", 20)

        logger.info(f"📡 [API] Starting autonomous run with max {max_turns} turns")
        results = agent_runner.agent.run_until_completion(max_turns=max_turns)

        # Get final status
        final_result = results[-1] if results else {}
        final_objective = final_result.get("objective", "unknown")

        response_data = {
            "success": True,
            "results": results,
            "total_turns": len(results),
            "final_objective": final_objective,
            "level_completed": final_objective == "completed",
        }

        logger.info(
            f"📡 [API] Autonomous run completed: {len(results)} turns, final objective: '{final_objective}'"
        )
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"📡 [API] Autonomous run error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    print("🤖 Starting SimpleAgent Server with LangChain/LangGraph...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🎮 Make sure your game is running at: http://localhost:3000")
    print("🧠 SimpleAgent uses OpenAI API - set OPENAI_API_KEY environment variable")
    print(
        "🎯 SimpleAgent can navigate levels, use computers, activate bridges, and switch agents"
    )
    app.run(host="0.0.0.0", port=5001, debug=True)
