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

        return response_data

    def reset_position(self) -> Dict[str, Any]:
        """Reset character position to starting position."""
        url = f"{self.base_url}/character/reset"

        response = requests.post(url)
        response_data = response.json()

        return response_data

    def switch_agent(self, agent_index: int) -> Dict[str, Any]:
        """Switch to a different agent."""
        url = f"{self.base_url}/character/switch-agent"
        payload = {"agentIndex": agent_index}

        response = requests.post(url, json=payload)
        response_data = response.json()

        return response_data

    def use_button(self) -> Dict[str, Any]:
        """Press button to activate bridges."""
        url = f"{self.base_url}/character/use-button"

        response = requests.post(url)
        response_data = response.json()

        return response_data

    def use_computer(self) -> Dict[str, Any]:
        """Use computer to complete the level."""
        url = f"{self.base_url}/character/use-pc"

        response = requests.post(url)
        response_data = response.json()

        return response_data

    # ----- Agent stream helpers -----
    def agent_add_message(self, text: str, type_: str = "info") -> Dict[str, Any]:
        """Add a new live agent message in UI via Next API."""
        url = f"{self.base_url}/agent/events"
        payload = {"action": "add", "message": {"text": text, "type": type_}}
        response = requests.post(url, json=payload)
        response_data = response.json()

        return response_data

    def agent_update_last(self, text: str, type_: str = "info") -> Dict[str, Any]:
        """Update the last live agent message (stream-like)."""
        url = f"{self.base_url}/agent/events"
        payload = {"action": "update_last", "message": {"text": text, "type": type_}}
        response = requests.post(url, json=payload)
        response_data = response.json()

        return response_data

    def get_level_info(self) -> Dict[str, Any]:
        """Get current level information and layout."""
        url = f"{self.base_url}/level/info"

        response = requests.get(url)
        response_data = response.json()

        return response_data

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state including all agents and positions."""
        url = f"{self.base_url}/character/multi-move"

        response = requests.get(url)
        response_data = response.json()

        return response_data.get("data", {})
