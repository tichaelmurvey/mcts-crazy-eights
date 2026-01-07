from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from crazy_eight.types import CardValue, Suit
    from crazy_eight.types import Move


def format_card(card: Card) -> str:
    """Format a card for display."""
    suit_symbols = {
        "HEARTS": "♥",
        "SPADES": "♠",
        "DIAMONDS": "♦",
        "CLUBS": "♣",
    }
    value_display = {
        "ACE": "A",
        "TWO": "2",
        "THREE": "3",
        "FOUR": "4",
        "FIVE": "5",
        "SIX": "6",
        "SEVEN": "7",
        "EIGHT": "8",
        "NINE": "9",
        "TEN": "10",
        "JACK": "J",
        "QUEEN": "Q",
        "KING": "K",
    }
    symbol = suit_symbols.get(card.suit.name, card.suit.name)
    value = value_display.get(card.cvalue.name, card.cvalue.name)
    return f"{value}{symbol}"


def format_move(move: Move) -> str:
    if isinstance(move, str):
        return "Draw Card"
    card_strs = [card.to_str() for card in move]
    return ", ".join(card_strs)


@dataclass
class Card:
    suit: Suit
    cvalue: CardValue

    def to_dict(self):
        return {"suit": self.suit.name, "value": self.cvalue.name}

    def to_str(self):
        return format_card(self)
