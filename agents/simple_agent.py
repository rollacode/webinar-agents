"""
Simple Agent for controlling the game character using LangChain and LangGraph.
This agent can perform all available actions: move, use computer, use button, switch agents, etc.
"""

import json
import time
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agents.utils import extract_json_from_text

from .agent_logger import AgentLogger
from .game_client import GameClient
from .tools import (
    GetGameStateTool,
    GetLevelInfoTool,
    MultiMoveTool,
    ResetPositionTool,
    SwitchAgentTool,
    UseButtonTool,
    UseComputerTool,
)

MAX_RECURSION_LIMIT = 30
MODEL = "gpt-5-mini"


class SimpleAgentState(TypedDict):
    messages: List[SystemMessage | HumanMessage | AIMessage]
    game_data: Dict[str, Any]
    level_data: Dict[str, Any]
    last_action: str
    action_result: Dict[str, Any]
    current_objective: str
    turn_count: int
    should_stop: bool


class SimpleAgent:
    def __init__(
        self,
        api_key: Optional[str] = None,
        game_url: str = "http://localhost:3000/api",
        temperature: float = 1,
    ):
        self.game_client = GameClient(game_url)
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=MODEL,
            temperature=temperature,
        )
        self.should_stop = False

        self.tools = [
            MultiMoveTool(self.game_client),
            UseComputerTool(self.game_client),
            UseButtonTool(self.game_client),
            SwitchAgentTool(self.game_client),
            ResetPositionTool(self.game_client),
            GetGameStateTool(self.game_client),
            GetLevelInfoTool(self.game_client),
        ]

        self.graph = self._create_graph()

        self.system_prompt = self._create_system_prompt()

    async def run(self) -> None:
        """Run the agent until completion or max turns reached."""
        self.should_stop = False

        self.logger = AgentLogger(f"session_{time.time()}")

        # Log session start
        self.logger.log_info(
            "Agent session started",
            {
                "objective": "explore_and_find_computer",
                "model": self.llm.model_name if self.llm else "No LLM",
                "game_url": self.game_client.base_url,
            },
        )

        initial_state = {
            "messages": [],
            "game_data": {},
            "level_data": {},
            "last_action": "",
            "action_result": {},
            "current_objective": "explore_and_find_computer",
            "turn_count": 0,
            "should_stop": False,
        }

        config = RunnableConfig(recursion_limit=MAX_RECURSION_LIMIT)
        final_state = await self.graph.ainvoke(initial_state, config)

        # Log session completion
        self.logger.log_info(
            "Agent session completed",
            {
                "final_objective": final_state["current_objective"],
                "final_action": final_state["last_action"],
                "final_result": final_state["action_result"],
                "total_turns": final_state["turn_count"],
            },
        )

        # Close the logger session
        self.logger.close_session()

        print(f"Agent completed with objective: {final_state['current_objective']}")
        print(f"Final action: {final_state['last_action']}")
        print(f"Final result: {final_state['action_result']}")

    def stop(self) -> None:
        """Stop the agent."""
        self.should_stop = True

    def _create_system_prompt(self) -> str:
        return """
                You are an AI agent controlling a character in a 2D platformer game. Your goal is to navigate the level and reach the computer (C) to complete the level.

                GAME MECHANICS:
                - The level consists of platforms (#), ladders (|), empty spaces (░), and a computer (C)
                - You can move on platforms and climb ladders
                - You can move multiple steps in one direction (1-10 steps)
                - Movement directions: up, down, left, right
                - You can only move to valid positions (on platforms or ladders)
                - There may be multiple agents you can switch between

                LEVEL OBJECTIVES:
                1. Navigate through the level using platforms and ladders
                2. Find and reach the computer (C) to complete the level
                3. Use buttons if available to activate bridges
                4. Switch between agents if there are multiple agents available

                AVAILABLE ACTIONS:
                - multi_move: Move multiple steps in one direction
                - use_computer: Use computer when standing on or adjacent to it (completes level)
                - use_button: Press button when standing on it (activates bridges)
                - switch_agent: Switch to different agent by index
                - reset_position: Reset to starting position (use if stuck)
                - get_game_state: Get current positions and available actions
                - get_level_info: Get level layout and information

                STRATEGY:
                1. First, get the level information to understand the layout
                2. Get current game state to see your position and available actions
                3. Plan your path to the computer using platforms and ladders
                4. Move efficiently using multi_move when possible
                5. Use buttons to activate bridges if needed
                6. Switch agents if it helps reach the objective
                7. Use computer when you reach it to complete the level

                Always analyze the level layout and plan your moves carefully. Use multi_move for efficient movement along platforms.
                """

    def _create_graph(self) -> Any:
        """Create the LangGraph state graph for the simple agent."""
        builder = StateGraph(SimpleAgentState)

        # Nodes
        builder.add_node("initialize", self._initialize)
        builder.add_node("analyze_situation", self._analyze_situation)
        builder.add_node("decide_action", self._decide_action)
        builder.add_node("execute_action", self._execute_action)
        builder.add_node("evaluate_result", self._evaluate_result)

        # Edges
        builder.add_edge(START, "initialize")
        builder.add_edge("initialize", "analyze_situation")
        builder.add_edge("analyze_situation", "decide_action")
        builder.add_edge("decide_action", "execute_action")
        builder.add_edge("execute_action", "evaluate_result")
        builder.add_conditional_edges(
            "evaluate_result",
            self._should_continue,
            {"continue": "analyze_situation", "end": END},
        )

        return builder.compile()

    async def _initialize(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Initialize the agent by getting level and game state information."""
        level_result = self.game_client.get_level_info()
        level_info = (
            level_result.get("data", {}).get("level", {})
            if level_result.get("success")
            else {}
        )

        layout_string = ""
        layout = level_info.get("layout", [])
        for i, row in enumerate(layout):
            layout_string += f"{row}\n"

        level_data = f"""
LEVEL INFORMATION:
- Size: {level_info.get("size", {})}
- Starting Position: {level_info.get("starting_position", {})}
- Legend: {level_info.get("legend", {})}
- Layout:
{layout_string}
Coordinates is calulating from the top left corner and start from 0

Based on the level layout and your current situation, what action should you take?
Respond with a JSON object containing:
- action: the tool name to use
- parameters: object with parameters for the tool if needed

Available actions are:
move_left in available actions means it's possible to make multi_move with direction left.
move_right in available actions means it's possible to make multi_move with direction right.
move_up in available actions means it's possible to make multi_move with direction up.
move_down in available actions means it's possible to make multi_move with direction down.

multi_moves can be made with steps 1 to 10 just put amount of steps you want to move.
you could predict how many steps you need to move like to clump a ladder or to get to the computer.

use_computer in available actions means it's possible to use the computer.
use_button in available actions means it's possible to use the button.

switch_agent in available actions means it's possible to switch to a different agent.

Example response:
{{
"action": "multi_move",
"parameters": {{"direction": "right", "steps": 5}}
}}

other actions just like
{{
"action": "use_computer"
}}
"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=level_data),
        ]

        return {"messages": messages, "level_data": level_info}

    async def _analyze_situation(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Analyze the current game situation."""
        game_data = self.game_client.get_game_state()
        level_result = self.game_client.get_level_info()
        level_data = level_result.get("data", {}) if level_result.get("success") else {}

        self.logger.log_info("Analyzing situation")

        return {"game_data": game_data, "level_data": level_data}

    def _create_context_string(self, state: SimpleAgentState) -> str:
        """Create a context string describing the current situation."""
        game_data = state.get("game_data", {})

        context = f"""
GAME STATE:
- Current position: {game_data.get("position", {})}
- Active agent: {game_data.get("activeAgent", 0)}
- Agents count: {game_data.get("agentCount", 1)}
- Available actions: {game_data.get("available_actions", [])}

"""

        return context

    async def _decide_action(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Decide what action to take based on current situation and LLM."""
        decision_context = self._create_context_string(state)
        messages = state.get("messages", [])

        prompt = f"""{decision_context}
Current objective: {state.get("current_objective", "explore_and_find_computer")}
"""
        messages.append(HumanMessage(content=prompt))

        self.logger.log_sent(prompt)

        response = self.llm.invoke(messages)
        response_content = response.content

        messages.append(AIMessage(content=response_content))

        print(response_content)
        if isinstance(response_content, list):
            response_content = str(response_content[0]) if response_content else ""

        # Extract JSON from response
        action_data = extract_json_from_text(response_content)
        if action_data is None:
            self.logger.log_error(f"No valid JSON found in response {response_content}")
            action_data = {"action": "get_game_state", "parameters": {}}

        self.logger.log_answered(response_content)

        return {"last_action": json.dumps(action_data), "messages": messages}

    async def _execute_action(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Execute the decided action."""
        try:
            action_data = json.loads(state.get("last_action", "{}"))
            action_type = action_data.get("action", "")
            parameters = action_data.get("parameters", {})

            if action_type == "multi_move":
                result = self.game_client.multi_move(
                    parameters["direction"],
                    parameters["steps"],
                    parameters.get("agent_index", 0),
                )
            elif action_type == "use_computer":
                result = self.game_client.use_computer()
            elif action_type == "use_button":
                result = self.game_client.use_button()
            elif action_type == "switch_agent":
                result = self.game_client.switch_agent(parameters["agent_index"])
            elif action_type == "reset_position":
                result = self.game_client.reset_position()
            elif action_type == "get_game_state":
                result = self.game_client.get_game_state()
            elif action_type == "get_level_info":
                result = self.game_client.get_level_info()
            else:
                result = {"success": False, "error": f"Unknown action: {action_type}"}

        except (ValueError, IndexError, json.JSONDecodeError) as e:
            result = {"success": False, "error": f"Action execution error: {str(e)}"}

        return {"action_result": result}

    async def _evaluate_result(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Evaluate the result of the action."""
        result = state.get("action_result", {})
        current_objective = state.get("current_objective", "explore_and_find_computer")
        turn_count = state.get("turn_count", 0) + 1

        if result.get("success"):
            data = result.get("data", {})
            if data.get("level_completed") or data.get("victory"):
                current_objective = "completed"
            elif data.get("bridgesActivated"):
                current_objective = "bridges_activated_continue_to_computer"

        return {"current_objective": current_objective, "turn_count": turn_count}

    def _should_continue(self, state: SimpleAgentState) -> str:
        """Determine if the agent should continue or stop."""
        if state.get("current_objective") == "completed":
            return "end"

        if self.should_stop:
            return "end"

        return "continue"
