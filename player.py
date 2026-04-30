from PlayerDoubleException import PlayerDoubleException
from card import Card

class Player:
    name: str
    second_chance: bool = False
    jokers: list[Card] = []
    cards: list[Card] = []
    is_stopped: bool = False

    def __init__(self, name: str):
        self.name = name

    def draw_card(self, card: Card):
        if card.is_plus_joker():
            self.jokers.append(card)
        elif card.is_second_chance():
            self.second_chance = True
        else:
            self._check_for_duplicate(card)
            self.cards.append(card)

    def stop(self):
        self.is_stopped = True
        print(self.name, 'doit arrêter de jouer')

    def _check_for_duplicate(self, card: Card):
        if card in self.cards:
            raise PlayerDoubleException(self)

    def has_second_chance(self):
        return self.second_chance
        
    @property
    def current_points(self) -> int:
        current_points = 0

        for card in self.cards:
            current_points += int(card.value)

        for joker in self.jokers:
            if joker.is_plus_joker():
                current_points += int(joker.value[1:])

        return current_points