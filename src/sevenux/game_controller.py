from sevenux.game import Game
from sevenux.game_actions import GameActions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sevenux.sevenuxui import SevenuxUI

class GameController:
    ui: SevenuxUI = None
    game: Game = None

    def __init__(self, ui: SevenuxUI):
        self.ui = ui
        self.game = Game()
        self.game.set_game_controller(self)

    def ui_action(self, action: str, data: any = None) -> any:
        if action == GameActions.DECIDE_DRAW:
            return self.ui.decide_draw()
        elif action == GameActions.DECIDE_STOP:
            return self.ui.decide_stop(self.game.bots_to_choose)
        elif action == GameActions.DECIDE_DRAW3:
            return self.ui.decide_draw3(self.game.bots_to_choose)
        elif action == GameActions.DECIDE_SECONDCHANCE:
            return self.ui.decide_second_chance(self.game.bots_to_choose)
        elif action == GameActions.PRINT_MESSAGE:
            return self.ui.print_message(data)

        return None

    def execute_action(self, action: str):
        if action == GameActions.NEXT_TURN:
            return self.game.next_turn()
        elif action == GameActions.COUNT_SCORES:
            self.game.count_scores()