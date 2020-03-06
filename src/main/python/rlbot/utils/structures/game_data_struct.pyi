from dataclasses import dataclass
from enum import IntEnum
from typing import List


# This file was created by hand for the sole purpose of giving bot makers better autocomplete.
# The ctypes structures in game_data_struct.py are what actually transport the data, but they
# fail to give autocomplete in some code editors.

# In some places we will use these classes in our type hints, but ONLY in type hints. These classes
# should probably never be constructed.

@dataclass
class Vector3:
    """
    Note that in Rocket League, the x-axis is backwards from what you might expect.
    The orange goal is in the positive y direction. To the left of the orange goal
    is the positive x direction (yes really). Be careful with trig functions!
    """
    x: float
    y: float
    z: float


@dataclass
class Rotator:
    """
    Values are in radians. For the mathematically inclined:
    Order of application is yaw, pitch, roll
    """
    pitch: float
    yaw: float
    roll: float


@dataclass
class Physics:
    location: Vector3
    rotation: Rotator
    velocity: Vector3
    angular_velocity: Vector3


@dataclass
class Touch:
    player_name: str
    time_seconds: float
    hit_location: Vector3
    hit_normal: Vector3
    team: int
    player_index: int


@dataclass
class ScoreInfo:
    score: int
    goals: int
    own_goals: int
    assists: int
    saves: int
    shots: int
    demolitions: int


@dataclass
class BoxShape:
    length: float
    width: float
    height: float


@dataclass
class SphereShape:
    diameter: float


@dataclass
class CylinderShape:
    diameter: float
    height: float


@dataclass
class ShapeType(IntEnum):
    box = 0
    sphere = 1
    cylinder = 2


@dataclass
class CollisionShape:
    type: ShapeType
    box: BoxShape
    sphere: SphereShape
    cylinder: CylinderShape


@dataclass
class PlayerInfo:
    physics: Physics
    score_info: ScoreInfo
    is_demolished: bool
    has_wheel_contact: bool
    is_super_sonic: bool
    is_bot: bool
    jumped: bool
    double_jumped: bool
    name: str
    team: int
    boost: int
    hitbox: BoxShape
    hitbox_offset: Vector3
    spawn_id: int


@dataclass
class DropShotInfo:
    absorbed_force: float
    damage_index: int
    force_accum_recent: float


@dataclass
class BallInfo:
    physics: Physics
    latest_touch: Touch
    drop_shot_info: DropShotInfo
    collision_shape: CollisionShape


@dataclass
class BoostPadState:
    is_active: bool
    timer: float


@dataclass
class TileInfo:
    tile_state: int


@dataclass
class TeamInfo:
    team_index: int
    score: int


@dataclass
class GameInfo:
    seconds_elapsed: float
    game_time_remaining: float
    is_overtime: bool
    is_unlimited_time: bool
    is_round_active: bool
    is_kickoff_pause: bool
    is_match_ended: bool
    world_gravity_z: bool
    game_speed: float


@dataclass
class GameTickPacket:
    game_cars: List[PlayerInfo]
    num_cars: int
    game_boosts: List[BoostPadState]
    num_boost: int
    game_ball: BallInfo
    game_info: GameInfo
    # dropshot_tiles: List[TileInfo]  Hiding this for now because we don't support dropshot at the moment
    # num_tiles: int  Hiding this for now because we don't support dropshot at the moment
    teams: List[TeamInfo]
    num_teams: int


@dataclass
class BoostPad:
    location: Vector3
    is_full_boost: bool


@dataclass
class GoalInfo:
    team_num: int
    location: Vector3
    direction: Vector3
    width: float
    height: float


@dataclass
class FieldInfoPacket:
    boost_pads: List[BoostPad]
    num_boosts: int
    goals: List[GoalInfo]
    num_goals: int

class DropshotTileState(IntEnum):
    UNKNOWN = 0
    FILLED = 1
    DAMAGED = 2
    OPEN = 3
