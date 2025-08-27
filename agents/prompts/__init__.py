from typing import Any, Dict, List


def get_system_prompt() -> str:
    return """
You are an AI agent controlling a character in a 2D platformer game. Your goal is to navigate the level and reach the computer (C) to complete the level.

GAME MECHANICS:
- You can move on platforms and climb ladders
- You can move multiple steps in one direction (1-10 steps)
- Movement directions: up, down, left, right
- You can only move to valid positions (on platforms or ladders)
- There may be multiple agents you can switch between

LEVEL OBJECTIVES:
1. Navigate through the level using platforms # and ladders |
2. Find and reach the computer (C) to complete the level
3. Use buttons if available to activate bridges
4. Switch between agents if there are multiple agents available

AVAILABLE ACTIONS:
- multi_move: Move multiple steps in one direction
- use_computer: Use computer when standing on or adjacent to it (completes level)
- use_button: Press button when standing on it (activates bridges)
- switch_agent: Switch to different agent by index
- reset_position: Reset to starting position (use if stuck)

STRATEGY:
1. First, get the level information to understand the layout
2. Get current game state to see your position and available actions
3. Plan your path to the computer using platforms and ladders
4. Move efficiently using multi_move when possible
5. Use buttons to activate bridges if needed
6. Switch agents if it helps reach the objective
7. Use computer when you reach it to complete the level, do not forget that comuter have X and Y coordinates, so ladders!

Always analyze the level layout and plan your moves carefully. Use multi_move for efficient movement along platforms.
"""


def build_level_prompt(level_info: Dict[str, Any]) -> str:
    layout_string = ""
    layout: List[str] = level_info.get("layout", [])
    for row in layout:
        layout_string += f"{row}\n"

    return f"""
LEVEL INFORMATION:
- Size: {level_info.get("size", {})}
- Layout:
{layout_string}

Based on the level layout and your current situation, what action should you take?
Respond with a JSON object containing:
- action: the tool name to use
- parameters: object with parameters for the tool if needed

multi_moves can be made with steps 1 to 10 just put amount of steps you want to move.
you could predict how many steps you need to move like to clump a ladder or to get to the computer.

use_computer in available actions means it's possible to use the computer.
use_button in available actions means it's possible to use the button.

switch_agent in available actions means it's possible to switch to a different agent.

"""


def build_decision_prompt(game_data: Dict[str, Any], level_data: Dict[str, Any]) -> str:
    position = game_data.get("position", {})
    level_map = level_data.get("layout", [])
    map_height = len(level_map)

    level_map = [list(row) for row in level_map]
    level_map[position["y"]][position["x"]] = "X"

    converted_agent_position = {
        "x": position["x"],
        "y": map_height - 1 - position["y"],
    }

    computer_position = None
    for y, row in enumerate(level_map):
        if "C" in row:
            computer_position = (y, row.index("C"))
            break

    level_map = ["".join(row) for row in level_map]

    level_map_string = ""
    for row in level_map:
        level_map_string += f"{row}\n"

    if computer_position:
        computer_y_bottom_left = map_height - 1 - computer_position[0]
        computer_pos_str = (
            f'{{"x": {computer_position[1]}, "y": {computer_y_bottom_left}}}'
        )
    else:
        computer_pos_str = "Not found"

    return f"""
GAME STATE:
- Current position: {converted_agent_position}
- Computer position: {computer_pos_str}
- Active agent: {game_data.get("activeAgent", 0)}
- Agents count: {game_data.get("agentCount", 1)}
- Available actions: {game_data.get("available_actions", [])}

Example response:
{{
"plan": "I need to move ... to reach the computer",
"path_planning": "I moving ... because I see that computer is on top and I need to use ladders to reach it",
"action": "...",
"parameters": {{"direction": "...", "steps": ...}}
}}

<HINT>
    You can make multiple steps at ones in one direction.
    On ladders you need to move 1 step more up to be aligned with the platform to move left and right then.
</HINT>

<LEVEL_MAP>
{level_map_string}

platforms (#), ladders (|), empty spaces (░), Computer (C), Button (B)
X is your current position
</LEVEL_MAP>

YOU NEED TO STAY ON LADDERS TO BE ABLE TO MOVE UP AND DOWN! LADDERS ARE NOT EMPTY SPACES THYE HAVE SYMBOL (|)
Set your goal to reach the computer in few steps and move there.
DO not try to clumb up or down without ladders!

<IMPORTANT>
  Do not try to execute actions that are not available in the Available actions array {game_data.get("available_actions", [])}
  you can only use actions that are in the Available actions array.

  move towards the ladder if you see it.
</IMPORTANT>
"""
