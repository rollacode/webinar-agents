from typing import Any, Dict, List


def get_system_prompt() -> str:
    return """
You are an AI agent controlling a character in a 2D platformer game. Your goal is to navigate the level and reach the computer (C) to complete the level.

GAME MECHANICS:
- You can move on platforms # and climb ladders L
- You can move multiple steps in one direction (1-10 steps)
- Movement directions: up, down, left, right
- You can only move to valid positions (on platforms # or ladders L)

LEVEL OBJECTIVES:
1. Find and reach the computer (C) to complete the level
2. Use buttons if available to activate bridges
3. Switch between agents if there are multiple agents available

AVAILABLE ACTIONS:
- multi_move: Move multiple steps in one direction
- use_computer: Use computer when standing on or adjacent to it (completes level)
- use_button: Press button when standing on it (activates bridges)
- switch_agent: Switch to different agent by index

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
"""


def build_decision_prompt(game_data: Dict[str, Any], level_data: Dict[str, Any]) -> str:
    position = game_data.get("position", {})
    level_map = level_data.get("layout", [])
    map_height = len(level_map)

    helper_text = "You are not on ladder right now so you can't move up or down."

    level_map = [list(row) for row in level_map]
    current_pos_tile = level_map[position["y"]][position["x"]]
    if current_pos_tile == "L":
        level_map[position["y"]][position["x"]] = "H"
        helper_text = "You are on ladder right now so you CAN move up or down."
    elif current_pos_tile == "B":
        level_map[position["y"]][position["x"]] = "G"
        helper_text = "You are on button right now so you CAN press it."
    elif current_pos_tile == "C":
        level_map[position["y"]][position["x"]] = "J"
        helper_text = "You are on computer right now so you CAN use it."
    else:
        level_map[position["y"]][position["x"]] = "X"

    converted_agent_position = {
        "x": position["x"],
        "y": map_height - 1 - position["y"],
    }
    converted_agent_position_str = (
        f"{{x: {converted_agent_position['x']}, y: {converted_agent_position['y']}}}"
    )

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
        computer_pos_str = f"{{x: {computer_position[1]}, y: {computer_y_bottom_left}}}"
    else:
        computer_pos_str = "Not found"

    return f"""
<SYSTEM_PROMPT>
{get_system_prompt()}
</SYSTEM_PROMPT>

>GAME STATE>
- Current position: {converted_agent_position_str}
- Computer position: {computer_pos_str}
- Active agent: {game_data.get("activeAgent", 0)}
- Agents count: {game_data.get("agentCount", 1)}
- Available actions: {game_data.get("available_actions", [])}
</GAME_STATE>

<HINT>
    You can make multiple steps at ones in one direction.
    On ladders you need to move 1 step more up to be aligned with the platform to move left and right then.
</HINT>

<LEVEL_MAP>
{level_map_string}

platforms (#), ladders (L), empty spaces (E), Computer (C), Button (B), your current position (X), your current ladder position (H), bridge (G)

X is your current position, H means same as X but on ladder.
G means same as X but you are on Button.
J means same as X but you are on Computer.
</LEVEL_MAP>

<IMPORTANT>
    YOU NEED TO STAY ON LADDERS TO BE ABLE TO MOVE UP AND DOWN! LADDERS ARE NOT EMPTY SPACES THYE HAVE SYMBOL (L)
    Set your goal to reach the computer in few steps and move there.
    DO not try to clumb up or down without ladders!

    Do not try to execute actions that are not available in the Available actions
    you can only use actions that are in the Available actions array.

    Do not try to move under computer just to allign with it, you need to use ladders to reach it.
    Just move up if computer above and down if computer below use ladders!!!

    to activate pc you need to be on exact position of computer, not on ladder.
    {helper_text}
</IMPORTANT>

<THINK>
  ACT AS DISCOVERER! DO NOT BE STUCK! DO NOT SCARE DO THE THINGS GO TO THE COMPUTER WITH BEST PATHFINDING ALGORITHM!
  YOU ARE THINKIN ABOUT YOUR NEXT ACTION HERE BE A DISCOVERER! TRY TO FIND THE BEST PATH TO THE COMPUTER!
  JUST DESCRIBE IN WARDS WHAT YOU THINK YOU SHOULD DO! DO NOT SCARE!
  IF YOU ARE STUCK SEARCH LADDERS THAT LEAD TO COMPUTER!
</THINK>

<COORDINATES_FORMAT>
  x: 0, y: 0 is bottom left corner

  so if computer y coordinate is 0 you need to move down to reach it.
  if your y coordinate is lower then computer y coordinate you need to move up to reach it, and vice versa.

  plan your path and keep in mind that you can move multiple steps at once.
  you may use bulletpoints to describe your idea

  PICK ONLY ONE LADDER TO CLIMB AT A TIME! JUST GO UP AND UP TO THE PC IF IT IS ABOVE YOU!
</COORDINATES_FORMAT>
"""


def build_verify_action_prompt() -> str:
    return """
From everything that you said in previous messages, verify that the action is possible to execute.
Return only JSON object with action and parameters.

<EXAMPLE_RESPONSE>
{
"action": "...",
"parameters": {"direction": "...", "steps": ...}
"explanation": "explain your decision"
}
</EXAMPLE_RESPONSE>

multi_move[right] means you can do {{"action": "multi_move", "parameters": {{"direction": "right", "steps": ...}}}}

decide multiple steps at once if possible it will be better for you.

PICK ONLY ONE LADDER TO CLIMB AT A TIME! JUST GO UP AND UP TO THE PC IF IT IS ABOVE YOU!
Check previous steps and try to avoid repeating them, means if you moved right 1 time and then left 1 time, 
it's a cycle and you need to think how to break it with other actions, or with some plan of action that will lead you to pc

JSON ONLY!
"""
