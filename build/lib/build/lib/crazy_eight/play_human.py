import random
from crazy_eight.card import format_card, format_move
from crazy_eight.game_env import CrazyEightGame
from crazy_eight.types import Card, Move


def print_game_state(game: CrazyEightGame, human_player_idx: int):
    """Print the current game state from human player's perspective."""
    print("\n" + "=" * 50)

    # Show opponent info
    for i, player in enumerate(game.players):
        if i != human_player_idx:
            print(
                f"Computer (Player {i}): {len(player.hand)} cards, {player.crazy} is wild"
            )

    # Show discard pile top
    top_card = game.discard[-1]
    print(f"\nDiscard pile top: {format_card(top_card)}")
    print(f"Deck: {len(game.deck)} cards remaining")

    # Show human hand
    human = game.players[human_player_idx]
    print(f"\nYour hand ({human.crazy} is wild):")
    hand_str = "  "
    for i, card in enumerate(human.hand):
        hand_str += f"{format_card(card)}, "
        if (i + 1) % 6 == 0:
            hand_str += "\n  "
    print(hand_str)
    print("=" * 50)


def get_human_move(game: CrazyEightGame) -> Move:
    """Get move input from human player."""
    if not game.legal_moves:
        print("No legal moves available. You must draw a card.")
        input("Press Enter to draw...")
        return "draw"

    print("\nLegal moves:")
    for i, move in enumerate(game.legal_moves):
        print(f"  [{i}] {format_move(move)}")
    print(f"  [d] Draw a card")

    while True:
        choice = input("\nYour choice: ").strip().lower()

        if choice == "d":
            return "draw"

        try:
            idx = int(choice)
            if 0 <= idx < len(game.legal_moves):
                return game.legal_moves[idx]
            else:
                print(
                    f"Invalid choice. Enter 0-{len(game.legal_moves)-1} or 'd' to draw."
                )
        except ValueError:
            print("Invalid input. Enter a number or 'd' to draw.")


def get_computer_move(game: CrazyEightGame) -> Move:
    """Get a random move for the computer player."""
    if not game.legal_moves:
        raise Exception("Error: No legal moves found")
    return random.choice(game.legal_moves)


def play_game(human_player_idx: int = 0):
    """Play a game of Crazy Eights against the computer."""
    game = CrazyEightGame(n_players=2)
    game.deal()

    print("\n" + "=" * 50)
    print("   CRAZY EIGHTS - Human vs Computer")
    print("=" * 50)
    print("\nRules:")
    print("- Match the suit or value of the top discard card")
    print("- 8s are wild (can be played on anything)")
    print("- 2s make the next player draw 2 cards")
    print("- Jacks skip the next player's turn")
    print("- Queen of Spades makes next player draw 5 cards")
    print("- Empty your hand to reduce your 'crazy' number")
    print("- First to play all cards when crazy=1 (Ace) wins!")

    while game.winner is None:
        current_idx = game.players.index(game.current_player)
        game.get_legal_moves()

        if current_idx == human_player_idx:
            # Human turn
            print_game_state(game, human_player_idx)
            print("\n>>> YOUR TURN <<<")
            move = get_human_move(game)
            if move:
                print(f"You played: {format_move(move)}")
            else:
                print("You draw a card.")
        else:
            # Computer turn
            print(f"\n>>> COMPUTER'S TURN <<<")
            move = get_computer_move(game)
            if move:
                print(f"Computer plays: {format_move(move)}")
            else:
                print("Computer draws a card.")

        game.resolve_move(move)

    # Game over
    print("\n" + "=" * 50)
    if game.winner == human_player_idx:
        print("   CONGRATULATIONS! YOU WIN!")
    else:
        print("   GAME OVER - Computer wins!")
    print("=" * 50 + "\n")


def main():
    """Main entry point."""
    print("\nWelcome to Crazy Eights!")

    while True:
        play_game()

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
