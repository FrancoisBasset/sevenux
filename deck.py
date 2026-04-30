from random import shuffle
from card import Card

class Deck:
    cards: list[Card] = []

    def __init__(self):
        self._create_new_deck()

    def _create_new_deck(self):
        values: list[str] = ['0', '+2', '+4', '+6', '+8', '+10', 'x2', 'stop', 'stop', 'stop', 'draw3', 'draw3', 'draw3', 'secondchance', 'secondchance', 'secondchance'];
        self.cards.extend([Card(value) for value in values])

        for i in range(1, 13):
            self.cards.extend([Card(str(i))] * i)

        shuffle(self.cards)

    def draw_card(self) -> Card:
        return self.cards.pop()

    def is_empty(self):
        return len(self.cards) == 0