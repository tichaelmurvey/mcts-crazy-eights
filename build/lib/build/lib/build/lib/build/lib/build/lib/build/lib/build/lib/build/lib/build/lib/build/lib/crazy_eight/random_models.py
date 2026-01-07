from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crazy_eight.game_env import CrazyEightGame

from crazy_eight.types import Model
import random


class AlwaysDrawPlayer(Model):
    def __init__(self) -> None:
        super().__init__()

    def choose_move(self, game: CrazyEightGame):
        return "draw"


class RandomPlayer(Model):
    def __init__(self) -> None:
        super().__init__()

    def choose_move(self, game: CrazyEightGame):
        return random.choice(game.legal_moves)


class PlayBiasRandomPlayer(Model):
    def __init__(self) -> None:
        super().__init__()

    def choose_move(self, game: CrazyEightGame):
        if len(game.legal_moves) > 1:
            return random.choice(game.legal_moves[1:])
        return random.choice(game.legal_moves)
