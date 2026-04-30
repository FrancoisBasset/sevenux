from bot import Bot
from card import Card
from deck import Deck
from game_actions import GameActions
from player import Player

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_controller import GameController

class Game:
    deck: Deck = None
    player: Player = None
    bots: list[Bot] = []
    turn: int = 0
    game_controller: GameController = None

    def __init__(self):
        self.deck = Deck()

    def set_player(self, player: Player):
        self.player = player

    def add_bot(self, bot: Bot):
        self.bots.append(bot)

    def set_game_controller(self, game_controller: GameController):
        self.game_controller = game_controller

    @property
    def players(self) -> list[Player|Bot]:
        return [self.player, *self.bots]

    @property
    def bots_to_choose(self) -> list[Bot]:
        return [bot for bot in self.bots if not bot.is_stopped]

    def get_current_player(self) -> Player|Bot:
        self.turn = (self.turn + 1) % len(self.players)
        return self.players[self.turn]

    def next_turn(self) -> bool:
        player: Player|Bot = self.get_current_player()

        if player.is_stopped:
            return True

        draw: bool = self._decide_draw(player)
        if not draw:
            player.stop()
            return True

        return self.draw_card(player)

    def draw_card(self, player: Player):
        card: Card = self.deck.draw_card()

        if card.is_stop():
            self._decide_stop(player)
        elif card.is_draw3():
            self._decide_draw3(player)
        elif card.is_second_chance():
            self._decide_second_chance(player)
        else:
            player.draw_card(card)

        return not self.deck.is_empty()

    def _decide_draw(self, player: Player|Bot) -> bool:
        if isinstance(player, Player):
            return self.game_controller.ui_action(GameActions.DECIDE_DRAW)
        else:
            return player.decide_draw()

    def _decide_stop(self, player: Player|Bot):
        if isinstance(player, Player):
            if len(self.bots_to_choose) == 0:
                player.stop()
            elif len(self.bots_to_choose) == 1:
                self.bots_to_choose[0].stop()
            else:
                target: Player = self.game_controller.ui_action(GameActions.DECIDE_STOP)
                target.stop()
        else:
            self.player.stop()

    def _decide_draw3(self, player: Player|Bot):
        if isinstance(player, Player):
            target: Player = self.game_controller.ui_action(GameActions.DECIDE_DRAW3)
        else:
            target: Player = player.decide_draw3(self.players)

        self.draw_card()

    def _decide_second_chance(self, player: Player|Bot):
        if not player.has_second_chance():
            target: Player = player
        else:
            if isinstance(player, Player):
                target: Player = self.game_controller.ui_action(GameActions.DECIDE_SECONDCHANCE)
            else:
                target: Player = player.decide_secondchance(self.players)

        target.draw_card(Card('secondchance'))

    def _wait(self):
        self.wait_for_action = True
        while self.wait_for_action:
            pass