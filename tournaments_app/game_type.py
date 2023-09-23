
from enum import Enum
class GAME_TYPES(Enum):
    SWISS_BO1 = 1
    SINGLE_ELIMINATION_BO1 = 2
    SWISS_BO3 = 3
    SINGLE_ELIMINATION_BO3 = 4
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

# class SCORE_TYPES(Enum):
