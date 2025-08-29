"""
Simple Agent for controlling the game character using LangChain and LangGraph.
This agent can perform all available actions: move, use computer, use button, switch agents, etc.
"""

import json
import os
import time
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agents.action_executor import ActionExecutor
from agents.agent_logger import AgentLogger
from agents.game_client import GameClient
from agents.llm_service import LLMService
from agents.prompts import (
    build_decision_prompt,
    build_verify_action_prompt,
)
from agents.utils import extract_json_from_text


class LLMStudioModel(Enum):
    """Available LLM Studio models."""

    GEMMA_3_12B = "google/gemma-3-12b"
    GEMMA_3_27B = "google/gemma-3-27b"
    DEEPSEEK_R1 = "deepseek/deepseek-r1-0528-qwen3-8b"
    GPT_OSS = "openai/gpt-oss-20b"


USE_LLM_STUDIO = True
LLM_STUDIO_BASE_URL = "http://192.168.1.183:1234"
LLM_STUDIO_MODEL = LLMStudioModel.GPT_OSS.value
MODEL = "gpt-5-nano-2025-08-07"

TEMPERATURE = 1

MAX_RECURSION_LIMIT = 500

CONTEXT_HISTORY_LENGTH = 7


class SimpleAgentState(TypedDict):
    messages: List[SystemMessage | HumanMessage | AIMessage]
    game_data: Dict[str, Any]
    level_data: Dict[str, Any]
    last_action: str
    current_objective: str
    turn_count: int
    should_stop: bool


class SimpleAgent:
    running = False

    def __init__(
        self,
        api_key: Optional[str] = None,
        game_url: str = "http://localhost:3000/api",
        temperature: float = TEMPERATURE,
    ):
        self.game_client = GameClient(game_url)
        # Configure OpenAI key via env if provided
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        # Use streaming-capable LLM client when not using LLM Studio
        self.llm = None
        if not USE_LLM_STUDIO:
            self.llm = ChatOpenAI(
                model=MODEL,
                temperature=temperature,
            )
        self.should_stop = False

        self.llm_service = LLMService(
            llm=self.llm,
            use_llm_studio=USE_LLM_STUDIO,
            base_url=LLM_STUDIO_BASE_URL,
            model=LLM_STUDIO_MODEL,
        )
        self.action_executor = ActionExecutor(self.game_client)

        self.graph = self._create_graph()

    async def run(self) -> None:
        """Run the agent until completion or max turns reached."""
        self.running = True
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

    def _create_graph(self) -> Any:
        """Create the LangGraph state graph for the simple agent."""
        builder = StateGraph(SimpleAgentState)

        # Nodes
        builder.add_node("initialize", self._initialize)
        builder.add_node("analyze_situation", self._analyze_situation)
        builder.add_node("decide_action", self._decide_action)
        builder.add_node("verify_action", self._verify_action)
        builder.add_node("evaluate_result", self._evaluate_result)

        # Edges
        builder.add_edge(START, "initialize")
        builder.add_edge("initialize", "analyze_situation")
        builder.add_edge("analyze_situation", "decide_action")
        builder.add_edge("decide_action", "verify_action")
        builder.add_edge("verify_action", "evaluate_result")
        builder.add_conditional_edges(
            "evaluate_result",
            self._should_continue,
            {"continue": "analyze_situation", "end": END},
        )

        return builder.compile()

    async def _initialize(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Initialize the agent by getting level and game state information."""
        level_result = self.game_client.get_level_info()
        level_data_dict = (
            level_result.get("data", {}).get("level", {})
            if level_result.get("success")
            else {}
        )

        return {"level_data": level_data_dict}

    async def _analyze_situation(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Analyze the current game situation."""
        game_data = self.game_client.get_game_state()
        return {"game_data": game_data}

    async def _decide_action(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Decide what action to take based on current situation and LLM."""
        game_data = state.get("game_data", {})
        level_data = state.get("level_data", {})
        messages = state.get("messages", [])

        decision_prompt = build_decision_prompt(game_data, level_data)
        messages.append(HumanMessage(content=decision_prompt))
        self.logger.log_sent(decision_prompt)
        self.game_client.agent_add_message("Thinking about next decision...", "action")

        response_content: str = ""
        # Took only last message to get clear understanding about the current
        # state only, and not all the history.
        last_messages = messages[-1:]

        for delta in self.llm_service.stream_completion(
            last_messages, temperature=TEMPERATURE
        ):
            if not delta:
                continue
            response_content += delta
            self.game_client.agent_update_last(f"LLM: {response_content}", "action")

        self.logger.log_answered(response_content)
        messages.append(AIMessage(content=response_content))
        return {"messages": messages}

    async def _verify_action(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Verify the decided action."""
        messages = state.get("messages", [])

        verify_action_prompt = build_verify_action_prompt()
        messages.append(HumanMessage(content=verify_action_prompt))
        self.logger.log_sent(verify_action_prompt)
        self.game_client.agent_add_message("Verifying decision...", "action")

        # Taking more messages here to get more context about the previous steps
        # to avoid repeating the same actions.
        last_messages = messages[-CONTEXT_HISTORY_LENGTH:]
        response_content: str = ""
        for delta in self.llm_service.stream_completion(
            last_messages, temperature=TEMPERATURE
        ):
            if not delta:
                continue
            response_content += delta
            self.game_client.agent_update_last(f"LLM: {response_content}", "action")

        self.logger.log_answered(response_content)
        messages.append(AIMessage(content=response_content))

        action_data = extract_json_from_text(response_content)
        if action_data is None:
            self.logger.log_error(f"No valid JSON found in response {response_content}")
            action_data = {"action": "get_game_state", "parameters": {}}

        return {"last_action": json.dumps(action_data), "messages": messages}

    async def _evaluate_result(self, state: SimpleAgentState) -> Dict[str, Any]:
        """Evaluate the result of the action."""
        last_action = state.get("last_action", "{}")
        current_objective = state.get("current_objective", "explore_and_find_computer")
        turn_count = state.get("turn_count", 0) + 1

        result = self.action_executor.execute(last_action)

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
            self.running = False
            return "end"

        if self.should_stop:
            self.running = False
            return "end"

        return "continue"
