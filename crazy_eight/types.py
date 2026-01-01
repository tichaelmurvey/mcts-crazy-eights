from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Callable, Literal

from crazy_eight.card import Card


if TYPE_CHECKING:
    from crazy_eight.game_env import CrazyEightGame


class Suit(Enum):
    HEARTS = 0
    SPADES = 1
    DIAMONDS = 2
    CLUBS = 3


class CardValue(IntEnum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


@dataclass
class Player:
    hand: list[Card]
    crazy: int
    idx: int


type Move = list[Card] | Literal["draw"]
type Model = Callable[[CrazyEightGame, int], Move]
