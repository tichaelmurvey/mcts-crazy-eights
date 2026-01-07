from __future__ import annotations
from copy import deepcopy
import math
import random
import time
from typing import TYPE_CHECKING
from crazy_eight.card import format_move
from crazy_eight.evaluate_state import evaluate_state
from crazy_eight.random_models import RandomPlayer
from crazy_eight.types import Model, Move, Player

if TYPE_CHECKING:
    from crazy_eight.game_env import CrazyEightGame


EXPLORE_PARAM = 1.41
DEBUG = False


def debug_print(*args):
    if DEBUG:
        print(args)


class MCTS(Model):
    rollout_mover: Model

    def __init__(
        self,
        rollout_mover: Model = RandomPlayer(),
        rollout_evaluator=evaluate_state,
        iterations=500.0,
        max_time: None | float = None,
        verbose=False,
        rollout_limit: int = 200,
    ):
        self.rollout_mover = rollout_mover
        self.rollout_evaluator = rollout_evaluator
        self.iterations = iterations
        self.max_time = max_time
        self.rollout_limit = rollout_limit
        self.verbose = verbose

    def choose_move(self, game: CrazyEightGame):
        best_option, i = self.choose_node(game)
        if best_option.action is None:
            raise Exception("Returned best node choice with no action")
        return best_option.action

    def choose_node(self, game: CrazyEightGame):
        root_node = MCTSNode(
            deepcopy(game), game.current_player, rollout_limit=self.rollout_limit
        )
        start_time = time.time()

        i = 0
        while i < self.iterations:

            root_node.select()

            if self.max_time and time.time() - start_time > self.max_time:
                break

            i += 1

        debug_print("iterations done")

        if self.verbose:
            print()
            print()
            print(f"Completed {i} iterations in {time.time() - start_time} seconds")
            print("Move evaluation summary")
            for child in root_node.children:
                if child.action is None:
                    print("Chose root node I guess?")
                else:
                    print(
                        f"Move: {format_move(child.action)}, Visits: {child.visits}, Wins: {child.wins}, winrate: {child.wins/child.visits}, max search depth: {child.max_depth}, ends reached: {child.game_ends_reached} action_player: {child.action_player} winner: {child.game.winner}"
                    )

        best_option = max(root_node.children, key=lambda c: c.visits)
        if self.verbose:
            print(f"Chose move: {format_move(best_option.action)}")  # type: ignore

        return best_option, i


class MCTSNode:
    parent: MCTSNode | None
    game: CrazyEightGame
    children: list[MCTSNode]
    action_player: int
    action: Move | None
    rollout_limit: int

    def __init__(
        self,
        game: CrazyEightGame,
        player: Player,
        parent=None,
        action: Move | None = None,
        rollout_mover=RandomPlayer(),
        rollout_limit: int = 200,
        evaluator=evaluate_state,
    ) -> None:
        self.game = game
        self.parent = parent
        self.action = action
        self.action_player = player.idx
        self.visits = 0
        self.wins = 0
        game.get_legal_moves()
        self.untried_actions = game.legal_moves
        self.children = []
        self.max_depth = 0
        self.game_ends_reached = 0
        self.rollout_mover = rollout_mover
        self.rollout_limit = rollout_limit
        self.evaluator = evaluator

    def best_child(self):
        for child in self.children:
            if child.visits == 0:
                return child
        log_visits = math.log(self.visits)

        def ucb(child):
            return child.wins / child.visits + EXPLORE_PARAM * math.sqrt(
                log_visits / child.visits
            )

        return max(self.children, key=ucb)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def select(self):
        if self.game.winner is not None:
            winval = 1.0 if self.game.winner == 0 else -1.0
            self.backprop(winner=winval, depth=0)
            return

        if not self.is_fully_expanded():
            self.expand()
            return

        self.best_child().select()

    def expand(self):
        if self.game.winner is not None:
            raise Exception("Attempted to expand node with winner")
        random.shuffle(self.untried_actions)
        action = self.untried_actions.pop()
        child_game = deepcopy(self.game)
        action_player = child_game.current_player
        child_game.resolve_move(action)
        new_child = MCTSNode(
            child_game,
            parent=self,
            action=action,
            player=action_player,
            rollout_limit=self.rollout_limit,
        )
        self.children.append(new_child)
        new_child.rollout()

    def rollout(self):
        rolled_game = deepcopy(self.game)
        rollout_turns = 0
        while True:
            if rolled_game.winner is not None:
                winval = 1.0 if rolled_game.winner == 0 else -1.0
                self.backprop(winner=winval, depth=0)
                return

            if rollout_turns > self.rollout_limit:
                self.backprop(self.evaluator(rolled_game))
                return

            rolled_game.get_legal_moves()
            move = self.rollout_mover.choose_move(rolled_game)
            rolled_game.resolve_move(move)
            rollout_turns += 1

    def backprop(self, winner: float, depth: int = 0):
        self.visits += 1
        self.max_depth = max(depth, self.max_depth)
        if winner == 1.0 or winner == -1.0:
            self.game_ends_reached += 1

        if self.action_player == 0:
            self.wins += winner
        else:
            self.wins -= winner

        if self.parent:
            self.parent.backprop(winner, depth + 1)
