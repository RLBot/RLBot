import random
from typing import Any, NewType, Union, Optional, Mapping, Iterator, Tuple
import traceback
from datetime import datetime, timedelta

from rlbot.utils.structures import game_data_struct as gd
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState
from rlbot.setup_manager import SetupManager
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils import rate_limiter

# Extend Pass or Fail to more detailed metrics

class Pass:
    """ Indicates that the bot passed the exercise. """
    def __repr__(self):
        return 'PASS'

class Fail:
    """ Indicates that the bot failed the exercise. """
    def __repr__(self):
        return 'FAIL'

class FailDueToExerciseException(Fail):
    """ Indicates that the test code threw an expetion. """
    def __init__(self, exception: Exception, traceback_string: str):
        self.exception = exception
        self.traceback_string = traceback_string
    def __repr__(self):
        return 'FAIL: Exception raised by Exercise:\n' + self.traceback_string

# Note: not using Grade as a abstract base class for Pass/Fail
#       as there should not be Grades which are neither Pass nor Fail.
Grade = Union[Pass, Fail]

class Exercise:
    """
    Statisfy this interface to define your test cases.
    This class provides a seeded random generator to support variation testing.
    The responsibility of detecting timeouts lies with the implementation of 
    on_tick().
    """

    """
    Gets the config with which this exercise should be run.
    It is required to be immutable. (Fixed per instance)
    """
    def get_config_path(self) -> str:
        raise NotImplementedError()

    """
    Returns the state in which the game should start in. 
    :param random: A seeded random number generator. For repeated runs of this
        exercise, this parameter and the bots should be the only things which  
        causes variations between runs.
    """
    def setup(self, rng: random.Random) -> GameState:
        raise NotImplementedError()

    """
    This method is called each tick to allow you to make an assessment of the 
    performance of the bot(s).
    The order for whether on_tick comes before the bots recieving the packet is undefined.

    If this method returns None, the run of the exercise will continue.
    If this method returns Pass() or Fail() or raises an exceptions, the run of
    the exercise is terminated and any metrics will be returned.
    """
    def on_tick(self, game_tick_packet: GameTickPacket) -> Optional[Grade]:
        raise NotImplementedError()

class Result:
    def __init__(self, input_exercise: Exercise, input_seed: int, grade: Grade):
        assert grade
        self.seed = input_seed
        self.exercise = input_exercise
        self.grade = grade

"""
Runs all the given named exercises.
We order the runs such the number of match changes is minimized as they're slow.
"""
def run_all_exercises(exercises: Mapping[str, Exercise], seed=4) -> Iterator[Tuple[str, Result]]:
    run_tuples = sorted((ex.get_config_path(), name, ex) for name, ex in exercises.items())
    prev_config_path = None
    results = {}
    # TODO: contextmanager for SetupManager
    setup_manager = SetupManager()
    for config_path, name, ex in run_tuples:
        if config_path != prev_config_path:
            _setup_match(config_path, setup_manager)
            prev_config_path = config_path
        yield (name, _run_exercise(ex, seed))
    setup_manager.shut_down()

"""
Runs one exercise repeatedly with different seeds.
e.g. You can use this to improve a situation your bot finds difficult by leaving
     train_repeatedly() running and changing your bots code.
"""
def train_repeatedly(ex: Exercise, keep_training=lambda result: True, initial_seed=4):
    seed = initial_seed
    keep_looping = True
    setup_manager = SetupManager()
    _setup_match(ex.get_config_path(), setup_manager)

    while keep_looping:
        result = _run_exercise(ex, seed)
        seed += 1
    setup_manager.shut_down()


def _setup_match(config_path: str, manager: SetupManager):
    manager.connect_to_game()
    manager.load_config(config_location=config_path)
    manager.launch_ball_prediction()
    manager.launch_quick_chat_manager()
    manager.launch_bot_processes()
    manager.start_match()

def _run_exercise(ex: Exercise, seed: int) -> Result:
    # TODO: Timeout
    grade = None
    rate_limit = rate_limiter.RateLimiter(120)
    last_tick_game_time = None  # What the tick time of the last observed tick was
    last_call_real_time = datetime.now()  # When we last called the Agent
    game_tick_packet = gd.GameTickPacket()  # We want to do a deep copy for game inputs so people don't mess with em
    game_interface = GameInterface(get_logger('run_exercise'))
    game_interface.load_interface()

    # Set the game state
    rng = random.Random()
    rng.seed(seed)
    try:
        game_state = ex.setup(rng)
    except Exception as e:
        return Result(ex, seed, FailDueToExerciseException(e, traceback.format_exc()))
    game_interface.set_game_state(game_state)

    # Run until the Exercise finishes.
    while grade is None:
        before = datetime.now()

        # Read from game data shared memory
        game_interface.update_live_data_packet(game_tick_packet)

        # Run ex.on_tick() only if the game_info has updated.
        tick_game_time = game_tick_packet.game_info.seconds_elapsed
        if tick_game_time != last_tick_game_time:
            last_tick_game_time = tick_game_time
            try:
                grade = ex.on_tick(game_tick_packet)
            except Exception as e:
                return Result(ex, seed, FailDueToExerciseException(e, traceback.format_exc()))

        after = datetime.now()
        rate_limit.acquire(after - before)

    return Result(ex, seed, grade)
