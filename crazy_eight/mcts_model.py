from __future__ import annotations
from copy import deepcopy
import math
import random
import time
from crazy_eight.card import format_move
from crazy_eight.evaluate_state import evaluate_state
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.random_models import random_move
from crazy_eight.types import Card, Move, Player

EXPLORE_PARAM = 1.41
DEBUG = False
ROLLOUT_TURN_LIMIT = 100


def debug_print(*args):
    if DEBUG:
        print(args)


def mcts_search_wrapper(
    rollout_mover=random_move,
    rollout_evaluator=evaluate_state,
):
    return lambda root_game, iterations: mcts_search(
        root_game, iterations, rollout_mover, rollout_evaluator
    )


def mcts_search(
    root_game: CrazyEightGame,
    rollout_mover=random_move,
    rollout_evaluator=evaluate_state,
    iterations=500.0,
    max_time: None | float = None,
    verbose=False,
):
    root_node = MCTSNode(root_game, root_game.current_player)
    start_time = time.time()

    i = 0
    while i < iterations:

        leaf = root_node.select()
        winner = leaf.rollout(rollout_mover, rollout_evaluator)
        leaf.backprop(winner)

        if max_time and time.time() - start_time > max_time:
            break

        i += 1

    debug_print("iterations done")

    if verbose:
        print()
        print(f"Completed {i} iterations in {time.time() - start_time} seconds")
        print("Move evaluation summary")
        for child in root_node.children:
            if child.action is None:
                print("Chose root node I guess?")
            else:
                print(
                    f"Move: {format_move(child.action)}, Visits: {child.visits}, Wins: {child.wins}, winrate: {child.wins/child.visits}, max search depth: {child.max_depth}, ends reached: {child.game_ends_reached}"
                )

    best_option = max(root_node.children, key=lambda c: c.visits)
    debug_print("got best option", best_option.action)
    if best_option.action is None:
        raise Exception("Returned best node choice with no action")

    return best_option.action


class MCTSNode:
    parent: MCTSNode | None
    game: CrazyEightGame
    children: list[MCTSNode]
    action_player: Player
    action: Move | None

    def __init__(
        self,
        game: CrazyEightGame,
        player: Player,
        parent=None,
        action: Move | None = None,
    ) -> None:
        self.game = deepcopy(game)
        self.parent = parent
        self.action = action
        self.action_player = player
        self.visits = 0
        self.wins = 0
        game.get_legal_moves()
        self.untried_actions = game.legal_moves
        self.children = []
        self.max_depth = 0
        self.game_ends_reached = 0

    def best_child(self):
        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child):
            return child.wins / child.visits + EXPLORE_PARAM * math.sqrt(
                math.log(self.visits) / child.visits
            )

        return max(self.children, key=ucb)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def select(self) -> MCTSNode:
        if self.game.winner is not None:
            return self

        if not self.is_fully_expanded():
            return self.expand()

        return self.best_child().select()

    def expand(self) -> MCTSNode:
        if self.game.winner is not None:
            raise Exception("Attempted to expand node with winner")

        action = random.choice(self.untried_actions)
        self.untried_actions.remove(action)
        child_game = deepcopy(self.game)
        action_player = child_game.current_player
        child_game.resolve_move(action)
        new_child = MCTSNode(
            child_game, parent=self, action=action, player=action_player
        )
        self.children.append(new_child)
        return new_child

    def rollout(self, mover=random_move, evaluator=evaluate_state) -> float:
        rolled_game = deepcopy(self.game)
        rollout_turns = 0
        while True:
            if rolled_game.winner is not None:
                return 1 if rolled_game.winner == 0 else -1
            if rollout_turns > ROLLOUT_TURN_LIMIT:
                return evaluator(rolled_game)
            rolled_game.get_legal_moves()
            move = mover(rolled_game)
            rolled_game.resolve_move(move)
            rollout_turns += 1

    def backprop(self, winner: float, depth: int = 0):
        self.visits += 1
        self.game_ends_reached
        self.max_depth = max(depth, self.max_depth)

        if winner == 1.0 or winner == -1.0:
            self.game_ends_reached += 1

        if self.action_player.idx == 0:
            self.wins += winner
        else:
            self.wins -= winner

        if self.parent:
            self.parent.backprop(winner, depth + 1)
