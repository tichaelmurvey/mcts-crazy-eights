from itertools import permutations, product
from random import shuffle

from c8_env.types import Card, CardValue, Player, Suit


class CrazyEightGame:
    players: list[Player]
    deck: list[Card]
    discard: list[Card]
    current_player: Player
    draw_two_mult: int
    winner: int | None
    legal_moves: list[list[Card]]

    def __init__(self, n_players: int = 2) -> None:
        self.players = [Player(hand=[], crazy=8) for _ in range(n_players)]
        self.current_player = self.players[0]
        self.deck = setup_deck()
        self.discard = []
        self.draw_two_mult = 1
        self.winner = None
        self.legal_moves = []

    def get_legal_moves(self):
        playable = self.discard[-1]
        legal_moves: list[list[Card]] = []
        for active_card in self.current_player.hand:
            if (
                active_card.suit is playable.suit
                or active_card.cvalue is self.current_player.crazy
            ):
                legal_moves.append([active_card])
                cardset = list(
                    filter(
                        lambda card: card.cvalue is active_card.cvalue
                        and card is not active_card,
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
                        lambda card: card.cvalue is playable.cvalue,
                        self.current_player.hand,
                    )
                )

        same_val = list(
            filter(
                lambda card: card.cvalue is playable.cvalue,
                self.current_player.hand,
            )
        )

        for i in range(len(same_val)):
            legal_moves += [list(move) for move in permutations(same_val, i + 1)]

        self.legal_moves = legal_moves

    def deal(self):
        for player in self.players:
            self.draw_n(player, 8)
        self.discard.append(self.deck.pop())

    def draw_n(self, player: Player, num_cards: int):
        draw = self.deck[-num_cards:]
        del self.deck[-num_cards:]
        player.hand += draw
        player.hand.sort(key=lambda card: card.cvalue)

    def play_card(self, cards_idx: list[int]):
        cards_to_play: list[Card] = []
        for idx in cards_idx:
            cards_to_play.append(self.current_player.hand.pop(idx))
        self.discard += cards_to_play

        if len(self.current_player.hand) is 0:
            self.reduce_crazy()

        if cards_to_play[0].cvalue == CardValue.TWO:
            self.two_effect()

        if cards_to_play[0].cvalue == CardValue.JACK:
            self.advance_turn()

        for card in cards_to_play:
            if card.cvalue == CardValue.QUEEN and card.suit == Suit.SPADES:
                self.draw_n(self.next_player(), 5)

        self.advance_turn()

    def next_player(self):
        player_idx = self.players.index(self.current_player)

        next_player_idx = player_idx + 1
        if next_player_idx >= len(self.players):
            next_player_idx = 0
        return self.players[player_idx]

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
            for card in player.hand:
                print(f"    {card.cvalue.name} of {card.suit.name}")
            print()
        discard = self.discard[-1]
        print(f"Discard top card: {discard.cvalue.name} of {discard.suit.name}")

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
