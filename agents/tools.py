import json

from langchain.tools import BaseTool
from pydantic import Field

from .game_client import GameClient


class MultiMoveTool(BaseTool):
    name: str = "multi_move"
    description: str = "Move the character multiple steps in one direction (up, down, left, right). Steps can be 1-10."
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self, direction: str, steps: int, agent_index: int = 0) -> str:
        result = self.game_client.multi_move(direction, steps, agent_index)
        return json.dumps(result)

    async def _arun(self, direction: str, steps: int, agent_index: int = 0) -> str:
        return self._run(direction, steps, agent_index)


class UseComputerTool(BaseTool):
    name: str = "use_computer"
    description: str = "Use the computer to complete the level. Only works when standing on or adjacent to computer."
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self) -> str:
        result = self.game_client.use_computer()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()


class UseButtonTool(BaseTool):
    name: str = "use_button"
    description: str = (
        "Press button to activate bridges. Only works when standing on a button."
    )
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self) -> str:
        result = self.game_client.use_button()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()


class SwitchAgentTool(BaseTool):
    name: str = "switch_agent"
    description: str = "Switch to a different agent by index (0, 1, 2, etc.)"
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self, agent_index: int) -> str:
        result = self.game_client.switch_agent(agent_index)
        return json.dumps(result)

    async def _arun(self, agent_index: int) -> str:
        return self._run(agent_index)


class ResetPositionTool(BaseTool):
    name: str = "reset_position"
    description: str = "Reset character position to the starting position of the level."
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self) -> str:
        result = self.game_client.reset_position()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()


class GetGameStateTool(BaseTool):
    name: str = "get_game_state"
    description: str = "Get current game state including all agent positions, active agent, and available actions."
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self) -> str:
        result = self.game_client.get_game_state()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()


class GetLevelInfoTool(BaseTool):
    name: str = "get_level_info"
    description: str = (
        "Get current level information including layout, legend, and size."
    )
    game_client: GameClient = Field(exclude=True)

    def __init__(self, game_client: GameClient):
        super().__init__(game_client=game_client)

    def _run(self) -> str:
        result = self.game_client.get_level_info()
        return json.dumps(result)

    async def _arun(self) -> str:
        return self._run()
