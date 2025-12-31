import json
from random import choice
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.types import Card, CardValue, Suit

game = CrazyEightGame(crazy=8)


def start_game():
    global game
    print("player.py starting game")
    game = CrazyEightGame(crazy=8)
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
    moves = [[c.to_dict() for c in move] for move in game.legal_moves]
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
    move = choice(game.legal_moves) if len(game.legal_moves) > 0 else None
    game.resolve_move(move)
    game.get_legal_moves()


def attempt_move(move: list[Card] | None):
    """Attempt move, determine legality and resolve gamestate"""
    if move is None or move in game.legal_moves:
        game.resolve_move(move)
        game.get_legal_moves()
        return True
    return False
