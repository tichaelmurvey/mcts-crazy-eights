let pyodide = null;
let selectedCards = [];
let playerHand = [];

async function main() {
    pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = await pyodide.pyimport("micropip");
    await micropip.install("crazy_eight-0.1.0-py3-none-any.whl");
    const testCode = await fetch("player.py").then(r => r.text());
    await pyodide.FS.writeFile("/home/pyodide/player.py", testCode);
    await pyodide.runPython("import player; player.say_hello()");

    const gameStateJson = pyodide.runPython('player.get_game_state_json()');
    console.log(gameStateJson);
    renderGameState(JSON.parse(gameStateJson));
}

function new_game() {
    console.log("starting new game")
    pyodide.runPython("player.start_game()")
    const gameStateJson = pyodide.runPython('player.get_game_state_json()');
    renderGameState(JSON.parse(gameStateJson));
}

function getCardSvgId(card) {
    // Convert card value/suit to SVG sprite ID
    // Values: ACE, TWO, THREE... -> 1, 2, 3...
    // Suits: HEARTS, SPADES, DIAMONDS, CLUBS -> heart, spade, diamond, club
    const valueMap = {
        'ACE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5',
        'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'TEN': '10',
        'JACK': 'jack', 'QUEEN': 'queen', 'KING': 'king'
    };
    const suitMap = {
        'HEARTS': 'heart', 'SPADES': 'spade', 'DIAMONDS': 'diamond', 'CLUBS': 'club'
    };



    const value = valueMap[card.value];
    const suit = suitMap[card.suit];
    return `img/cards/${suit}_${value}.png`;
}

function createCardElement(card, isBack = false) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    const img = document.createElement("img");
    if (isBack) {
        img.setAttribute("src", "img/cards/back-blue.png")
    }
    if (card) {
        img.setAttribute("src", getCardSvgId(card))
    }
    cardDiv.appendChild(img);

    if (!isBack && card) {
        cardDiv.dataset.suit = card.suit;
        cardDiv.dataset.value = card.value;
    }

    return cardDiv;
}

function renderGameState(gameState) {
    console.log("rendering game state")
    console.log(gameState)
    selectedCards = [];
    playerHand = [...gameState.player_hand];

    // Update info bar
    document.getElementById('opponent-cards').textContent = `Computer: ${gameState.opponent_hand.length} cards`;
    document.getElementById('opponent-wild').textContent = `Wild: ${gameState.opponent_crazy}`;
    document.getElementById('player-wild').textContent = `Your Wild: ${gameState.player_crazy}`;

    // Clear and rebuild card table
    const cardTable = document.getElementById('card-table');
    cardTable.innerHTML = '';

    // Opponent hand (card backs)
    const opponentHand = document.createElement('div');
    opponentHand.className = 'hand opponent';
    gameState.opponent_hand.forEach(() => {
        const card = createCardElement(null, true);
        card.style.cursor = 'default';
        opponentHand.appendChild(card);
    });
    cardTable.appendChild(opponentHand);

    // Center area with deck and discard
    const centerArea = document.createElement('div');
    centerArea.className = 'center-area';

    // Deck
    const deck = document.createElement('div');
    deck.className = 'deck';
    deck.id = 'deck';
    const deckCard = createCardElement(null, true);
    deck.appendChild(deckCard);
    deck.addEventListener('click', () => drawCard());
    centerArea.appendChild(deck);

    // Discard pile
    const discard = document.createElement('div');
    discard.className = 'discard';
    discard.id = 'discard';
    if (gameState.top_card) {
        const discardCard = createCardElement(gameState.top_card);
        discard.appendChild(discardCard);
    }
    centerArea.appendChild(discard);

    cardTable.appendChild(centerArea);

    // Player hand with play button
    const playerControls = document.createElement('div');
    playerControls.className = 'player-controls';

    const handContainer = document.createElement('div');
    handContainer.className = 'hand-container';

    const playerHandDiv = document.createElement('div');
    playerHandDiv.className = 'hand player';
    playerHandDiv.id = 'player-hand';

    playerHand.forEach((card, index) => {
        const cardEl = createCardElement(card);
        cardEl.dataset.index = index;

        // Click to select/deselect
        cardEl.addEventListener('click', () => toggleCardSelection(cardEl, index));

        playerHandDiv.appendChild(cardEl);
    });

    handContainer.appendChild(playerHandDiv);
    playerControls.appendChild(handContainer);

    // Initialize SortableJS for drag reordering
    new Sortable(playerHandDiv, {
        animation: 150,
        ghostClass: 'dragging',
        onEnd: function(evt) {
            const oldIndex = evt.oldIndex;
            const newIndex = evt.newIndex;

            if (oldIndex !== newIndex) {
                // Reorder the playerHand array
                const [movedCard] = playerHand.splice(oldIndex, 1);
                playerHand.splice(newIndex, 0, movedCard);

                // Update selected cards indices
                selectedCards = selectedCards.map(idx => {
                    if (idx === oldIndex) return newIndex;
                    if (oldIndex < newIndex) {
                        if (idx > oldIndex && idx <= newIndex) return idx - 1;
                    } else {
                        if (idx >= newIndex && idx < oldIndex) return idx + 1;
                    }
                    return idx;
                });

                // Update data-index attributes
                playerHandDiv.querySelectorAll('.card').forEach((el, i) => {
                    el.dataset.index = i;
                });
            }
        }
    });

    // Play button
    const playBtn = document.createElement('button');
    playBtn.id = 'play-btn';
    playBtn.textContent = 'Play Selected';
    playBtn.disabled = true;
    playBtn.addEventListener('click', () => attemptPlayMove());
    playerControls.appendChild(playBtn);

    cardTable.appendChild(playerControls);

    // Status message container
    const statusMsg = document.createElement('div');
    statusMsg.id = 'status-message';
    cardTable.appendChild(statusMsg);

    // Check for winner
    if (gameState.winner !== null) {
        showWinner(gameState.winner);
    }

    // Indicate current player
    if (gameState.current_player === 0) {
        showStatus("Your turn!");
        setTimeout(() => hideStatus(), 1500);
    } else {
        showStatus("Opponent's turn...");
        setTimeout(() => {
            opponentTurn();
        }, 1000);
    }
}

function toggleCardSelection(cardEl, index) {
    const selectedIndex = selectedCards.indexOf(index);

    if (selectedIndex === -1) {
        selectedCards.push(index);
        cardEl.classList.add('selected');
    } else {
        selectedCards.splice(selectedIndex, 1);
        cardEl.classList.remove('selected');
    }

    // Update play button state
    const playBtn = document.getElementById('play-btn');
    playBtn.disabled = selectedCards.length === 0;
}


function rerenderPlayerHand() {
    const playerHandDiv = document.getElementById('player-hand');
    playerHandDiv.innerHTML = '';

    playerHand.forEach((card, index) => {
        const cardEl = createCardElement(card);
        cardEl.dataset.index = index;

        if (selectedCards.includes(index)) {
            cardEl.classList.add('selected');
        }

        cardEl.addEventListener('click', () => toggleCardSelection(cardEl, index));

        playerHandDiv.appendChild(cardEl);
    });

    // Re-initialize SortableJS
    new Sortable(playerHandDiv, {
        animation: 150,
        ghostClass: 'dragging',
        onEnd: function(evt) {
            const oldIndex = evt.oldIndex;
            const newIndex = evt.newIndex;

            if (oldIndex !== newIndex) {
                const [movedCard] = playerHand.splice(oldIndex, 1);
                playerHand.splice(newIndex, 0, movedCard);

                selectedCards = selectedCards.map(idx => {
                    if (idx === oldIndex) return newIndex;
                    if (oldIndex < newIndex) {
                        if (idx > oldIndex && idx <= newIndex) return idx - 1;
                    } else {
                        if (idx >= newIndex && idx < oldIndex) return idx + 1;
                    }
                    return idx;
                });

                playerHandDiv.querySelectorAll('.card').forEach((el, i) => {
                    el.dataset.index = i;
                });
            }
        }
    });
}

async function attemptPlayMove() {
    if (selectedCards.length === 0) return;

    // Get selected cards in hand order (left to right)
    const sortedIndices = [...selectedCards].sort((a, b) => a - b);
    const cardsToPlay = sortedIndices.map(i => playerHand[i]);

    // Animate cards to discard one by one
    const discardEl = document.getElementById('discard');
    const discardRect = discardEl.getBoundingClientRect();

    for (let i = 0; i < sortedIndices.length; i++) {
        const cardIndex = sortedIndices[i];
        const cardEl = document.querySelector(`#player-hand .card[data-index="${cardIndex}"]`);

        if (cardEl) {
            await animateCardToDiscard(cardEl, discardRect);
        }
    }

    // Build Python-compatible card list
    const cardListStr = cardsToPlay.map(c =>
        `player.Card(suit=player.Suit.${c.suit}, cvalue=player.CardValue.${c.value})`
    ).join(', ');

    // Attempt the move
    const result = pyodide.runPython(`player.attempt_move([${cardListStr}])`);

    if (result) {
        // Move succeeded, refresh game state
        const gameStateJson = pyodide.runPython('player.get_game_state_json()');
        renderGameState(JSON.parse(gameStateJson));
    } else {
        // Move failed, show error
        showStatus("Invalid move!");
        setTimeout(() => {
            hideStatus();
            // Deselect all cards
            selectedCards = [];
            rerenderPlayerHand();
            document.getElementById('play-btn').disabled = true;
        }, 1500);
    }
}

async function animateCardToDiscard(cardEl, targetRect) {
    return new Promise(resolve => {
        const startRect = cardEl.getBoundingClientRect();

        // Create a clone for animation
        const clone = cardEl.cloneNode(true);
        clone.classList.add('animating');
        clone.style.left = startRect.left + 'px';
        clone.style.top = startRect.top + 'px';
        clone.style.width = startRect.width + 'px';
        clone.style.height = startRect.height + 'px';
        document.body.appendChild(clone);

        // Hide original
        cardEl.style.visibility = 'hidden';

        // Trigger animation
        requestAnimationFrame(() => {
            clone.style.left = targetRect.left + 'px';
            clone.style.top = targetRect.top + 'px';
        });

        // Cleanup after animation
        setTimeout(() => {
            clone.remove();
            resolve();
        }, 400);
    });
}

async function drawCard() {
    // Animate card from deck
    const deckEl = document.getElementById('deck');
    const playerHandDiv = document.getElementById('player-hand');
    const deckRect = deckEl.getBoundingClientRect();
    const handRect = playerHandDiv.getBoundingClientRect();

    // Create animated card back
    const animCard = createCardElement(null, true);
    animCard.classList.add('animating');
    animCard.style.left = deckRect.left + 'px';
    animCard.style.top = deckRect.top + 'px';
    animCard.style.width = '80px';
    animCard.style.height = '112px';
    document.body.appendChild(animCard);

    // Animate to hand
    requestAnimationFrame(() => {
        animCard.style.left = (handRect.left + handRect.width / 2) + 'px';
        animCard.style.top = handRect.top + 'px';
    });

    await new Promise(r => setTimeout(r, 400));
    animCard.remove();

    // Execute draw (pass None to attempt_move)
    pyodide.runPython('player.attempt_move(None)');

    // Refresh game state
    const gameStateJson = pyodide.runPython('player.get_game_state_json()');
    renderGameState(JSON.parse(gameStateJson));
}

function opponentTurn() {
    // Simple AI: get legal moves and pick one
    const legalMovesJson = pyodide.runPython('player.get_legal_moves_json()');
    const legalMoves = JSON.parse(legalMovesJson);

    // Switch current player context (would need backend support)
    // For now, just advance the turn automatically
    showStatus("Opponent is thinking...");

    setTimeout(() => {
        // The opponent plays - this needs proper backend support
        // For demo, just draw a card
        pyodide.runPython('player.random_move()');

        hideStatus();
        const gameStateJson = pyodide.runPython('player.get_game_state_json()');
        renderGameState(JSON.parse(gameStateJson));
    }, 1500);
}

function showStatus(message) {
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.classList.add('visible');
    }
}

function hideStatus() {
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.classList.remove('visible');
    }
}

function showWinner(winnerIndex) {
    const overlay = document.createElement('div');
    overlay.className = 'winner-overlay';

    const message = document.createElement('div');
    message.className = 'winner-message';
    message.textContent = winnerIndex === 0 ? 'You Win!' : 'Computer Wins!';

    overlay.appendChild(message);
    document.body.appendChild(overlay);

    overlay.addEventListener('click', () => {
        overlay.remove();
        // Reload for new game
        location.reload();
    });
}

// Initialize on load
main();
