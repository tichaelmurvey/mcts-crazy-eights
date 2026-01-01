from __future__ import annotations
from collections import Counter
from copy import deepcopy
import math
import os
import random
from crazy_eight.card import format_move
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.mcts_model import mcts_search, mcts_search_wrapper
from crazy_eight.random_models import random_move, random_move_play_card_bias
from crazy_eight.types import Card, Model
from tqdm import tqdm

ITERATIONS = 120
DEBUG = False


def debug_print(*args):
    if DEBUG:
        print(args)


def bulk_test_models(
    evaluator1: Model, evaluator2: Model = random_move, tests: int = 100, verbose=True
):
    if verbose:
        print("Crazy Eight Model Test")
        print(f"Tests: {tests}")
        print(f"P1: {evaluator1.__name__}")
        print(f"P2: {evaluator2.__name__}")
    evaluators: list[Model] = [evaluator1, evaluator2]
    wincounts = [0, 0]

    for i in tqdm(range(tests)):
        outcome = test_model(evaluator1, evaluator2, verbose=False)
        wincounts[outcome] += 1

    print("=== Tests complete! ===")
    print(f"P1 {evaluator1.__name__} wins: {wincounts[0]} win%: {wincounts[0]/tests}")
    print(f"P2 {evaluator2.__name__} wins: {wincounts[1]} win%: {wincounts[1]/tests}")


def test_model(
    evaluator1: Model, evaluator2: Model = random_move, verbose=True, crazy=4
):
    real_game = CrazyEightGame(crazy=crazy)
    real_game.deal()
    evaluators: list[Model] = [evaluator1, evaluator2]
    if verbose:
        print()
        print("Crazy Eight Model Test")
        print(f"P1: {evaluator1.__name__}")
        print(f"P2: {evaluator2.__name__}")
    turn = 1
    while real_game.winner is None:
        if verbose:
            print(
                turn, real_game.players[0].crazy, real_game.players[1].crazy, end="\r"
            )
            turn = turn + 1
        move = evaluators[real_game.current_player.idx](real_game, ITERATIONS)
        real_game.resolve_move(move)

    if verbose:
        print(
            f"Game is over! Winner: P{real_game.winner + 1} {evaluators[real_game.winner].__name__} Turns: {real_game.turn_count}"
        )
        print()
    return real_game.winner


def test_action():
    random.seed(10)
    real_game = CrazyEightGame(crazy=4)
    real_game.deal()
    real_game.print_game_state()
    results = []
    for i in range(1):
        random.seed(i)
        game_clone = deepcopy(real_game)
        option_strs = " | ".join([format_move(move) for move in game_clone.legal_moves])
        print()
        print("From moves: ", option_strs)
        move = mcts_search(
            game_clone,
            random_move,
            iterations=math.inf,
            max_time=1,
            verbose=True,
        )
        results.append(format_move(move))
    totals = Counter(results)
    print(totals)


# test_action()
# test_model(random_move)

# test_model(random_move_play_card_bias)

# print("MCTS with random move rollouts VS random player")
# test_model(mcts_search_wrapper(random_move), random_move)

# print("mcts with play card bias in rollout VS random play card bias")
# test_model(mcts_search_wrapper(random_move_play_card_bias), random_move_play_card_bias)

# print("mcts with play card bias in rollout VS random player")
# test_model(mcts_search_wrapper(random_move_play_card_bias), random_move)

# print("mcts with random move rollout VS play card bias")
# test_model(mcts_search_wrapper(random_move), random_move_play_card_bias)

# print("Random vs Random")
# bulk_test_models(random_move, tests=1000)

# print("Random w/ Play Card Bias vs Random")
# bulk_test_models(random_move_play_card_bias, tests=1000)

# bulk_test_models(mcts_search)
bulk_test_models(
    mcts_search_wrapper(rollout_mover=random_move),
    mcts_search_wrapper(rollout_mover=random_move_play_card_bias),
    10,
)
