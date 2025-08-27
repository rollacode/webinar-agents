"""
Game API client for communicating with the Next.js turn-based game.
"""

import json
import logging
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameClient:
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url = base_url

    def multi_move(
        self, direction: str, steps: int, agent_index: int = 0
    ) -> Dict[str, Any]:
        """Move character multiple steps in one direction."""
        url = f"{self.base_url}/character/multi-move"
        payload = {"direction": direction, "steps": steps, "agentIndex": agent_index}

        response = requests.post(url, json=payload)
        response_data = response.json()

        logger.info(
            f"📥 [MULTI_MOVE] Response data: {json.dumps(response_data, indent=2)}"
        )

        return response_data

    def reset_position(self) -> Dict[str, Any]:
        """Reset character position to starting position."""
        url = f"{self.base_url}/character/reset"

        response = requests.post(url)
        response_data = response.json()

        logger.info(f"📥 [RESET] Response data: {json.dumps(response_data, indent=2)}")

        return response_data

    def switch_agent(self, agent_index: int) -> Dict[str, Any]:
        """Switch to a different agent."""
        url = f"{self.base_url}/character/switch-agent"
        payload = {"agentIndex": agent_index}

        response = requests.post(url, json=payload)
        response_data = response.json()

        logger.info(
            f"📥 [SWITCH_AGENT] Response data: {json.dumps(response_data, indent=2)}"
        )

        return response_data

    def use_button(self) -> Dict[str, Any]:
        """Press button to activate bridges."""
        url = f"{self.base_url}/character/use-button"

        response = requests.post(url)
        response_data = response.json()

        logger.info(
            f"📥 [USE_BUTTON] Response data: {json.dumps(response_data, indent=2)}"
        )

        return response_data

    def use_computer(self) -> Dict[str, Any]:
        """Use computer to complete the level."""
        url = f"{self.base_url}/character/use-pc"

        response = requests.post(url)
        response_data = response.json()

        logger.info(f"📥 [USE_PC] Response data: {json.dumps(response_data, indent=2)}")

        return response_data

    def get_level_info(self) -> Dict[str, Any]:
        """Get current level information and layout."""
        url = f"{self.base_url}/level/info"

        response = requests.get(url)
        response_data = response.json()

        logger.info(
            f"📥 [LEVEL_INFO] Response data: {json.dumps(response_data, indent=2)}"
        )

        return response_data

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state including all agents and positions."""
        url = f"{self.base_url}/character/multi-move"

        response = requests.get(url)
        response_data = response.json()

        logger.info(
            f"📥 [GAME_STATE] Response data: {json.dumps(response_data, indent=2)}"
        )

        return response_data.get("data", {})
