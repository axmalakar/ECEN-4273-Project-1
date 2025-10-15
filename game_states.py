"""
Game state management.
"""
from enum import Enum, auto


class GameState(Enum):
    """Enumeration of possible game states."""
    PLAYING = auto()
    PAUSED = auto()
    BLACKJACK = auto()
    CUTSCENE = auto()