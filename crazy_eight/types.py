from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import NamedTuple, Tuple


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
class Card:
    suit: Suit
    cvalue: CardValue


@dataclass
class Player:
    hand: list[Card]
    crazy: int
