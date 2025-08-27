"""
Game API client for communicating with the Next.js turn-based game.
"""

import json
import logging
from typing import Any, Dict, Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameClient:
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url = base_url

    def move_character(self, direction: str) -> Dict[str, Any]:
        """Move the player character in the specified direction."""
        url = f"{self.base_url}/character/multi-move"
        payload = {"direction": direction, "steps": 1}

        logger.info(f"📤 [MOVE] Sending request to {url}")
        logger.info(f"📤 [MOVE] Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, json=payload)
            response_data = response.json()

            logger.info(f"📥 [MOVE] Response status: {response.status_code}")
            logger.info(
                f"📥 [MOVE] Response data: {json.dumps(response_data, indent=2)}"
            )

            return response_data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [MOVE] Request failed: {str(e)}")
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def attack_target(self, x: int, y: int) -> Dict[str, Any]:
        """Attack a target at the specified coordinates."""
        url = f"{self.base_url}/character/attack"
        payload = {"target": {"x": x, "y": y}}

        logger.info(f"🎯 [ATTACK] Sending request to {url}")
        logger.info(f"🎯 [ATTACK] Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, json=payload)
            response_data = response.json()

            logger.info(f"📥 [ATTACK] Response status: {response.status_code}")
            logger.info(
                f"📥 [ATTACK] Response data: {json.dumps(response_data, indent=2)}"
            )

            return response_data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [ATTACK] Request failed: {str(e)}")
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def scan_field(self) -> Dict[str, Any]:
        """Scan the game field for enemies, obstacles, and other information."""
        url = f"{self.base_url}/character/multi-move"

        logger.info(f"🔍 [SCAN] Sending request to {url}")

        try:
            response = requests.get(url)
            response_data = response.json()

            return response_data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [SCAN] Request failed: {str(e)}")
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
