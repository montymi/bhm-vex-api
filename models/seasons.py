from enum import Enum

class Seasons(Enum):
    """
    Enum representing different seasons for VEX V5.
    
    Each team has a unique identifier and name.
    """
    VEX2526 = 197
    VEX2425 = 190
    VRC2324 = 181
    VRC2223 = 173
    VRC2122 = 154
    VRC2021 = 139
    
    @classmethod
    def get_all_values(cls):
        """Returns a list of all season values."""
        return [season.value for season in cls]