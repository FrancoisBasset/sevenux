from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sevenux.player import Player

class PlayerDoubleException(Exception):
    def __init__(self, _player: Player, with_second_chance: bool):
        self.player = _player
        self.with_second_chance = with_second_chance
        super().__init__()