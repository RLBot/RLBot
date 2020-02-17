from dataclasses import dataclass
from typing import List

from rlbot.utils.structures.game_data_struct import Physics

MAX_SLICES = 360

@dataclass
class Slice:
    physics: Physics
    game_seconds: float


@dataclass
class BallPrediction:
    slices: List[Slice]
    num_slices: int
