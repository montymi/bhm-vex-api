from enum import Enum


class Teams(Enum):
    """
    Enum representing different teams.

    Each team has a unique identifier and name.
    """

    BH_A = 130515
    BH_B = 133493
    BH_C = 171257
    BH_X = 171256

    @classmethod
    def get_all_values(cls):
        """Returns a list of all team values."""
        return [team.value for team in cls]

