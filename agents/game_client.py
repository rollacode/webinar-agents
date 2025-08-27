"""
Game API client for communicating with the Next.js turn-based game.
"""

from typing import Any, Dict, Optional

import requests


class GameClient:
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url = base_url

    def move_character(self, direction: str) -> Dict[str, Any]:
        """Move the player character in the specified direction."""
        url = f"{self.base_url}/character/multi-move"
        payload = {"direction": direction, "steps": 1}

        try:
            response = requests.post(url, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def attack_target(self, x: int, y: int) -> Dict[str, Any]:
        """Attack a target at the specified coordinates."""
        url = f"{self.base_url}/character/attack"
        payload = {"target": {"x": x, "y": y}}

        try:
            response = requests.post(url, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def scan_field(self) -> Dict[str, Any]:
        """Scan the game field for enemies, obstacles, and other information."""
        url = f"{self.base_url}/character/multi-move"

        try:
            response = requests.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def get_player_position(self) -> Optional[Dict[str, int]]:
        """Get the current player position."""
        scan_result = self.scan_field()
        if scan_result.get("success") and "data" in scan_result:
            return scan_result["data"].get("playerPosition")
        return None

    def get_nearby_enemies(self) -> list:
        """Get list of nearby enemies."""
        scan_result = self.scan_field()
        if scan_result.get("success") and "data" in scan_result:
            return scan_result["data"].get("nearbyCharacters", [])
        return []
