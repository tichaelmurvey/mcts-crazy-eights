let pyodide = null;
let opponentHandSize = 0;

const ANIMATION_DURATION = 400;
const HIDE_OPPONENT_HAND = false;
// Hand object - source of truth for player's hand in JS
// Each entry: { suit, value, selected }
let hand = [];

function cardKey(card) {
    return `${card.suit}_${card.value}`;
}

function getSelectedCards() {
    return hand.filter(c => c.selected);
}

function syncHand(gameStateHand) {
    // Build count map of cards in new game state
    const newCounts = new Map();
    for (const card of gameStateHand) {
        const key = cardKey(card);
        newCounts.set(key, (newCounts.get(key) || 0) + 1);
    }

    // Build count map of current hand
    const currentCounts = new Map();
    for (const card of hand) {
        const key = cardKey(card);
        currentCounts.set(key, (currentCounts.get(key) || 0) + 1);
    }

    // Remove cards that are no longer in game state
    const newHand = [];
    const usedCounts = new Map();
    for (const card of hand) {
        const key = cardKey(card);
        const used = usedCounts.get(key) || 0;
        const available = newCounts.get(key) || 0;
        if (used < available) {
            newHand.push(card);
            usedCounts.set(key, used + 1);
        }
    }

    // Find cards to add (in game state but not in our hand)
    const cardsToAdd = [];
    const handCounts = new Map();
    for (const card of newHand) {
        const key = cardKey(card);
        handCounts.set(key, (handCounts.get(key) || 0) + 1);
    }
    for (const card of gameStateHand) {
        const key = cardKey(card);
        const inHand = handCounts.get(key) || 0;
        if (inHand === 0) {
            cardsToAdd.push({ suit: card.suit, value: card.value, selected: false });
            handCounts.set(key, 1);
        } else {
            handCounts.set(key, inHand - 1);
        }
    }

    hand = newHand;
    return cardsToAdd;
}

// --- Initialization ---

async function main() {
    pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = await pyodide.pyimport("micropip");
    await micropip.install("crazy_eight-0.1.0-py3-none-any.whl");
    const playerCode = await fetch("player.py").then(r => r.text());
    await pyodide.FS.writeFile("/home/pyodide/player.py", playerCode);
    await pyodide.runPython("import player; player.say_hello()");
    refreshGameState(true);
}

function new_game() {
    hand = [];
    opponentHandSize = 0;
    pyodide.runPython("player.start_game()");
    refreshGameState(true);
}

async function refreshGameState(skipAnimations = false) {
    const gameStateJson = pyodide.runPython('player.get_game_state_json()');
    const gameState = JSON.parse(gameStateJson);

    if (skipAnimations) {
        // Sync hand without animation
        const cardsToAdd = syncHand(gameState.player_hand);
        for (const card of cardsToAdd) {
            hand.push(card);
        }
        opponentHandSize = gameState.opponent_hand.length;
    }

    await renderGameState(gameState, skipAnimations);
}

// --- Card Utilities ---

function getCardImagePath(card) {
    const valueMap = {
        'ACE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5',
        'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'TEN': '10',
        'JACK': 'jack', 'QUEEN': 'queen', 'KING': 'king'
    };
    const suitMap = {
        'HEARTS': 'heart', 'SPADES': 'spade', 'DIAMONDS': 'diamond', 'CLUBS': 'club'
    };
    return `img/cards/${suitMap[card.suit]}_${valueMap[card.value]}.png`;
}

function createCardElement(card, isBack = false) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    const img = document.createElement("img");
    img.src = isBack ? "img/cards/back-blue.png" : getCardImagePath(card);
    cardDiv.appendChild(img);

    if (!isBack && card) {
        cardDiv.dataset.suit = card.suit;
        cardDiv.dataset.value = card.value;
    }
    return cardDiv;
}

function cardsToPythonExpr(cards) {
    return cards.map(c =>
        `player.Card(suit=player.Suit.${c.suit}, cvalue=player.CardValue.${c.value})`
    ).join(', ');
}

// --- Animation ---

function animateCard(cardEl, targetRect, onComplete) {
    const startRect = cardEl.getBoundingClientRect();
    const deltaX = targetRect.left - startRect.left;
    const deltaY = targetRect.top - startRect.top;

    cardEl.classList.add('animating');
    cardEl.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
    cardEl.style.zIndex = '1000';

    setTimeout(() => {
        cardEl.remove();
        onComplete?.();
    }, ANIMATION_DURATION);
}

function animateCardAsync(cardEl, targetRect) {
    return new Promise(resolve => animateCard(cardEl, targetRect, resolve));
}

async function animateNewCardTo(targetEl) {
    const deckEl = document.getElementById('deck');
    const deckCard = deckEl.querySelector('.card');
    const deckRect = deckCard.getBoundingClientRect();
    const targetRect = targetEl.getBoundingClientRect();

    const deltaX = (targetRect.left + targetRect.width / 2) - deckRect.left;
    const deltaY = targetRect.top - deckRect.top;

    const animCard = createCardElement(null, true);
    deckEl.appendChild(animCard);
    animCard.style.position = 'absolute';
    animCard.style.top = '0';
    animCard.style.left = '0';

    // Force reflow then animate
    animCard.offsetHeight;
    animCard.classList.add('animating');
    animCard.style.transform = `translate(${deltaX}px, ${deltaY}px)`;

    await new Promise(resolve => setTimeout(() => {
        animCard.remove();
        resolve();
    }, ANIMATION_DURATION));
}

// --- Rendering ---

async function renderGameState(gameState, skipAnimations = false) {
    // Sync hand and get cards to add
    const cardsToAdd = skipAnimations ? [] : syncHand(gameState.player_hand);
    const opponentCards = gameState.opponent_hand
    const opponentCardsToAdd = skipAnimations ? 0 : Math.max(0, gameState.opponent_hand.length - opponentHandSize);
    const opponentCardsToShow = gameState.opponent_hand.length - opponentCardsToAdd;

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
    for (let i = 0; i < opponentCards.length; i++) {
        const card = createCardElement(opponentCards[i], HIDE_OPPONENT_HAND);
        card.style.cursor = 'default';
        opponentHand.appendChild(card);
    }
    cardTable.appendChild(opponentHand);

    // Center area with deck and discard
    const centerArea = document.createElement('div');
    centerArea.className = 'center-area';

    const deck = document.createElement('div');
    deck.className = 'deck';
    deck.id = 'deck';
    deck.appendChild(createCardElement(null, true));
    deck.addEventListener('click', drawCard);
    centerArea.appendChild(deck);

    const discard = document.createElement('div');
    discard.className = 'discard';
    discard.id = 'discard';
    if (gameState.top_card) {
        discard.appendChild(createCardElement(gameState.top_card));
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

    hand.forEach((card, index) => {
        const cardEl = createCardElement(card);
        cardEl.dataset.index = index;
        if (card.selected) {
            cardEl.classList.add('selected');
        }
        cardEl.addEventListener('click', (e) => {
            const idx = parseInt(e.currentTarget.dataset.index, 10);
            toggleCardSelection(idx);
        });
        playerHandDiv.appendChild(cardEl);
    });

    handContainer.appendChild(playerHandDiv);
    playerControls.appendChild(handContainer);

    initSortable(playerHandDiv);

    const playBtn = document.createElement('button');
    playBtn.id = 'play-btn';
    playBtn.textContent = 'Play Selected';
    playBtn.disabled = true;
    playBtn.addEventListener('click', attemptPlayMove);
    playerControls.appendChild(playBtn);

    cardTable.appendChild(playerControls);

    const statusMsg = document.createElement('div');
    statusMsg.id = 'status-message';
    cardTable.appendChild(statusMsg);

    // Animate drawn cards
    for (const card of cardsToAdd) {
        await animateNewCardTo(playerHandDiv);
        hand.push(card);
        const cardEl = createCardElement(card);
        cardEl.dataset.index = hand.length - 1;
        cardEl.addEventListener('click', (e) => {
            const idx = parseInt(e.currentTarget.dataset.index, 10);
            toggleCardSelection(idx);
        });
        playerHandDiv.appendChild(cardEl);
    }

    // Update opponent hand size
    opponentHandSize = gameState.opponent_hand.length;

    updatePlayButtonState();

    if (gameState.winner !== null) {
        showWinner(gameState.winner);
    } else if (gameState.current_player === 0) {
        showStatus("Your turn!");
        setTimeout(hideStatus, 1500);
    } else {
        showStatus("Opponent's turn...");
        setTimeout(opponentTurn, 1000);
    }
}

function initSortable(playerHandDiv) {
    new Sortable(playerHandDiv, {
        animation: 150,
        ghostClass: 'dragging',
        onEnd: function (evt) {
            if (evt.oldIndex === evt.newIndex) return;

            // Reorder the hand array
            const [movedCard] = hand.splice(evt.oldIndex, 1);
            hand.splice(evt.newIndex, 0, movedCard);

            // Update data-index attributes
            playerHandDiv.querySelectorAll('.card').forEach((el, i) => {
                el.dataset.index = i;
            });

            updatePlayButtonState();
        }
    });
}

// --- Selection & Validation ---

function toggleCardSelection(index) {
    hand[index].selected = !hand[index].selected;

    const cardEl = document.querySelector(`#player-hand .card[data-index="${index}"]`);
    if (cardEl) {
        cardEl.classList.toggle('selected', hand[index].selected);
    }

    updatePlayButtonState();
}

function updatePlayButtonState() {
    const playBtn = document.getElementById('play-btn');
    if (!playBtn) return;

    const selected = getSelectedCards();
    if (selected.length === 0) {
        playBtn.disabled = true;
        return;
    }

    const isValid = pyodide.runPython(`player.validate_move([${cardsToPythonExpr(selected)}])`);
    playBtn.disabled = !isValid;
}

// --- Player Actions ---

async function attemptPlayMove() {
    const selected = getSelectedCards();
    if (selected.length === 0) return;

    const discardRect = document.getElementById('discard').getBoundingClientRect();

    // Animate cards in selection order (order in hand array)
    for (let i = 0; i < hand.length; i++) {
        if (hand[i].selected) {
            const cardEl = document.querySelector(`#player-hand .card[data-index="${i}"]`);
            if (cardEl) {
                await animateCardAsync(cardEl, discardRect);
            }
        }
    }

    const result = pyodide.runPython(`player.attempt_move([${cardsToPythonExpr(selected)}])`);

    if (result) {
        refreshGameState();
    } else {
        showStatus("Invalid move!");
        setTimeout(() => {
            hideStatus();
            refreshGameState();
        }, 1500);
    }
}

async function drawCard() {
    pyodide.runPython('player.attempt_move("draw")');
    await refreshGameState();
}

// --- Opponent Actions ---

async function opponentTurn() {
    showStatus("Opponent is thinking...");
    await new Promise(resolve => setTimeout(resolve, 1000));

    const moveJson = pyodide.runPython('player.model_move()');
    const cardsPlayed = JSON.parse(moveJson);

    hideStatus();

    // Animate played cards before refreshing state
    if (cardsPlayed !== null) {
        const discardRect = document.getElementById('discard').getBoundingClientRect();
        for (const card of cardsPlayed) {
            await animateOpponentCard(card, discardRect);
        }
    }

    await refreshGameState();
}

async function animateOpponentCard(card, targetRect) {
    const opponentHand = document.querySelector('.hand.opponent');
    const cardEl = opponentHand?.querySelector('.card');

    if (!cardEl) return;

    // Flip to face before animating
    const img = cardEl.querySelector('img');
    if (img) img.src = getCardImagePath(card);

    await animateCardAsync(cardEl, targetRect);
}

// --- UI Helpers ---

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
        location.reload();
    });
}

// Initialize on load
main();
