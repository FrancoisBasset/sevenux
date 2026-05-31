from sevenux.PlayerDoubleException import PlayerDoubleException
from sevenux.bot import Bot
from sevenux.card import Card
from sevenux.deck import Deck
from sevenux.game_actions import GameActions
from sevenux.player import Player

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sevenux.game_controller import GameController

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
    def players_in_game(self) -> list[Player|Bot]:
        return [p for p in self.players if not p.is_stopped]

    @property
    def bots_to_choose(self) -> list[Bot]:
        return [bot for bot in self.bots if not bot.is_stopped]

    def get_current_player(self) -> Player|Bot:
        self.turn = (self.turn + 1) % len(self.players)
        return self.players[self.turn]

    def next_turn(self) -> bool:
        player: Player|Bot = self.get_current_player()

        if player.is_stopped:
            return False

        self.game_controller.ui_action(GameActions.PRINT_MESSAGE, 'Au tour de ' + player.name)

        draw: bool = self._decide_draw(player)
        if not draw:
            player.stop()
            return True

        return self.draw_card(player)

    def draw_card(self, player: Player):
        card: Card = self.deck.draw_card()

        self.game_controller.ui_action(GameActions.PRINT_MESSAGE, 'Carte piochée : ' + card.value)

        if card.is_stop():
            self._decide_stop(player)
        elif card.is_draw3():
            self._decide_draw3(player)
        elif card.is_second_chance():
            self._decide_second_chance(player)
        else:
            try:
                player.add_card(card)
            except PlayerDoubleException:
                self.game_controller.ui_action(GameActions.PRINT_MESSAGE, 'Le joueur a déjà une carte en double')
        return not self.deck.is_empty()

    def _decide_draw(self, player: Player|Bot) -> bool:
        if isinstance(player, Bot):
            return player.decide_draw()
        else:
            return self.game_controller.ui_action(GameActions.DECIDE_DRAW)

    def _decide_stop(self, player: Player|Bot):
        if isinstance(player, Bot):
            target: Player = player.decide_stop(self.players)
        else:
            if len(self.bots_to_choose) == 0:
                target: Player = player
            elif len(self.bots_to_choose) == 1:
                target: Player = self.bots_to_choose[0]
            else:
                target: Player = self.game_controller.ui_action(GameActions.DECIDE_STOP)

        target.stop()
        self.game_controller.ui_action(GameActions.PRINT_MESSAGE, target.name + ' doit arrêter de jouer')

    def _decide_draw3(self, player: Player|Bot):
        if len(self.players_in_game) == 0:
            target: Player = player
        elif not player.is_bot:
            choice = self.game_controller.ui_action(GameActions.DECIDE_DRAW3)

            if choice is True:
                target: Player = player
            else:
                target: Player = choice
        else:
            target: Player = player.decide_draw3(self.players)

        text += '[' + player.name + ' ' + ' '.join(card.value for card in player.cards) + '] ' + target.name + ' doit piocher 3 cartes'
        self.game_controller.ui_action(GameActions.PRINT_MESSAGE, text)
        self.draw_card(target)
        self.draw_card(target)
        self.draw_card(target)

    def _decide_second_chance(self, player: Player|Bot):
        if not player.has_second_chance():
            target: Player = player
        else:
            if isinstance(player, Player):
                target: Player = self.game_controller.ui_action(GameActions.DECIDE_SECONDCHANCE)
            else:
                target: Player = player.decide_secondchance(self.players)

        target.add_card(Card('secondchance'))

    def _wait(self):
        self.wait_for_action = True
        while self.wait_for_action:
            pass

    def count_scores(self) -> int:
        for player in self.players:
            player.total_points += player.current_points