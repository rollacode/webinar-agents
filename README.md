# Webinar Agents Project

This project contains a turn-based game with AI agents that can control characters using LangChain and LangGraph technologies.

## Project Structure

```
webinar-agents/
├── webinar/                 # Jupyter notebooks with examples
│   └── examples.ipynb      # Demo notebooks for the webinar
├── turn-based-game/        # Next.js game with grid-based combat
│   ├── src/
│   │   ├── app/api/        # Game API endpoints
│   │   ├── lib/            # Game logic and types
│   │   └── components/     # React components
│   └── package.json
├── agents/                 # AI agents using LangChain/LangGraph
│   ├── game_client.py     # API client for game communication
│   ├── combat_agent.py    # Main AI agent for combat
│   ├── example_usage.py   # Usage examples
│   └── __init__.py
├── pyproject.toml         # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Install Python Dependencies

Make sure you have Poetry installed, then:

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 2. Setup the Turn-Based Game

```bash
cd turn-based-game
npm install
npm run dev
```

The game will be available at `http://localhost:3000`

### 3. Setup Environment Variables (Optional)

For AI agent features, create a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Testing the Game API

First, make sure the Next.js game is running, then test the API endpoints:

```bash
# Test field scanning
curl http://localhost:3000/api/field/scan

# Test character movement
curl -X POST http://localhost:3000/api/character/move \
  -H "Content-Type: application/json" \
  -d '{"direction": "right"}'

# Test attack
curl -X POST http://localhost:3000/api/character/attack \
  -H "Content-Type: application/json" \
  -d '{"target": {"x": 5, "y": 5}}'
```

### Using the AI Agent

```bash
cd agents
python example_usage.py
```

### Jupyter Notebook Examples

```bash
# Start Jupyter
poetry run jupyter notebook

# Open the webinar examples
# Navigate to webinar/examples.ipynb
```

## Game Features

- **Grid-based movement**: Character moves on a 10x10 grid
- **Combat system**: Attack adjacent enemies
- **Obstacles**: Static obstacles block movement
- **Multiple characters**: Player vs enemies
- **Health system**: Characters have health points

## AI Agent Features

- **Autonomous combat**: AI agent can control character automatically
- **Strategic decision making**: Chooses between moving and attacking
- **Field awareness**: Scans environment for enemies and obstacles
- **LangGraph workflow**: Uses state graphs for decision flow
- **API integration**: Communicates with game through REST API

## API Endpoints

- `GET /api/field/scan` - Get current game state and nearby characters
- `POST /api/character/move` - Move character in direction (up/down/left/right)
- `POST /api/character/attack` - Attack target at specific coordinates

## Development

### Adding New Agent Behaviors

1. Extend the `CombatAgent` class in `agents/combat_agent.py`
2. Add new decision logic in `_decide_action` method
3. Create new tools by extending `BaseTool`

### Extending the Game

1. Add new game mechanics in `turn-based-game/src/lib/gameLogic.ts`
2. Create new API endpoints in `turn-based-game/src/app/api/`
3. Update types in `turn-based-game/src/lib/gameTypes.ts`

## Troubleshooting

1. **Poetry installation issues**: Make sure you have Python 3.9+ installed
2. **Game connection errors**: Ensure Next.js server is running on port 3000
3. **LangChain errors**: Check that OPENAI_API_KEY is set correctly
4. **Import errors**: Make sure you're in the poetry virtual environment

## Next Steps

- Add visual game interface with React components
- Implement more sophisticated AI strategies
- Add multiplayer support
- Create more game mechanics (items, skills, etc.)
- Add tournament mode for AI vs AI battles 