from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Mapping, Iterator, Iterable, Tuple, List
import random
import time
import traceback

from rlbot.training.status_rendering import training_status_renderer_context, Row
from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.setup_manager import SetupManager, setup_manager_context
from rlbot.utils import rate_limiter
from rlbot.utils.game_state_util import GameState
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.game_interface import GameInterface

"""
This file contains a minimal API to implement training.
For a more useful API see: https://github.com/RLBot/RLBotTraining/
"""


# Extend Pass and/or Fail to add your own, more detailed metrics.

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

    def get_name(self) -> str:
        """
        Gets the name to be displayed on screen.
        """
        raise NotImplementedError()

    def get_match_config(self) -> MatchConfig:
        """
        Gets the config with which this exercise should be run.
        """
        raise NotImplementedError()

    def setup(self, rng: random.Random) -> GameState:
        """
        Returns the state in which the game should start in.
        The implementing class is responsible for resetting the state after setup is called,
        such that the exercise can be run multiple times to get the same result.
        :param random: A seeded random number generator. For repeated runs of this
            exercise, this parameter and the bots should be the only things which
            causes variations between runs.
        """
        raise NotImplementedError()

    def on_tick(self, game_tick_packet: GameTickPacket) -> Optional[Grade]:
        """
        This method is called each tick to allow you to make an assessment of the
        performance of the bot(s).
        The order for whether on_tick comes before the bots recieving the packet is undefined.

        If this method returns None, the run of the exercise will continue.
        If this method returns Pass() or Fail() or raises an exceptions, the run of
        the exercise is terminated and any metrics will be returned.
        """
        raise NotImplementedError()

    def render(self, renderer: RenderingManager):
        """
        This method is called each tick to render exercise debug information.
        This method is called after on_tick().
        It is optional to override this method.
        """
        pass


class Result:
    def __init__(self, input_exercise: Exercise, input_seed: int, grade: Grade):
        assert grade
        self.seed = input_seed
        self.exercise = input_exercise
        self.grade = grade


def run_exercises(setup_manager: SetupManager, exercises: Iterable[Exercise], seed: int) -> Iterator[Result]:
    """
    It is recommended to use setup_manager_context() to generate your setup_manager.
    """
    game_interface = setup_manager.game_interface
    names = [exercise.get_name() for exercise in exercises]
    with training_status_renderer_context(names, game_interface.renderer) as ren:
        for i, exercise in enumerate(exercises):
            def update_row(status: str, status_color_func):
                nonlocal i
                nonlocal exercise
                ren.update(i, Row(exercise.get_name(), status, status_color_func))

            update_row('config', ren.renderman.white)
            # Only reload the match if the config has changed.
            new_match_config = exercise.get_match_config()
            if new_match_config != setup_manager.match_config:
                update_row('match', ren.renderman.white)
                _setup_match(new_match_config, setup_manager)
                update_row('bots', ren.renderman.white)
                _wait_until_bots_ready(setup_manager)

            update_row('wait', ren.renderman.white)
            _wait_until_good_ticks(game_interface)

            update_row('setup', ren.renderman.white)
            error_result = _setup_exercise(game_interface, exercise, seed)
            if error_result is not None:
                update_row('setup', ren.renderman.red)
                yield error_result
                continue

            update_row('reload', ren.renderman.white)
            setup_manager.reload_all_agents(quiet=True)

            # Wait for the set_game_state() to propagate before we start running ex.on_tick()
            # TODO: wait until the game looks similar.
            update_row('sleep', ren.renderman.white)
            time.sleep(0.03)

            update_row('>>>>', ren.renderman.white)
            result = _grade_exercise(game_interface, exercise, seed)

            if isinstance(result.grade, Pass):
                update_row('PASS', ren.renderman.green)
            else:
                update_row('FAIL', ren.renderman.red)

            yield result


def _wait_until_bots_ready(setup_manager: SetupManager):
    total_ready = 0
    total_ready += setup_manager.try_recieve_agent_metadata()
    logger = get_logger(DEFAULT_LOGGER)
    while total_ready < setup_manager.num_participants:
        logger.debug('Waiting on all bots to post their metadata.')
        time.sleep(0.1)
        total_ready += setup_manager.try_recieve_agent_metadata()


def _wait_until_good_ticks(game_interface: GameInterface, required_new_ticks: int=3):
    """Blocks until we're getting new packets, indicating that the match is ready."""
    rate_limit = rate_limiter.RateLimiter(120)
    last_tick_game_time = None  # What the tick time of the last observed tick was
    game_tick_packet = GameTickPacket()  # We want to do a deep copy for game inputs so people don't mess with em
    seen_times = 0
    while seen_times < required_new_ticks:
        loop_begin_time = datetime.now()

        # Read from game data shared memory
        game_interface.update_live_data_packet(game_tick_packet)
        tick_game_time = game_tick_packet.game_info.seconds_elapsed
        if tick_game_time != last_tick_game_time and game_tick_packet.game_info.is_round_active:
            last_tick_game_time = tick_game_time
            seen_times += 1

        rate_limit.acquire(datetime.now() - loop_begin_time)


def _setup_match(match_config: MatchConfig, manager: SetupManager):
    manager.shut_down(quiet=True)  # To be safe.
    manager.load_match_config(match_config)
    manager.launch_quick_chat_manager()
    manager.launch_ball_prediction()
    manager.launch_bot_processes()
    manager.start_match()


def _setup_exercise(game_interface: GameInterface, ex: Exercise, seed: int) -> Optional[Result]:
    """
    Set the game state.
    Only returns a result if there was an error in ex.setup()
    """
    rng = random.Random()
    rng.seed(seed)
    try:
        game_state = ex.setup(rng)
    except Exception as e:
        return Result(ex, seed, FailDueToExerciseException(e, traceback.format_exc()))
    game_interface.set_game_state(game_state)


def _grade_exercise(game_interface: GameInterface, ex: Exercise, seed: int) -> Result:
    grade = None
    rate_limit = rate_limiter.RateLimiter(120)
    last_tick_game_time = None  # What the tick time of the last observed tick was
    game_tick_packet = GameTickPacket()  # We want to do a deep copy for game inputs so people don't mess with em

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
                ex.render(game_interface.renderer)
            except Exception as e:
                return Result(ex, seed, FailDueToExerciseException(e, traceback.format_exc()))

        after = datetime.now()
        rate_limit.acquire(after - before)

    return Result(ex, seed, grade)
