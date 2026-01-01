from crazy_eight.game_env import CrazyEightGame


import random

from crazy_eight.types import Move


def random_move(game: CrazyEightGame, iterations=0) -> Move:
    """Execute a random legal move and return the cards played as JSON."""
    return random.choice(game.legal_moves)


def random_move_play_card_bias(game: CrazyEightGame, iterations=0) -> Move:
    """Execute a random legal move and return the cards played as JSON."""
    if len(game.legal_moves) > 1:
        return random.choice(game.legal_moves[1:])
    return random.choice(game.legal_moves)
