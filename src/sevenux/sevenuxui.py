import time

from readchar import readkey

from sevenux.bot import Bot
from sevenux.game_actions import GameActions
from sevenux.game_controller import GameController
from sevenux.player import Player

class SevenuxUI:
    game_controller: GameController = None

    def __init__(self):
        self.game_controller = GameController(self)

        player: Player = Player('François')

        self.game_controller.game.set_player(player)
        self.game_controller.game.add_bot(Bot('Cyprien'))
        self.game_controller.game.add_bot(Bot('Nikola'))
        self.game_controller.game.add_bot(Bot('Rahim'))
        self.game_controller.game.add_bot(Bot('Benazir'))

    def start(self):
        while not self.game_controller.game.deck.is_empty() and len(self.game_controller.game.players_in_game) > 0:
            played: bool = self.game_controller.execute_action(GameActions.NEXT_TURN)
            if not played:
                continue

            self.show()

            time.sleep(1)

        self.game_controller.execute_action(GameActions.COUNT_SCORES)
        self.show_scores()

    def decide_draw(self) -> bool:
        self.print_message('Piocher ? y/n')
        return readkey() == 'y'

    def decide_stop(self, bots: list[Bot]) -> Bot:
        self.print_message('Stopper qui ?')
        self.print_message('\n'.join(f"{i} {p.name}" for i, p in enumerate(bots)))
        
        choice: int = int(readkey())
        return bots[choice]

    def decide_draw3(self, bots: list[Bot]) -> Bot|bool:
        self.print_message('Piocher 3 cartes ? y/n')

        choice: str = readkey()

        if choice == 'y':
            return True
        else:
            self.print_message("Donner à qui ?")
            self.print_message('\n'.join(f"{i} {p.name}" for i, p in enumerate(bots)))
            
            choice: int = int(readkey())
            return bots[choice]

    def decide_second_chance(self, bots: list[Bot]) -> Bot:
        self.print_message('Qui prend le second chance ?')
        self.print_message('\n'.join(f"{i} {p.name}" for i, p in enumerate(bots)))

        choice: int = int(readkey())
        return bots[choice]

    def show(self):
        players: list[str] = []

        for player in self.game_controller.game.players:
            cards = ' '.join(card.value for card in (*player.cards, *player.jokers))
            badges = ' '.join(
                icon
                for icon, enabled in (
                    ('󰑓 ', player.has_second_chance()),
                    ('⏩', player.has_x2()),
                    (' ', player.is_stopped),
                )
                if enabled
            )
            players.append(f"[{' '.join(part for part in (player.name, cards, badges) if part)}]")

        self.print_message(' '.join(players) + '\n')

    def show_scores(self):
        text: str = 'Scores :\n'
        for player in self.game_controller.game.players:
            text += f"{player.name} : {player.total_points}\n"

        self.print_message(text)

    def print_message(self, message: str):
        print(message)