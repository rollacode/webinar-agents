# Webinar Agents - Turn-Based Game with AI

A turn-based platformer game with AI agents powered by LangChain and LangGraph. The project consists of a Next.js frontend game and Python AI agents that can intelligently navigate levels.

## 🚀 Quick Start

### Prerequisites

- **Python 3.12.3+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Poetry** - [Installation guide](https://python-poetry.org/docs/#installation)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd webinar-agents
   ```

2. **Install Python dependencies**
   ```bash
   poetry install
   ```

3. **Install frontend dependencies** (automatic on first run)
   ```bash
   cd turn-based-game
   npm install
   cd ..
   ```

### Running the Application

#### Option 1: Using Poetry Scripts (Recommended)

1. **Start the frontend game server**
   ```bash
   poetry run front
   ```
   This will start the Next.js development server at `http://localhost:3000`

2. **Start the AI agent server** (in a new terminal)
   ```bash
   poetry run agents
   ```
   This will start the Flask server at `http://localhost:5001`

#### Option 2: Manual Start

1. **Start frontend manually**
   ```bash
   cd turn-based-game
   npm run dev
   ```

2. **Start AI server manually**
   ```bash
   python -m agents.server
   ```

### Accessing the Application

- **Game Interface**: Open [http://localhost:3000](http://localhost:3000) in your browser
- **AI Agent API**: Available at [http://localhost:5001](http://localhost:5001)

## 🎮 Game Features

- **2D Platformer**: Navigate through levels with platforms (#) and ladders (L)
- **AI Agents**: Intelligent agents that can:
  - Move multiple steps in one direction
  - Use computers to complete levels
  - Press buttons to activate bridges
  - Switch between different agents
- **Real-time Communication**: Live agent messages and streaming responses

## 🤖 AI Agent Capabilities

The AI agents use LangChain and LangGraph to:
- Analyze level layouts and game state
- Plan optimal paths to objectives
- Execute actions with verification
- Handle complex navigation scenarios

### Available Actions
- `multi_move`: Move multiple steps in one direction
- `use_computer`: Complete level by using computer
- `use_button`: Activate bridges by pressing buttons
- `switch_agent`: Switch to different agent

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### LLM Studio Configuration (Optional)

The project supports local LLM Studio for offline AI processing:

```python
USE_LLM_STUDIO = True
LLM_STUDIO_BASE_URL = "http://192.168.1.183:1234"
LLM_STUDIO_MODEL = "openai/gpt-oss-20b"
```

## 📁 Project Structure

```
webinar-agents/
├── agents/                 # Python AI agents
│   ├── prompts/           # LLM prompts and templates
│   ├── simple_agent.py    # Main agent implementation
│   ├── server.py          # Flask API server
│   └── ...
├── turn-based-game/       # Next.js frontend
│   ├── src/              # React components
│   ├── public/           # Static assets
│   └── ...
├── scripts/              # Run scripts
├── logs/                 # Agent session logs
└── pyproject.toml        # Python dependencies
```

## 🛠️ Development

### Adding New Features

1. **Frontend**: Modify components in `turn-based-game/src/`
2. **AI Logic**: Update agent logic in `agents/simple_agent.py`
3. **Prompts**: Customize prompts in `agents/prompts/`

### Testing

```bash
# Run Python tests
poetry run pytest

# Run frontend tests
cd turn-based-game
npm test
```

### Code Quality

```bash
# Format Python code
poetry run black agents/
poetry run isort agents/

# Lint Python code
poetry run flake8 agents/

# Format frontend code
cd turn-based-game
npm run lint
```

## 📊 Monitoring

- **Agent Logs**: Session logs are saved in `logs/` directory
- **Real-time Updates**: Agent actions are streamed to the frontend
- **API Status**: Check agent status via `/api/agent/status` endpoint

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Frontend: Change port in `turn-based-game/package.json`
   - Backend: Change port in `agents/server.py`

2. **Missing dependencies**
   ```bash
   poetry install --sync
   cd turn-based-game && npm install
   ```

3. **AI agent not responding**
   - Check `OPENAI_API_KEY` is set
   - Verify game server is running at `localhost:3000`
   - Check agent logs in `logs/` directory

### Getting Help

- Check the logs in `logs/` directory for detailed error information
- Verify all services are running on correct ports
- Ensure all dependencies are properly installed

## 📝 License

This project is for educational purposes as part of a webinar demonstration.
