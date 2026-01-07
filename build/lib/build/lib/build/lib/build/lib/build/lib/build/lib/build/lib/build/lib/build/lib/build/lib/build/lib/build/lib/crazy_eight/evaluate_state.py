from crazy_eight.game_env import CrazyEightGame

CRAZY_WEIGHT = 3
HAND_WEIGHT = 1


def evaluate_state(game: CrazyEightGame) -> float:
    player = game.players[0]
    opp = game.players[1]
    if len(opp.hand) == 0 or len(player.hand) == 0:
        game.print_game_state()
        raise Exception("Somehow evaluate_state got weird gamestate.")
    crazy_diff = (opp.crazy - player.crazy) / game.crazy
    # hand_diff = 1 / len(player.hand) - 1 / len(opp.hand)
    hand_diff = min(max(len(opp.hand) - len(player.hand), -5), 5) / 5

    score = (crazy_diff * CRAZY_WEIGHT + hand_diff * HAND_WEIGHT) / (
        CRAZY_WEIGHT + HAND_WEIGHT
    )
    if score > 1.0 or score < -1.0:
        raise Exception("Error: Evaluate state out of bounds", score)
    return score
