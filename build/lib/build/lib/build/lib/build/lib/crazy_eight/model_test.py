from __future__ import annotations
from collections import Counter
from copy import deepcopy
import math
import random
import statistics
from time import time
from typing import TYPE_CHECKING
from crazy_eight.card import Card, format_move
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.mcts_model import MCTS
from crazy_eight.random_models import (
    AlwaysDrawPlayer,
    PlayBiasRandomPlayer,
    RandomPlayer,
)
from tqdm import tqdm

from crazy_eight.types import CardValue, Suit

if TYPE_CHECKING:
    from crazy_eight.types import Model

ITERATIONS = 120
DEBUG = False


def debug_print(*args):
    if DEBUG:
        print(args)


def bulk_test_models(
    evaluator1: Model,
    evaluator2: Model = RandomPlayer(),
    tests: int = 100,
    verbose=True,
):
    if verbose:
        print("Crazy Eight Model Test")
        print(f"Tests: {tests}")
        print(f"P1: {evaluator1.__class__.__name__}")
        print(f"P2: {evaluator2.__class__.__name__}")
    evaluators: list[Model] = [evaluator1, evaluator2]
    wincounts = [0, 0]

    for i in tqdm(range(tests)):
        outcome = test_model(evaluator1, evaluator2, verbose=True)
        wincounts[outcome] += 1

    print("=== Tests complete! ===")
    print(
        f"P1 {evaluator1.__class__.__name__} wins: {wincounts[0]} win%: {wincounts[0]/tests}"
    )
    print(
        f"P2 {evaluator2.__class__.__name__} wins: {wincounts[1]} win%: {wincounts[1]/tests}"
    )


def test_model(
    evaluator1: Model, evaluator2: Model = RandomPlayer(), verbose=True, crazy=4
):
    real_game = CrazyEightGame(crazy=crazy)
    real_game.deal()
    models: list[Model] = [evaluator1, evaluator2]
    start_time = time()
    if verbose:
        print()
        print("Crazy Eight Model Test")
        print(f"P1: {evaluator1.__class__.__name__}")
        print(f"P2: {evaluator2.__class__.__name__}")
    turn = 1
    while real_game.winner is None:
        if verbose:
            print(
                f"Turn: {turn}, P1crazy, hand: {real_game.players[0].crazy} {len(real_game.players[0].hand)}, P2crazy, hand: {real_game.players[1].crazy} {len(real_game.players[1].hand)}",
                end="\r",
            )
            turn = turn + 1
        move = models[real_game.current_player.idx].choose_move(real_game)
        real_game.resolve_move(move)

    if verbose:
        print(real_game.print_game_state())
        print(
            f"Game is over! Winner: P{real_game.winner + 1} {models[real_game.winner].__class__.__name__} Turns: {real_game.turn_count}"
        )
        print(f"Test took: {time() - start_time} seconds")
        print()
    return real_game.winner


def test_action():
    random.seed(10)
    real_game = CrazyEightGame(crazy=4)
    real_game.deal()
    real_game.print_game_state()
    results = []
    model = MCTS(
        RandomPlayer(),
        iterations=math.inf,
        max_time=1,
        verbose=True,
    )
    for i in range(1):
        random.seed(i)
        game_clone = deepcopy(real_game)
        option_strs = " | ".join([format_move(move) for move in game_clone.legal_moves])
        print()
        print("From moves: ", option_strs)
        move = model.choose_move(game_clone)
        results.append(format_move(move))
    totals = Counter(results)
    print(totals)


def make_easy_game():
    easy_game = CrazyEightGame(crazy=1)
    easy_game.top_card = Card(Suit.CLUBS, CardValue.FIVE)
    easy_game.discard = [Card(Suit.CLUBS, CardValue.FIVE)]
    easy_game.players[0].hand = [
        Card(Suit.CLUBS, CardValue.THREE),
    ]
    easy_game.players[1].hand = [
        Card(Suit.DIAMONDS, CardValue.THREE),
        Card(Suit.SPADES, CardValue.FOUR),
        Card(Suit.HEARTS, CardValue.QUEEN),
    ]
    easy_game.current_player = easy_game.players[0]
    return easy_game


def make_medium_game():
    easy_game = CrazyEightGame(crazy=3)
    easy_game.top_card = Card(Suit.SPADES, CardValue.FIVE)
    easy_game.discard = [Card(Suit.SPADES, CardValue.FIVE)]
    easy_game.players[0].hand = [
        Card(Suit.SPADES, CardValue.SEVEN),
    ]
    easy_game.players[1].hand = [
        Card(Suit.DIAMONDS, CardValue.THREE),
        Card(Suit.SPADES, CardValue.FOUR),
        Card(Suit.HEARTS, CardValue.QUEEN),
    ]
    easy_game.current_player = easy_game.players[0]
    return easy_game


def make_tricky_game():
    easy_game = CrazyEightGame(crazy=3)
    easy_game.top_card = Card(Suit.SPADES, CardValue.FIVE)
    easy_game.discard = [Card(Suit.SPADES, CardValue.FIVE)]
    easy_game.players[0].hand = [
        Card(Suit.SPADES, CardValue.SEVEN),
        Card(Suit.SPADES, CardValue.QUEEN),
        Card(Suit.HEARTS, CardValue.SEVEN),
        Card(Suit.SPADES, CardValue.FOUR),
    ]
    easy_game.players[1].hand = [
        Card(Suit.DIAMONDS, CardValue.THREE),
        Card(Suit.SPADES, CardValue.FOUR),
        Card(Suit.HEARTS, CardValue.QUEEN),
        Card(Suit.HEARTS, CardValue.ACE),
    ]
    easy_game.current_player = easy_game.players[0]
    return easy_game


def test_known_move(model: MCTS):
    results = []
    ends = []
    iterations = []
    for i in tqdm(range(20)):
        game = make_tricky_game()
        bestnode, iters = model.choose_node(game)
        results.append(format_move(bestnode.action))  # type: ignore
        ends.append(bestnode.game_ends_reached)
        iterations.append(iters)
    totals = Counter(results)
    print(totals)
    print(Counter(ends))
    print(f"avg iterations: {statistics.fmean(iterations)}")


def compare_movers():
    model1 = MCTS(
        rollout_mover=RandomPlayer(), max_time=0.2, rollout_limit=50, verbose=False
    )

    model2 = MCTS(
        rollout_mover=PlayBiasRandomPlayer(),
        max_time=0.2,
        rollout_limit=50,
        verbose=False,
    )
    print()
    print("TEST")
    test_known_move(model1)
    test_known_move(model2)


bulk_test_models(
    MCTS(
        rollout_mover=PlayBiasRandomPlayer(),
        max_time=0.2,
        rollout_limit=50,
        verbose=False,
    ),
    MCTS(rollout_mover=RandomPlayer(), max_time=0.2, rollout_limit=50, verbose=False),
    tests=20,
)

# test_model(
#     MCTS(
#         rollout_mover=PlayBiasRandomPlayer(),
#         max_time=0.2,
#         rollout_limit=50,
#         verbose=True,
#     ),
#     PlayBiasRandomPlayer(),
# )
