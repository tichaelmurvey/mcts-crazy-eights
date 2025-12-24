from random import choice
from crazy_eight.game_env import CrazyEightGame


game = CrazyEightGame(crazy=3)
game.deal()

while game.winner is None:
    game.print_game_state()
    game.get_legal_moves()
    game.print_legal_moves()
    move = choice(game.legal_moves) if len(game.legal_moves) > 0 else None
    game.resolve_move(move)
print(f"Game ended! Player {game.winner} wins")
