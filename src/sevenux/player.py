from sevenux.PlayerDoubleException import PlayerDoubleException
from sevenux.card import Card

class Player:
    def __init__(self, name: str):
        self.is_bot = False
        self.name: str = name
        self.cards: list[Card] = []
        self.second_chance: bool = False
        self.jokers: list[Card] = []
        self.x2: bool = False
        self.is_stopped: bool = False
        self.is_knocked_out: bool = False
        self.total_points = 0

    def add_card(self, card: Card):
        if card.is_plus_joker():
            self.jokers.append(card)
        elif card.is_second_chance():
            self.second_chance = True
        elif card.is_x2():
            self.x2 = True
        elif card.is_stop():
            self.is_stopped = True
            self.is_knocked_out = False
        else:
            self._check_for_double(card)
            self.cards.append(card)

    def stop(self):
        self.is_stopped = True
        self.is_knocked_out = False

    def reset_for_round(self):
        self.cards = []
        self.second_chance = False
        self.jokers = []
        self.x2 = False
        self.is_stopped = False
        self.is_knocked_out = False

    def _check_for_double(self, card: Card):
        has_double: bool = any(existing.value == card.value for existing in self.cards)

        if has_double:
            had_second_chance = self.second_chance
            if had_second_chance:
                self.second_chance = False
            else:
                self.is_stopped = True
                self.is_knocked_out = True
            
            raise PlayerDoubleException(self, had_second_chance)

    def has_second_chance(self):
        return self.second_chance

    def has_x2(self):
        return self.x2
    
    def is_risky(self, min_bust_probability: float | None = None) -> bool:
        """
        Flip 7 heuristic: a draw is "risky" if the chance of immediately
        busting (drawing a number already owned) is high.

        Uses the standard Flip 7 deck distribution (0x1, 1..12 with N copies
        of N, plus action/joker cards), and subtracts this player's current
        number cards from the deck to estimate the next-draw bust probability.
        """
        if min_bust_probability is None:
            # Base: start getting cautious once duplicate chance gets noticeable.
            min_bust_probability = 0.40

            # Second chance reduces the penalty of busting once -> we can accept more risk.
            if self.has_second_chance():
                min_bust_probability += 0.15

            # x2 amplifies the value of current points -> be more conservative.
            if self.has_x2():
                min_bust_probability -= 0.10

            # At higher scores, the opportunity cost of busting is higher.
            if self.current_points >= 18:
                min_bust_probability -= 0.05

            min_bust_probability = max(0.10, min(0.90, min_bust_probability))

        owned_numbers: set[str] = {c.value for c in self.cards if c.value.isdigit()}
        if not owned_numbers:
            return False

        # Base deck composition (must match sevenux.deck.Deck)
        remaining_counts: dict[str, int] = {'0': 1}
        for n in range(1, 13):
            remaining_counts[str(n)] = n

        # Action / modifier cards are "safe" w.r.t. busting on a duplicate number.
        # Deck has 16 non-number entries, but one of them is '0' (a number), counted above.
        remaining_action_cards = 15  # +2,+4,+6,+8,+10,x2, 3x stop, 3x draw3, 3x secondchance

        # Remove the numbers this player already drew from the remaining deck.
        for number in owned_numbers:
            if number in remaining_counts:
                remaining_counts[number] = max(0, remaining_counts[number] - 1)

        remaining_numbers_total = sum(remaining_counts.values())
        remaining_total = remaining_numbers_total + remaining_action_cards
        if remaining_total <= 0:
            return True

        bust_cards_remaining = sum(remaining_counts.get(n, 0) for n in owned_numbers)
        bust_probability = bust_cards_remaining / remaining_total
        return bust_probability >= min_bust_probability

    @property
    def current_points(self) -> int:
        if self.is_knocked_out:
            return 0

        current_points = 0

        for card in self.cards:
            current_points += int(card.value)

        if self.x2:
            current_points *= 2

        for joker in self.jokers:
            if joker.is_plus_joker():
                current_points += int(joker.value[1:])

        return current_points
