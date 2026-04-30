from enum import Enum

class GameActions(Enum):
    NEXT_TURN = 'next_turn'
    DECIDE_DRAW = 'decide_draw'
    DECIDE_STOP = 'decide_stop'
    DECIDE_DRAW3 = 'decide_draw3'
    DECIDE_SECONDCHANCE = 'decide_secondchance'