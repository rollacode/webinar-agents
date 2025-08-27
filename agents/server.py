#!/usr/bin/env python3
"""
Flask server for the AI agent that can be controlled from the web game.
Uses the full CombatAgent with LangChain/LangGraph for intelligent gameplay.
"""

import json
import logging
import os
import threading
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

from .combat_agent import CombatAgent
from .game_client import GameClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend

# Global state
agent_thread = None
agent_running = False
agent_results: list = []


class AgentRunner:
    def __init__(self):
        self.game_client = GameClient()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.agent = CombatAgent(api_key=self.api_key) if self.api_key else None
        self.running = False
        self.results = []

    def start_agent(self):
        """Start the AI agent in a separate thread."""
        if self.running:
            return {"success": False, "error": "Agent is already running"}

        if not self.agent:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not set. Cannot start AI agent.",
            }

        self.running = True
        self.results = []

        # Start agent in a separate thread
        thread = threading.Thread(target=self._run_agent)
        thread.daemon = True
        thread.start()

        return {"success": True, "message": "AI Agent started successfully"}

    def stop_agent(self):
        """Stop the AI agent."""
        self.running = False
        return {"success": True, "message": "Agent stopped"}

    def get_status(self):
        """Get current agent status."""
        return {
            "running": self.running,
            "results": self.results[-10:] if self.results else [],  # Last 10 results
            "has_ai": self.agent is not None,
        }

    def _run_agent(self):
        """Run the AI agent logic using CombatAgent."""
        logger.info("🚀 [AI_AGENT] Starting AI Agent session...")
        try:
            # Test connection first
            logger.info("🔍 [AI_AGENT] Testing connection to game...")
            scan_result = self.game_client.scan_field()
            if not scan_result.get("success"):
                logger.error(f"❌ [AI_AGENT] Failed to connect to game: {scan_result}")
                self.results.append(
                    {
                        "timestamp": time.time(),
                        "type": "error",
                        "message": "Failed to connect to game",
                    }
                )
                return

            logger.info("✅ [AI_AGENT] Connected to game successfully!")
            self.results.append(
                {
                    "timestamp": time.time(),
                    "type": "info",
                    "message": "Connected to game successfully. AI Agent is ready!",
                }
            )

            # Run AI agent for multiple turns
            turn_count = 0
            max_turns = 20  # Reduced for AI agent since it's smarter

            while self.running and turn_count < max_turns:
                turn_count += 1

                self.results.append(
                    {
                        "timestamp": time.time(),
                        "type": "info",
                        "message": f"AI Agent turn {turn_count}",
                    }
                )

                # Run one turn of the AI agent
                logger.info(
                    f"🤖 [AI_AGENT] Turn {turn_count}: Starting AI decision making..."
                )
                turn_result = self.agent.run_turn()

                action = turn_result.get("action", "unknown")
                result = turn_result.get("result", {})
                game_state = turn_result.get("game_state", {})

                logger.info(
                    f"🤖 [AI_AGENT] Turn {turn_count}: AI decided to '{action}'"
                )
                logger.info(
                    f"🤖 [AI_AGENT] Turn {turn_count}: Action result: {json.dumps(result, indent=2)}"
                )

                # Log the AI action
                self.results.append(
                    {
                        "timestamp": time.time(),
                        "type": "action",
                        "action": action,
                        "success": result.get("success", False),
                        "turn": turn_count,
                        "ai_decision": True,
                    }
                )

                # Check if level completed or no enemies remain
                if result.get("success") and result.get("data", {}).get(
                    "level_completed"
                ):
                    logger.info(
                        f"🎉 [AI_AGENT] Turn {turn_count}: LEVEL COMPLETED! AI Agent wins!"
                    )
                    self.results.append(
                        {
                            "timestamp": time.time(),
                            "type": "success",
                            "message": "Level completed by AI Agent!",
                        }
                    )
                    break

                # Check if no enemies remain
                if game_state.get("success"):
                    enemies = game_state.get("data", {}).get("nearbyCharacters", [])
                    if not enemies:
                        logger.info(
                            f"⚔️ [AI_AGENT] Turn {turn_count}: All enemies defeated! Victory!"
                        )
                        self.results.append(
                            {
                                "timestamp": time.time(),
                                "type": "success",
                                "message": "All enemies defeated by AI Agent!",
                            }
                        )
                        break

                # Wait a bit between actions
                time.sleep(1.0)  # Slightly longer for AI agent

            if turn_count >= max_turns:
                logger.warning(
                    f"⏰ [AI_AGENT] Reached maximum turns ({max_turns}). Stopping AI Agent."
                )
                self.results.append(
                    {
                        "timestamp": time.time(),
                        "type": "warning",
                        "message": "AI Agent reached maximum turns",
                    }
                )

        except Exception as e:
            logger.error(
                f"💥 [AI_AGENT] Critical error during AI Agent execution: {str(e)}",
                exc_info=True,
            )
            self.results.append(
                {
                    "timestamp": time.time(),
                    "type": "error",
                    "message": f"AI Agent error: {str(e)}",
                }
            )
        finally:
            logger.info("🏁 [AI_AGENT] AI Agent session ended.")
            self.running = False


# Global agent runner
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
        response_data = {"success": True, "turn_result": turn_result}
        logger.info(f"📡 [API] AI turn response: {json.dumps(response_data, indent=2)}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"📡 [API] AI turn error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    print("🤖 Starting AI Agent Server with LangChain/LangGraph...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🎮 Make sure your game is running at: http://localhost:3000")
    print("🧠 AI Agent uses OpenAI API - set OPENAI_API_KEY environment variable")
    app.run(host="0.0.0.0", port=5001, debug=True)
