"""
Crazy Eights game interface for Pyodide (browser).
Uses the crazy_eight module loaded via pyodide.FS.
"""

import json
from random import choice
from crazy_eight.game_env import CrazyEightGame


def create_game():
    return CrazyEightGame(n_players=2)


def get_game_state_json(game):
    """Get full game state as JSON for JavaScript."""
    state = {
        "player_hand": [c.to_dict() for c in game.players[0].hand],
        "opponent_hand": [c.to_dict() for c in game.players[1].hand],
        "discard": [c.to_dict() for c in game.discard],
        "deck_size": len(game.deck),
        "current_player": game.players.index(game.current_player),
        "player_crazy": game.players[0].crazy,
        "opponent_crazy": game.players[1].crazy,
        "winner": game.winner,
    }
    return json.dumps(state)


def get_legal_moves_json(game):
    """Get legal moves as JSON."""
    moves = [[c.to_dict() for c in move] for move in game.legal_moves]
    return json.dumps(moves)


def play_move(game, move_index):
    """Play a specific move by index."""
    if 0 <= move_index < len(game.legal_moves):
        move = game.legal_moves[move_index]
        game.resolve_move(move)


def play_draw(game):
    """Draw a card (pass None as move)."""
    game.resolve_move(None)


def computer_play(game):
    """Computer plays a random move, returns description."""
    game.get_legal_moves()

    if not game.legal_moves:
        game.resolve_move(None)
        return "draw"

    move = choice(game.legal_moves)
    move_str = ", ".join(f"{c.cvalue.name} of {c.suit.name}" for c in move)
    game.resolve_move(move)
    return move_str
