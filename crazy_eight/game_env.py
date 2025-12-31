from itertools import permutations, product
from random import shuffle
from typing import Literal

from crazy_eight.types import Card, CardValue, Player, Suit


class CrazyEightGame:
    players: list[Player]
    deck: list[Card]
    discard: list[Card]
    top_card: Card | None
    current_player: Player
    draw_two_mult: int
    winner: int | None
    legal_moves: list[list[Card]]
    crazy: int

    def __init__(self, n_players: int = 2, crazy: int = 8) -> None:
        self.crazy = crazy
        self.players = [Player(hand=[], crazy=self.crazy) for _ in range(n_players)]
        self.current_player = self.players[0]
        self.deck = setup_deck()
        self.discard = []
        self.draw_two_mult = 1
        self.winner = None
        self.legal_moves = []
        self.top_card = None

    def get_legal_moves(self):
        legal_moves: list[list[Card]] = []
        if self.top_card is None:
            self.legal_moves = []
            return

        for active_card in self.current_player.hand:
            if (
                active_card.suit == self.top_card.suit
                or active_card.cvalue.value == self.current_player.crazy
            ):
                legal_moves.append([active_card])
                cardset = list(
                    filter(
                        lambda card, ac=active_card: card.cvalue == ac.cvalue
                        and card is not ac,
                        self.current_player.hand,
                    )
                )
                for i in range(len(cardset)):
                    cardsets = [
                        [active_card] + list(move)
                        for move in permutations(cardset, i + 1)
                    ]
                    legal_moves += cardsets

                cardset = list(
                    filter(
                        lambda card: card.cvalue == self.top_card.cvalue,
                        self.current_player.hand,
                    )
                )

        same_val = list(
            filter(
                lambda card: card.cvalue == self.top_card.cvalue,
                self.current_player.hand,
            )
        )

        for i in range(len(same_val)):
            legal_moves += [list(move) for move in permutations(same_val, i + 1)]

        self.legal_moves = legal_moves

    def deal(self):
        for player in self.players:
            self.draw_n(player, self.crazy)
        self.discard.append(self.deck.pop())
        self.top_card = self.discard[-1]

    def draw_n(self, player: Player, num_cards: int):
        for _ in range(num_cards):
            if len(self.deck) == 0:
                if len(self.discard) > 1:
                    new_discard = self.discard.pop()
                    self.deck = self.discard
                    self.discard = [new_discard]
                else:
                    return

            player.hand.append(self.deck.pop())
        player.hand.sort(key=lambda card: card.cvalue)

    def resolve_move(self, move: list[Card] | None):
        if move is None:
            self.draw_n(self.current_player, 1)
        else:
            self.play_cards(move)
        self.advance_turn()

    def play_cards(self, cards: list[Card]):
        for card in cards:
            self.current_player.hand.remove(card)
        self.discard += cards
        self.top_card = self.discard[-1]
        if len(self.current_player.hand) == 0:
            self.reduce_crazy()

        if cards[0].cvalue == CardValue.TWO:
            self.two_effect()
        else:
            self.draw_two_mult = 1

        if cards[0].cvalue == CardValue.JACK:
            self.advance_turn()

        for card in cards:
            if card.cvalue == CardValue.QUEEN and card.suit == Suit.SPADES:
                self.draw_n(self.next_player(), 5)

    def next_player(self):
        player_idx = self.players.index(self.current_player)

        next_player_idx = player_idx + 1
        if next_player_idx >= len(self.players):
            next_player_idx = 0
        return self.players[next_player_idx]

    def advance_turn(self):
        self.current_player = self.next_player()

    def reduce_crazy(self):
        if self.current_player.crazy == CardValue.ACE:
            self.winner = self.players.index(self.current_player)
            return

        self.current_player.crazy -= 1

        self.draw_n(self.current_player, self.current_player.crazy)

    def two_effect(self):
        self.draw_n(self.next_player(), 2 * self.draw_two_mult)
        self.draw_two_mult += 1

    def print_game_state(self):
        print("===== GAME STATE =====")
        for i, player in enumerate(self.players):
            print(f"Player {i}: Crazy {player.crazy}")
            hand_str = ""
            for card in player.hand:
                hand_str += f"{card.cvalue.name} of {card.suit.name}, "
            print(hand_str)
            print()
        print(f"Deck size: {len(self.deck)}")
        print(f"Discard size: {len(self.discard)}")
        print(
            f"Discard top card: {self.top_card.cvalue.name} of {self.top_card.suit.name}"
        )

    def print_legal_moves(self):
        print("====== LEGAL MOVES =====")
        print(f"Current player: {self.players.index(self.current_player)}")
        for move in self.legal_moves:
            move_str = ""
            for card in move:
                move_str += f"{card.cvalue.name} of {card.suit.name}, "
            print(move_str)


def setup_deck() -> list[Card]:
    suits = [suit for suit in Suit]
    nums = [n for n in CardValue]
    deck: list[Card] = [
        Card(card_data[0], card_data[1]) for card_data in product(suits, nums)
    ]
    shuffle(deck)
    return deck
