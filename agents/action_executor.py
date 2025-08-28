import json
from typing import Any, Dict

from .game_client import GameClient


class ActionExecutor:
    def __init__(self, game_client: GameClient) -> None:
        self.game_client = game_client

    def execute(self, last_action: str) -> Dict[str, Any]:
        try:
            action_data = json.loads(last_action or "{}")
            action_type = action_data.get("action", "")
            parameters = action_data.get("parameters", {})

            if (
                action_type == "multi_move"
                or action_type == "move"
                or action_type == "multi_move[right]"
                or action_type == "multi_move[left]"
                or action_type == "multi_move[up]"
                or action_type == "multi_move[down]"
            ):
                result = self.game_client.multi_move(
                    parameters["direction"],
                    parameters["steps"],
                    parameters.get("agent_index", 0),
                )
            elif action_type == "use_computer" or action_type == "use_pc":
                result = self.game_client.use_computer()
            elif action_type == "use_button":
                result = self.game_client.use_button()
            elif action_type == "switch_agent":
                result = self.game_client.switch_agent(parameters["agent_index"])
            elif action_type == "reset_position":
                result = self.game_client.reset_position()
            else:
                result = {"success": False, "error": f"Unknown action: {action_type}"}

        except (ValueError, IndexError, json.JSONDecodeError) as e:
            result = {"success": False, "error": f"Action execution error: {str(e)}"}

        return {"action_result": result}
