"""
Combat Agent for controlling the game character using LangChain and LangGraph.
"""

import json
from typing import Any, Dict, List

from langchain.schema import BaseMessage
from langchain.tools import BaseTool
from langchain_community.llms import OpenAI
from langgraph.graph import END, StateGraph

from .game_client import GameClient


class GameState:
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.game_data: Dict[str, Any] = {}
        self.last_action: str = ""
        self.action_result: Dict[str, Any] = {}


class GameMoveTool(BaseTool):
    name = "move_character"
    description = "Move the character in a direction (up, down, left, right)"

    def __init__(self, game_client: GameClient):
        self.game_client = game_client
        super().__init__()

    def _run(self, direction: str) -> str:
        result = self.game_client.move_character(direction)
        return json.dumps(result)

    async def _arun(self, direction: str) -> str:
        return self._run(direction)


class GameAttackTool(BaseTool):
    name = "attack_target"
    description = "Attack a target at specific coordinates (x, y)"

    def __init__(self, game_client: GameClient):
        self.game_client = game_client
        super().__init__()

    def _run(self, x: int, y: int) -> str:
        result = self.game_client.attack_target(x, y)
        return json.dumps(result)

    async def _arun(self, x: int, y: int) -> str:
        return self._run(x, y)


class GameScanTool(BaseTool):
    name = "scan_field"
    description = "Scan the game field for enemies, obstacles, and current state"

    def __init__(self, game_client: GameClient):
        self.game_client = game_client
        super().__init__()

    def _run(self) -> str:
        result = self.game_client.scan_field()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()


class CombatAgent:
    def __init__(
        self, api_key: str = None, game_url: str = "http://localhost:3000/api"
    ):
        self.game_client = GameClient(game_url)
        self.llm = OpenAI(api_key=api_key) if api_key else None

        # Create tools
        self.tools = [
            GameMoveTool(self.game_client),
            GameAttackTool(self.game_client),
            GameScanTool(self.game_client),
        ]

        # Create the state graph
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph for the combat agent."""
        graph = StateGraph(GameState)

        # Add nodes
        graph.add_node("analyze", self._analyze_situation)
        graph.add_node("decide_action", self._decide_action)
        graph.add_node("execute_action", self._execute_action)
        graph.add_node("evaluate_result", self._evaluate_result)

        # Add edges
        graph.add_edge("analyze", "decide_action")
        graph.add_edge("decide_action", "execute_action")
        graph.add_edge("execute_action", "evaluate_result")
        graph.add_conditional_edges(
            "evaluate_result",
            self._should_continue,
            {"continue": "analyze", "end": END},
        )

        graph.set_entry_point("analyze")
        return graph.compile()

    def _analyze_situation(self, state: GameState) -> GameState:
        """Analyze the current game situation."""
        scan_result = self.game_client.scan_field()
        state.game_data = scan_result
        return state

    def _decide_action(self, state: GameState) -> GameState:
        """Decide what action to take based on the current situation."""
        if not state.game_data.get("success"):
            state.last_action = "scan"
            return state

        data = state.game_data.get("data", {})
        player_pos = data.get("playerPosition", {})
        enemies = data.get("nearbyCharacters", [])

        if enemies:
            # If there are enemies nearby, decide whether to attack or move
            closest_enemy = min(
                enemies,
                key=lambda e: abs(e["position"]["x"] - player_pos["x"])
                + abs(e["position"]["y"] - player_pos["y"]),
            )

            distance = abs(closest_enemy["position"]["x"] - player_pos["x"]) + abs(
                closest_enemy["position"]["y"] - player_pos["y"]
            )

            if distance == 1:  # Adjacent, can attack
                state.last_action = f"attack,{closest_enemy['position']['x']},{closest_enemy['position']['y']}"
            else:  # Move closer
                # Simple pathfinding - move towards enemy
                dx = closest_enemy["position"]["x"] - player_pos["x"]
                dy = closest_enemy["position"]["y"] - player_pos["y"]

                if abs(dx) > abs(dy):
                    direction = "right" if dx > 0 else "left"
                else:
                    direction = "down" if dy > 0 else "up"

                state.last_action = f"move,{direction}"
        else:
            # No enemies, explore randomly
            import random

            direction = random.choice(["up", "down", "left", "right"])
            state.last_action = f"move,{direction}"

        return state

    def _execute_action(self, state: GameState) -> GameState:
        """Execute the decided action."""
        action_parts = state.last_action.split(",")
        action_type = action_parts[0]

        try:
            if action_type == "move":
                if len(action_parts) >= 2:
                    direction = action_parts[1]
                    result = self.game_client.move_character(direction)
                else:
                    result = {"success": False, "error": "Invalid move action format"}
            elif action_type == "attack":
                if len(action_parts) >= 3:
                    x, y = int(action_parts[1]), int(action_parts[2])
                    result = self.game_client.attack_target(x, y)
                else:
                    result = {"success": False, "error": "Invalid attack action format"}
            elif action_type == "scan":
                result = self.game_client.scan_field()
            else:
                result = {"success": False, "error": "Unknown action"}
        except (ValueError, IndexError) as e:
            result = {"success": False, "error": f"Action execution error: {str(e)}"}

        state.action_result = result
        return state

    def _evaluate_result(self, state: GameState) -> GameState:
        """Evaluate the result of the action."""
        # For now, just store the result
        return state

    def _should_continue(self, state: GameState) -> str:
        """Determine if the agent should continue or stop."""
        # Simple logic: continue if the game is still active
        if state.game_data.get("success") and state.game_data.get("data", {}).get(
            "nearbyCharacters"
        ):
            return "continue"
        return "end"

    def run_turn(self) -> Dict[str, Any]:
        """Run a single turn of the combat agent."""
        initial_state = GameState()
        final_state = self.graph.invoke(initial_state)

        return {
            "action": final_state.last_action,
            "result": final_state.action_result,
            "game_state": final_state.game_data,
        }

    def run_autonomous(self, max_turns: int = 10) -> List[Dict[str, Any]]:
        """Run the agent autonomously for multiple turns."""
        results = []

        for turn in range(max_turns):
            turn_result = self.run_turn()
            results.append({"turn": turn + 1, **turn_result})

            # Stop if no enemies remain
            game_data = turn_result.get("game_state", {})
            if game_data.get("success"):
                enemies = game_data.get("data", {}).get("nearbyCharacters", [])
                if not enemies:
                    break

        return results
