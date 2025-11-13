"""
PokéChamp Showcase Web Application

A lightweight Flask webapp to demonstrate the PokéChamp battle AI system
with live simulations, agent comparisons, and visualizations.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import asyncio
import json
import threading
from datetime import datetime
from collections import defaultdict
import sys
import os

# Add parent directory to path to import pokechamp modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from battle_runner import BattleRunner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokechamp-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global battle runner
battle_runner = BattleRunner(socketio)

# Store battle history
battle_history = []
agent_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'battles': 0})

# Available agents
AGENTS = {
    'gen1_agent': {
        'name': 'Gen1 Heuristic Agent',
        'description': 'Custom Gen1 bot with exact damage calculation and advanced switch logic. Achieves 100% win rate vs max_power baseline.',
        'type': 'Heuristic',
        'strength': 'Expert',
        'color': '#FF6B6B'
    },
    'pokechamp': {
        'name': 'PokéChamp',
        'description': 'Main LLM-based agent using minimax algorithm with Bayesian predictions. Expert-level play across multiple generations.',
        'type': 'LLM + Minimax',
        'strength': 'Expert',
        'color': '#4ECDC4'
    },
    'abyssal': {
        'name': 'Abyssal Bot',
        'description': 'Strong baseline heuristic bot. Good balance of offense and defense.',
        'type': 'Heuristic',
        'strength': 'Strong',
        'color': '#95E1D3'
    },
    'max_power': {
        'name': 'Max Power',
        'description': 'Always selects the move with maximum base power. Simple but effective baseline.',
        'type': 'Heuristic',
        'strength': 'Intermediate',
        'color': '#F38181'
    },
    'one_step': {
        'name': 'One Step Lookahead',
        'description': 'Plans one turn ahead using damage calculations. Better than random, worse than minimax.',
        'type': 'Heuristic',
        'strength': 'Intermediate',
        'color': '#FECA57'
    },
    'random': {
        'name': 'Random',
        'description': 'Selects random valid moves. Useful as a baseline for comparison.',
        'type': 'Random',
        'strength': 'Beginner',
        'color': '#A8E6CF'
    }
}

FORMATS = {
    'gen1ou': 'Gen 1 OU (Overused)',
    'gen2ou': 'Gen 2 OU',
    'gen3ou': 'Gen 3 OU',
    'gen8ou': 'Gen 8 OU',
    'gen9ou': 'Gen 9 OU',
    'gen9vgc2025regi': 'Gen 9 VGC 2025 (Doubles)'
}


@app.route('/')
def index():
    """Home page with project overview"""
    return render_template('index.html', agents=AGENTS, formats=FORMATS)


@app.route('/battle')
def battle():
    """Battle simulator page"""
    return render_template('battle.html', agents=AGENTS, formats=FORMATS)


@app.route('/agents')
def agents():
    """Agent showcase page"""
    stats = {agent: agent_stats[agent] for agent in AGENTS.keys()}
    for agent in stats:
        if stats[agent]['battles'] > 0:
            stats[agent]['win_rate'] = stats[agent]['wins'] / stats[agent]['battles'] * 100
        else:
            stats[agent]['win_rate'] = 0
    return render_template('agents.html', agents=AGENTS, stats=stats)


@app.route('/stats')
def stats():
    """Stats dashboard"""
    stats_data = {agent: agent_stats[agent] for agent in AGENTS.keys()}
    for agent in stats_data:
        if stats_data[agent]['battles'] > 0:
            stats_data[agent]['win_rate'] = stats_data[agent]['wins'] / stats_data[agent]['battles'] * 100
        else:
            stats_data[agent]['win_rate'] = 0

    return render_template('stats.html',
                         agents=AGENTS,
                         stats=stats_data,
                         battle_history=battle_history[-20:])


@app.route('/api/agents')
def api_agents():
    """API endpoint for agent information"""
    return jsonify(AGENTS)


@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    """Start a new battle simulation"""
    data = request.json
    player1 = data.get('player1', 'gen1_agent')
    player2 = data.get('player2', 'abyssal')
    battle_format = data.get('format', 'gen1ou')

    if player1 not in AGENTS or player2 not in AGENTS:
        return jsonify({'error': 'Invalid agent selection'}), 400

    if battle_format not in FORMATS:
        return jsonify({'error': 'Invalid format selection'}), 400

    # Start battle in background thread
    battle_id = f"{player1}_vs_{player2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    thread = threading.Thread(
        target=battle_runner.run_battle,
        args=(battle_id, player1, player2, battle_format)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'battle_id': battle_id,
        'player1': player1,
        'player2': player2,
        'format': battle_format,
        'status': 'started'
    })


@app.route('/api/battle_history')
def api_battle_history():
    """Get recent battle history"""
    return jsonify(battle_history[-50:])


@app.route('/api/agent_stats')
def api_agent_stats():
    """Get agent statistics"""
    stats = {}
    for agent in AGENTS.keys():
        stats[agent] = dict(agent_stats[agent])
        if stats[agent]['battles'] > 0:
            stats[agent]['win_rate'] = stats[agent]['wins'] / stats[agent]['battles'] * 100
        else:
            stats[agent]['win_rate'] = 0
    return jsonify(stats)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to PokéChamp battle server'})
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    print('Client disconnected')


@socketio.on('request_battle')
def handle_battle_request(data):
    """Handle battle request from client"""
    player1 = data.get('player1', 'gen1_agent')
    player2 = data.get('player2', 'abyssal')
    battle_format = data.get('format', 'gen1ou')

    battle_id = f"{player1}_vs_{player2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Run battle in background
    thread = threading.Thread(
        target=battle_runner.run_battle,
        args=(battle_id, player1, player2, battle_format)
    )
    thread.daemon = True
    thread.start()


def update_battle_stats(winner, loser):
    """Update agent statistics after battle"""
    agent_stats[winner]['wins'] += 1
    agent_stats[winner]['battles'] += 1
    agent_stats[loser]['losses'] += 1
    agent_stats[loser]['battles'] += 1


def record_battle(battle_data):
    """Record battle in history"""
    battle_history.append(battle_data)
    if len(battle_history) > 1000:
        battle_history.pop(0)


# Make these functions available to battle_runner
battle_runner.update_stats = update_battle_stats
battle_runner.record_battle = record_battle


if __name__ == '__main__':
    print("=" * 60)
    print("🎮 PokéChamp Showcase Web Application")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Available agents:", ", ".join(AGENTS.keys()))
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
