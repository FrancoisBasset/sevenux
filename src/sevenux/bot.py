from sevenux.player import Player

class Bot(Player):
    def __init__(self, name: str):
        super().__init__(name)
        self.is_bot: bool = True

    def decide_stop(self, players: list[Player]) -> Player:
        """
        Choose who must stop playing.
        No mercy: always target the human player (is_bot == False) if possible.
        """
        humans = [p for p in players if not getattr(p, 'is_bot', False) and not p.is_stopped]
        if humans:
            return humans[0]

        candidates = [p for p in players if p is not self and not p.is_stopped]
        if not candidates:
            return self

        # Otherwise, stop the most dangerous opponent.
        return max(candidates, key=lambda p: (p.current_points, p.has_x2(), p.has_second_chance()))
    
    def decide_draw(self) -> bool:
        # Use the bust-risk heuristic, taking into account x2 + second chance.
        risky = self.is_risky()

        # With x2, points grow quickly; stop earlier.
        base_limit = 14 if self.has_x2() else 18

        # With a second chance available, accept a bit more.
        if self.has_second_chance():
            base_limit += 4

        if risky:
            return self.current_points < max(10, base_limit - 4)

        return self.current_points < base_limit

    def decide_draw3(self, players: list[Player]) -> Player:
        """
        Decide who should receive the extra draw.
        Returning self means we draw the extra card ourselves.
        """
        # No mercy: if possible, give it to the human player.
        humans = [p for p in players if not getattr(p, 'is_bot', False) and not p.is_stopped]
        if humans:
            return humans[0]

        if self.is_risky():
            # If we're close to busting, try to give it to someone safer.
            candidates = [p for p in players if p is not self and not p.is_stopped]
            if candidates:
                return min(candidates, key=lambda p: (p.is_risky(), p.current_points))
        return self

    def decide_secondchance(self, players: list[Player]) -> Player:
        """
        If we already have a second chance, give it to the player most likely
        to benefit from it (high bust risk, still playing).
        """
        if not self.has_second_chance():
            return self

        # No mercy: never gift the human a second chance if we can avoid it.
        candidates = [
            p
            for p in players
            if p is not self
            and getattr(p, 'is_bot', False)
            and not p.is_stopped
            and not p.has_second_chance()
        ]
        if not candidates:
            return self

        return max(candidates, key=lambda p: (p.is_risky(), p.current_points))
