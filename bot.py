from card import Card
from player import Player

class Bot(Player):
    def decide_draw(self) -> bool:
        if self.has_second_chance():
            return True

        if 12 in self.cards or 11 in self.cards or 10 in self.cards:
            return self.current_points < 12

        return self.current_points < 18

    def decide_draw3(self, players: list[Player]):
        return self

    def decide_secondchance(self, players: list[Player]):
        return self