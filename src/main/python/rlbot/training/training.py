import random
from typing import Any, NewType, Union, Optional, Mapping
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState


# Defining the result of an Exercise.
# Metrics are user defined types which could be used to track performance over 
# time. e.g. seconds before touching the ball.
Metrics = NewType('Metrics', Any)

class Pass():
    """ Indicates that the bot passed the exercise. """
    def __init__(self, measured_metrics:Metrics = None):
        self.measured_metrics = measured_metrics

class Fail():
    """ Indicates that the bot failed the exercise. """
    def __init__(self, measured_metrics:Metrics = None):
        self.measured_metrics = measured_metrics

Result = Union[Pass, Fail]


class Exercise():
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
    def setup(self, random: random.Random) -> GameState:
        raise NotImplementedError()

    """
    This method is called each tick to allow you to make an assessment of the 
    performance of the bot(s).
    This method is called before agent code is executed on the game_tick_packet.

    If this method returns None, the run of the exercise will continue.
    If this method returns Pass() or Fail() or raises an exceptions, the run of
    the exercise is terminated and any metrics will be returned.
    """
    def on_tick(self, game_tick_packet: GameTickPacket) -> Optional[Result]:
        raise NotImplementedError()


"""
Runs all the given named exercises.
We order the runs such the number of match changes is minimized as they're slow.
"""
def run_all_exercises(exercises: Mapping[str, Exercise], seed=4) -> Mapping[str, Result]:
    run_tuples = sorted((ex.get_config_path(), name, ex) for ex in exercises)
    prev_config_path = None
    results = {}
    for config_path, name, ex in run_tuples:
        if config_path != prev_config_path:
            _setup_match(config_path)
            prev_config_path = config_path
        results[name] = _run_exercise(test, seed)
    return results

"""
Runs one exercise repeatedly with different seeds.
e.g. You can use this to improve a situation your bot finds difficult by leaving
     train_repeatedly() running and changing your bots code.
"""
def train_repeatedly(ex: Exercise, keep_training=lambda result: True, initial_seed=4):
    seed = initial_seed
    keep_looping = True
    _setup_match(ex.get_config_path())
    while keep_looping:
        result = _run_exercise(ex, seed)
        seed += 1


def _setup_match(config_path: str):
    pass # TODO

def _run_exercise(ex: Exercise, seed: int) -> Result:
    pass # TODO
