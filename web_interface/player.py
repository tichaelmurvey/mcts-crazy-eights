import json
from random import choice
from crazy_eight.card import format_move
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.mcts_model import MCTS
from crazy_eight.random_models import PlayBiasRandomPlayer
from crazy_eight.types import Card, CardValue, Move, Suit

game = CrazyEightGame()
model = MCTS(
    rollout_mover=PlayBiasRandomPlayer(),
    max_time=1.0,
    verbose=True,
)


def start_game():
    global game
    print("player.py starting game")
    game = CrazyEightGame(crazy=3)
    game.deal()
    game.get_legal_moves()
    print("player 0 hand, player 1 hand")
    print(game.players[0].hand, game.players[1].hand)


def say_hello():
    print("hello player!")


def get_moves():
    print("player.py legal moves")
    print(game.legal_moves)
    return game.legal_moves


def get_legal_moves_json():
    """Get legal moves as JSON."""
    moves = [
        ["draw" if isinstance(move, str) else c.to_dict() for c in move]  # type: ignore
        for move in game.legal_moves
    ]
    return json.dumps(moves)


def get_game_state_json():
    print("player.py get_game_state_json")
    """Get full game state as JSON for JavaScript."""

    state = {
        "player_hand": [c.to_dict() for c in game.players[0].hand],
        "opponent_hand": [c.to_dict() for c in game.players[1].hand],
        "top_card": game.top_card.to_dict() if game.top_card else None,
        "deck_size": len(game.deck),
        "current_player": game.players.index(game.current_player),
        "player_crazy": game.players[0].crazy,
        "opponent_crazy": game.players[1].crazy,
        "winner": game.winner,
    }
    print("game state from player.py")
    print(state)
    return json.dumps(state)


def random_move():
    """Execute a random legal move and return the cards played as JSON."""
    move = choice(game.legal_moves) if len(game.legal_moves) > 0 else "draw"
    game.resolve_move(move)
    game.get_legal_moves()
    if isinstance(move, str):
        return json.dumps(None)
    return json.dumps([c.to_dict() for c in move])


def model_move():
    global model
    move = model.choose_move(game)
    game.resolve_move(move)
    game.get_legal_moves()
    print(format_move(move))
    if isinstance(move, str):
        return json.dumps(None)
    return json.dumps([c.to_dict() for c in move])


def validate_move(move: list[Card]):
    return move in game.legal_moves


def attempt_move(move: Move):
    """Attempt move, determine legality and resolve gamestate."""
    if move is None or move in game.legal_moves:
        game.resolve_move(move)
        game.get_legal_moves()
        return True
    return False
