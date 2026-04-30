class Card:
    value: str

    def __init__(self, value: str):
        self.value = value

    def is_stop(self):
        return self.value == 'stop'

    def is_draw3(self):
        return self.value == 'draw3'

    def is_second_chance(self):
        return self.value == 'secondchance'

    def is_plus_joker(self):
        return self.value.startswith('+')