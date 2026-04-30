from bot import Bot
from game_actions import GameActions
from game_controller import GameController
from player import Player

class SevenuxUI:
    game_controller: GameController = None

    def __init__(self):
        self.game_controller = GameController(self)

        player_name: str = input('Player name : ')
        player: Player = Player(player_name)

        self.game_controller.game.set_player(player)
        self.game_controller.game.add_bot(Bot('Cyprien'))
        self.game_controller.game.add_bot(Bot('Nikola'))
        self.game_controller.game.add_bot(Bot('Rahim'))
        self.game_controller.game.add_bot(Bot('Benazir'))

    def start(self):
        while not self.game_controller.game.deck.is_empty():
            self.game_controller.execute_action(GameActions.NEXT_TURN)

    def decide_draw(self) -> bool:
        choice: str = input('Piocher ? y/n')
        return choice == 'y'

    def decide_stop(self, bots: list[Bot]) -> Bot:
        choice: int = int(input(
            "Stopper qui ?\n" +
            "\n".join(f"{i} {p}" for i, p in enumerate(bots))
        ))
        return bots[choice]

    def decide_draw3(self, bots: list[Bot]) -> Bot|bool:
        choice: str = input('Piocher 3 cartes ? y/n')
        if choice == 'y':
            return True
        else:
            choice: int = int(input(
                "Donner à qui ?\n" +
                "\n".join(f"{i} {p}" for i, p in enumerate(bots))
            ))
            return bots[choice]

    def decide_second_chance(self, bots: list[Bot]) -> Bot:
        choice: int = int(input(
            "Qui prend le second chance ?\n" +
            "\n".join(f"{i} {p}" for i, p in enumerate(bots))
        ))
        return bots[choice]