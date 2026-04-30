from game import Game
from game_actions import GameActions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sevenuxui import SevenuxUI

class GameController:
    ui: SevenuxUI = None
    game: Game = None

    def __init__(self, ui: SevenuxUI):
        self.ui = ui
        self.game = Game()
        self.game.set_game_controller(self)

    def ui_action(self, action: str):
        if action == GameActions.DECIDE_DRAW:
            return self.ui.decide_draw()
        elif action == GameActions.DECIDE_STOP:
            return self.ui.decide_stop(self.game.bots_to_choose)
        elif action == GameActions.DECIDE_DRAW3:
            return self.ui.decide_draw3(self.game.bots_to_choose)
        elif action == GameActions.DECIDE_SECONDCHANCE:
            return self.ui.decide_second_chance(self.game.bots_to_choose)

        return None

    def execute_action(self, action: str):
        if action == GameActions.NEXT_TURN:
            self.game.next_turn()