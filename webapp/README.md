# 🎮 PokéChamp Showcase Web Application

A fun, lightweight web application to showcase the PokéChamp battle AI system with live simulations, agent comparisons, and interactive visualizations.

![PokéChamp Banner](https://img.shields.io/badge/PokéChamp-Showcase-yellow?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask)
![Socket.IO](https://img.shields.io/badge/Socket.IO-4.0+-blue?style=for-the-badge)

## ✨ Features

- **🤖 Multiple AI Agents**: Compare different battle strategies from expert-level minimax to simple baselines
- **⚔️ Live Battle Simulation**: Watch agents battle in real-time with turn-by-turn visualization
- **📊 Performance Analytics**: Track win rates, battle statistics, and agent performance metrics
- **🎮 Multi-Format Support**: Battle across Gen 1-9 formats including singles and doubles
- **🎨 Pokemon-Themed UI**: Beautiful, animated interface with retro gaming aesthetics
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended) or `pip`

### Installation

1. **Navigate to the webapp directory:**
   ```bash
   cd webapp
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   cd .. && uv sync && cd webapp

   # OR using pip
   pip install flask flask-socketio python-socketio
   ```

3. **Run the web application:**
   ```bash
   # From the webapp directory
   python app.py
   ```

4. **Open your browser:**
   Navigate to [http://localhost:5000](http://localhost:5000)

## 📖 Usage

### Home Page
- Overview of the PokéChamp project
- System architecture visualization
- Quick links to all features

### Battle Simulator (`/battle`)
1. Select **Player 1** agent from the dropdown
2. Select **Player 2** agent from the dropdown
3. Choose a **battle format** (Gen 1-9)
4. Click **Start Battle** to begin
5. Watch the battle unfold in real-time!

### Agents Page (`/agents`)
- View all available agents and their descriptions
- See win rates and performance statistics
- Compare different agent types and strategies
- Quick links to battle specific agents

### Stats Dashboard (`/stats`)
- Overall performance metrics for each agent
- Recent battle history with timestamps
- Leaderboard ranked by win rate
- Battle analytics and trends

## 🤖 Available Agents

| Agent | Type | Description |
|-------|------|-------------|
| **Gen1 Heuristic Agent** | Heuristic | Expert Gen1 bot with exact damage calculation (100% win rate vs max_power) |
| **PokéChamp** | LLM + Minimax | Main agent using minimax algorithm with Bayesian predictions |
| **Abyssal Bot** | Heuristic | Strong baseline with balanced offense and defense |
| **Max Power** | Heuristic | Always selects maximum base power moves |
| **One Step Lookahead** | Heuristic | Plans one turn ahead with damage calculations |
| **Random** | Random | Random move selection baseline |

## 🎮 Battle Formats

- **gen1ou**: Generation 1 Overused (RBY)
- **gen2ou**: Generation 2 Overused (GSC)
- **gen3ou**: Generation 3 Overused (RSE)
- **gen8ou**: Generation 8 Overused (Sword/Shield)
- **gen9ou**: Generation 9 Overused (Scarlet/Violet)
- **gen9vgc2025regi**: VGC 2025 Regional (Doubles format)

## 🏗️ Architecture

```
webapp/
├── app.py                  # Flask application and routes
├── battle_runner.py        # Battle execution engine
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── battle.html        # Battle simulator
│   ├── agents.html        # Agent showcase
│   └── stats.html         # Statistics dashboard
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── main.js        # Core JavaScript
│       └── battle.js      # Battle interface logic
└── README.md              # This file
```

## 🔌 API Endpoints

### GET Endpoints

- `GET /` - Home page
- `GET /battle` - Battle simulator interface
- `GET /agents` - Agents showcase page
- `GET /stats` - Statistics dashboard
- `GET /api/agents` - JSON list of available agents
- `GET /api/battle_history` - Recent battle history
- `GET /api/agent_stats` - Agent performance statistics

### POST Endpoints

- `POST /api/start_battle` - Start a new battle simulation
  ```json
  {
    "player1": "gen1_agent",
    "player2": "abyssal",
    "format": "gen1ou"
  }
  ```

### WebSocket Events

**Client → Server:**
- `connect` - Establish connection
- `request_battle` - Request a new battle

**Server → Client:**
- `connected` - Connection established
- `battle_event` - Battle state updates
  - `battle_start` - Battle begins
  - `turn_start` - New turn
  - `move_used` - Move executed
  - `damage` - Damage dealt
  - `faint` - Pokemon fainted
  - `switch` - Pokemon switched
  - `battle_end` - Battle completed
  - `battle_error` - Error occurred

## 🎨 Customization

### Adding New Agents

1. Create your agent bot in `../bots/my_bot.py`
2. Add agent info to `AGENTS` dict in `app.py`:
   ```python
   'my_bot': {
       'name': 'My Custom Bot',
       'description': 'Description here',
       'type': 'Heuristic',
       'strength': 'Expert',
       'color': '#FF6B6B'
   }
   ```
3. Update `battle_runner.py` to recognize your agent

### Styling

Edit `static/css/style.css` to customize:
- Colors: Modify CSS variables in `:root`
- Layout: Adjust grid and flexbox properties
- Animations: Add or modify `@keyframes`

### Adding Features

The modular structure makes it easy to add:
- New pages (create template + route in `app.py`)
- New battle visualizations (extend `battle.js`)
- Additional statistics (update `stats.html`)

## 🐛 Troubleshooting

### Battle doesn't start
- Check that both agents are different
- Verify the battle format is valid
- Check browser console for errors
- Ensure backend server is running

### WebSocket connection failed
- Make sure Flask-SocketIO is installed
- Check firewall settings
- Try accessing via `http://localhost:5000` directly

### Agent not appearing
- Verify the agent is imported in `battle_runner.py`
- Check that the agent class exists in `../bots/`
- Look for import errors in terminal output

### Performance issues
- Battles run in background threads
- Each battle is isolated
- Check system resources if running many concurrent battles

## 📝 Development

### Running in Development Mode

```bash
# Enable debug mode (auto-reload on changes)
python app.py
```

The app runs with `debug=True` by default, which enables:
- Auto-reload on file changes
- Detailed error pages
- Interactive debugger

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 app:app
```

**Note:** Use only 1 worker (`-w 1`) due to Socket.IO requirements.

## 🤝 Contributing

This webapp is part of the PokéChamp project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is part of the PokéChamp framework. See the main repository for license information.

## 🙏 Acknowledgments

- **PokéChamp Team** - Original battle AI framework
- **poke-env** - Python interface for Pokémon Showdown
- **Flask & Socket.IO** - Web framework and real-time communication
- **Pokémon Showdown** - Battle simulation engine

## 🔗 Links

- [Main Repository](https://github.com/sethkarten/pokechamp)
- [Paper (ICML '25)](https://openreview.net/pdf?id=SnZ7SKykHh)
- [Dataset](https://huggingface.co/datasets/milkkarten/pokechamp)
- [Pokémon Showdown](https://pokemonshowdown.com/)

---

**Built with ❤️ for the Pokémon battle AI community**
