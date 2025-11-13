/**
 * PokéChamp Web App - Battle Simulator
 */

let socket = null;
let currentBattle = null;
let battleLog = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeBattle();
});

function initializeBattle() {
    // Initialize socket
    socket = window.pokechamp.initSocket();

    // Set up event listeners
    document.getElementById('startBattleBtn').addEventListener('click', startBattle);
    document.getElementById('newBattleBtn')?.addEventListener('click', resetBattle);

    // Update agent info on selection change
    document.getElementById('player1Select').addEventListener('change', updatePlayer1Info);
    document.getElementById('player2Select').addEventListener('change', updatePlayer2Info);

    // Initial agent info update
    updatePlayer1Info();
    updatePlayer2Info();

    // Listen for battle events
    socket.on('battle_event', handleBattleEvent);

    console.log('Battle simulator initialized');
}

function updatePlayer1Info() {
    const select = document.getElementById('player1Select');
    const agentId = select.value;
    const agent = AGENTS_DATA[agentId];
    const infoDiv = document.getElementById('player1Info');

    if (agent) {
        infoDiv.innerHTML = `
            <div style="color: ${agent.color}">
                <strong>${agent.type}</strong> • ${agent.strength}
            </div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                ${agent.description}
            </div>
        `;
    }
}

function updatePlayer2Info() {
    const select = document.getElementById('player2Select');
    const agentId = select.value;
    const agent = AGENTS_DATA[agentId];
    const infoDiv = document.getElementById('player2Info');

    if (agent) {
        infoDiv.innerHTML = `
            <div style="color: ${agent.color}">
                <strong>${agent.type}</strong> • ${agent.strength}
            </div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                ${agent.description}
            </div>
        `;
    }
}

function startBattle() {
    const player1 = document.getElementById('player1Select').value;
    const player2 = document.getElementById('player2Select').value;
    const format = document.getElementById('formatSelect').value;

    if (player1 === player2) {
        window.pokechamp.showNotification('Please select different agents', 'error');
        return;
    }

    // Hide config, show arena
    document.getElementById('battleConfig').style.display = 'none';
    document.getElementById('battleArena').style.display = 'block';
    document.getElementById('battleResult').style.display = 'none';

    // Reset battle state
    battleLog = [];
    clearBattleLog();
    addLogEntry('Initializing battle...', 'info');

    // Update battle info
    const player1Name = AGENTS_DATA[player1].name;
    const player2Name = AGENTS_DATA[player2].name;
    document.getElementById('battleTitle').textContent = `${player1Name} vs ${player2Name}`;
    document.getElementById('battleFormat').textContent = format.toUpperCase();

    // Initialize Pokemon displays
    document.getElementById('player1Name').textContent = player1Name;
    document.getElementById('player2Name').textContent = player2Name;
    resetPokemonDisplay('player1');
    resetPokemonDisplay('player2');

    // Start the battle via API
    fetch('/api/start_battle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            player1: player1,
            player2: player2,
            format: format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            window.pokechamp.showNotification(data.error, 'error');
            resetBattle();
        } else {
            currentBattle = data;
            addLogEntry(`Battle started: ${data.battle_id}`, 'success');
            window.pokechamp.showNotification('Battle started!', 'success');
        }
    })
    .catch(error => {
        console.error('Error starting battle:', error);
        window.pokechamp.showNotification('Failed to start battle', 'error');
        resetBattle();
    });
}

function handleBattleEvent(event) {
    console.log('Battle event:', event);

    switch (event.type) {
        case 'battle_start':
            addLogEntry(`Battle begins: ${event.data.player1} vs ${event.data.player2}`, 'info');
            break;

        case 'turn_start':
            addLogEntry(`--- Turn ${event.data.turn} ---`, 'turn');
            document.getElementById('battleTurn').textContent = `Turn: ${event.data.turn}`;
            break;

        case 'move_used':
            addLogEntry(`${event.data.pokemon} used ${event.data.move}`, 'move');
            break;

        case 'damage':
            addLogEntry(`${event.data.target} took ${event.data.damage} damage`, 'damage');
            updatePokemonHP(event.data.target, event.data.hp_percent);
            break;

        case 'faint':
            addLogEntry(`${event.data.pokemon} fainted!`, 'faint');
            break;

        case 'switch':
            addLogEntry(`${event.data.pokemon} switched in!`, 'switch');
            break;

        case 'battle_state':
            updateBattleState(event.data);
            break;

        case 'battle_end':
            handleBattleEnd(event.data);
            break;

        case 'battle_error':
            window.pokechamp.showNotification('Battle error: ' + event.data.error, 'error');
            addLogEntry('Battle error occurred', 'error');
            break;
    }
}

function updateBattleState(state) {
    if (!state) return;

    // Update turn
    if (state.turn) {
        document.getElementById('battleTurn').textContent = `Turn: ${state.turn}`;
    }

    // Update active Pokemon
    if (state.player) {
        updatePokemonDisplay('player1', state.player);
    }

    if (state.opponent) {
        updatePokemonDisplay('player2', state.opponent);
    }

    // Update teams
    if (state.player_team) {
        updateTeamDisplay('player1Team', state.player_team);
    }

    if (state.opponent_team) {
        updateTeamDisplay('player2Team', state.opponent_team);
    }
}

function updatePokemonDisplay(side, pokemon) {
    if (!pokemon) return;

    document.getElementById(`${side}Name`).textContent = pokemon.species || '-';

    // Update HP
    const hpPercent = pokemon.hp_fraction ? pokemon.hp_fraction * 100 : 0;
    updatePokemonHP(side, hpPercent);

    // Update status
    const statusDiv = document.getElementById(`${side}Status`);
    if (pokemon.status) {
        statusDiv.textContent = pokemon.status.toUpperCase();
        statusDiv.style.display = 'block';
    } else {
        statusDiv.style.display = 'none';
    }

    // Update types
    const typesDiv = document.getElementById(`${side}Types`);
    if (pokemon.types && pokemon.types.length > 0) {
        typesDiv.innerHTML = pokemon.types
            .map(type => `<span class="type-badge">${type}</span>`)
            .join('');
    }

    // Update sprite (use emoji based on type or default)
    const sprite = getPokemonSprite(pokemon);
    document.getElementById(`${side}Sprite`).textContent = sprite;
}

function getPokemonSprite(pokemon) {
    if (!pokemon || !pokemon.types) return '❓';

    // Simple emoji mapping based on primary type
    const typeEmojis = {
        'fire': '🔥',
        'water': '💧',
        'grass': '🌿',
        'electric': '⚡',
        'ice': '❄️',
        'fighting': '🥊',
        'poison': '☠️',
        'ground': '🏔️',
        'flying': '🦅',
        'psychic': '🧠',
        'bug': '🐛',
        'rock': '🪨',
        'ghost': '👻',
        'dragon': '🐉',
        'dark': '🌙',
        'steel': '⚙️',
        'fairy': '🧚',
        'normal': '⭐'
    };

    const primaryType = pokemon.types[0].toLowerCase();
    return typeEmojis[primaryType] || '❓';
}

function updatePokemonHP(side, percent) {
    const hpBar = document.getElementById(`${side}HP`);
    const hpText = document.getElementById(`${side}HPText`);

    if (hpBar) {
        hpBar.style.width = percent + '%';

        // Change color based on HP
        if (percent < 25) {
            hpBar.classList.add('low');
        } else {
            hpBar.classList.remove('low');
        }
    }

    if (hpText) {
        hpText.textContent = Math.round(percent) + '%';
    }
}

function updateTeamDisplay(teamId, team) {
    const teamDiv = document.getElementById(teamId);
    if (!teamDiv || !team) return;

    teamDiv.innerHTML = team.map(pokemon => {
        const sprite = getPokemonSprite(pokemon);
        const fainted = pokemon.fainted ? 'fainted' : '';
        const title = `${pokemon.species} (${Math.round(pokemon.hp_fraction * 100)}%)`;
        return `<div class="team-pokemon ${fainted}" title="${title}">${sprite}</div>`;
    }).join('');
}

function resetPokemonDisplay(side) {
    document.getElementById(`${side}Name`).textContent = '-';
    document.getElementById(`${side}Sprite`).textContent = side === 'player1' ? '🐉' : '🐲';
    updatePokemonHP(side, 100);
    document.getElementById(`${side}Status`).style.display = 'none';
    document.getElementById(`${side}Types`).innerHTML = '';
}

function handleBattleEnd(data) {
    addLogEntry(`Battle ended! Winner: ${data.winner}`, 'success');

    // Show result
    document.getElementById('battleResult').style.display = 'block';
    document.getElementById('resultTitle').textContent = 'Battle Complete!';
    document.getElementById('winnerDisplay').textContent = `🏆 ${AGENTS_DATA[data.winner]?.name || data.winner} wins!`;
    document.getElementById('resultTurns').textContent = data.turns || '?';

    window.pokechamp.showNotification(`${data.winner} wins!`, 'success');

    // Update final state if available
    if (data.player1_final) {
        updateBattleState(data.player1_final);
    }
}

function resetBattle() {
    document.getElementById('battleConfig').style.display = 'block';
    document.getElementById('battleArena').style.display = 'none';
    document.getElementById('battleResult').style.display = 'none';
    currentBattle = null;
    battleLog = [];
}

function addLogEntry(message, type = 'info') {
    battleLog.push({ message, type, timestamp: new Date() });

    const logContainer = document.getElementById('battleLog');
    if (!logContainer) return;

    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;

    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearBattleLog() {
    const logContainer = document.getElementById('battleLog');
    if (logContainer) {
        logContainer.innerHTML = '';
    }
}

// Handle URL parameters (for direct links to battles)
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const player1 = urlParams.get('player1');
    const player2 = urlParams.get('player2');
    const format = urlParams.get('format');

    if (player1) {
        document.getElementById('player1Select').value = player1;
        updatePlayer1Info();
    }

    if (player2) {
        document.getElementById('player2Select').value = player2;
        updatePlayer2Info();
    }

    if (format) {
        document.getElementById('formatSelect').value = format;
    }
});
