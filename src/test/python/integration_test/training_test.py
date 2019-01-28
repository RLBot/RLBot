from pathlib import Path
from typing import List, Optional
import math
import random
import unittest

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.setup_manager import setup_manager_context
from rlbot.training.training import Pass, Fail, Exercise, run_exercises, FailDueToExerciseException, Result
from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, Physics, Vector3, Rotator
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.structures.game_data_struct import GameTickPacket

"""
Tests that the training API works correctly.
If you'd like to bootstrap your own training framework this file might help as a
guide for what's required.
However, if you just want to implement training for your bot, check out
https://github.com/RLBot/RLBotTraining
"""

class FailWithReason(Fail):
    def __init__(self, reason: str):
        self.reason = reason

    def __repr__(self) -> str:
        return f'{super().__repr__()}: {self.reason}'


class BallInFrontOfCar(Exercise):
    """
    This exercise tests that the bot drives towards a stationary ball.
    It assumes that the config specifies exactly one bot.
    """

    def __init__(
            self,
            name: str,
            car_location: Vector3,
            ball_location: Vector3 = Vector3(0,4500,100),
            timeout_seconds: float = 5.0
        ):
        self.name = name
        self.car_location = car_location
        self.ball_location = ball_location
        self.timeout_seconds = timeout_seconds
        self._reset_state()

    def get_name(self):
        return self.name

    def get_match_config(self) -> MatchConfig:
        return read_match_config_from_file(Path(__file__).parent / 'training_test.cfg')

    def _reset_state(self):
        """
        Resets all state that is made between on_tick calls.
        This allows this exercise to be run with multiple seeds.
        """
        self.init_game_seconds = None
        self.init_scores = None

    def setup(self, rng: random.Random) -> GameState:
        self._reset_state()
        return GameState(
            ball=BallState(physics=Physics(
                location=self.ball_location,
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=self.car_location,
                        rotation=Vector3(
                            0,
                            math.atan2(  # face the ball
                                self.ball_location.y - self.car_location.y,
                                self.ball_location.x - self.car_location.x,
                            ),
                            0
                        ),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    jumped=False,
                    double_jumped=False,
                    boost_amount=100)
            },
            boosts={i: BoostState(0) for i in range(34)},
        )

    def on_tick(self, game_tick_packet: GameTickPacket) -> Optional[Result]:
        car_pos = game_tick_packet.game_cars[0].physics.location
        ball_pos = game_tick_packet.game_ball.physics.location
        to_ball_x = ball_pos.x - car_pos.x
        to_ball_y = ball_pos.y - car_pos.y
        dist_to_ball = math.sqrt(to_ball_x ** 2 + to_ball_y ** 2)

        # Did we score?
        scores = [int(team.score) for team in game_tick_packet.teams]
        if self.init_scores is None:
            self.init_scores = scores
        elif scores != self.init_scores:
            if scores[0] - self.init_scores[0] > 0:
                return Pass()  # GOOOAAL!
            elif scores[1] - self.init_scores[1] > 0:
                return FailWithReason('own goal') # oops

        # timeout
        seconds_elapsed = game_tick_packet.game_info.seconds_elapsed
        if self.init_game_seconds is None:
            self.init_game_seconds = seconds_elapsed
        if seconds_elapsed - self.init_game_seconds > self.timeout_seconds:
            overtime_ratio = 1/0  # this error is intentional
            return FailWithReason(f"Hit the timout of {self.timeout_seconds} seconds ({ratio_over_time}% over")

class TrainingTest(unittest.TestCase):

    def test_run_exercises(self):
        ownGoalExercise = BallInFrontOfCar('BallInFrontOfCar(facing own goal)', Vector3(0, -4000, 0), ball_location=Vector3(0,-4500,100))
        seed = 4
        with setup_manager_context() as setup_manager:
            result_iter = run_exercises(
                setup_manager,
                [
                    BallInFrontOfCar('BallInFrontOfCar(goal 1)', Vector3(0, 3500, 0)),
                    BallInFrontOfCar('BallInFrontOfCar(goal 2)', Vector3(1000, 3500, 0)),
                    ownGoalExercise,
                    BallInFrontOfCar('BallInFrontOfCar(sideways)', Vector3(-1500, 0, 0), ball_location=Vector3(1500, 0, 100)),
                ],
                seed
            )

            result = next(result_iter)
            self.assertEqual(result.exercise.get_name(), 'BallInFrontOfCar(goal 1)')
            self.assertIsInstance(result.grade, Pass)

            result = next(result_iter)
            self.assertEqual(result.exercise.get_name(), 'BallInFrontOfCar(goal 2)')
            self.assertIsInstance(result.grade, Pass)

            result = next(result_iter)
            self.assertEqual(result.exercise.get_name(), 'BallInFrontOfCar(facing own goal)')
            self.assertIsInstance(result.grade, Fail)
            self.assertIsInstance(result.grade, FailWithReason)
            self.assertEqual(result.grade.reason, 'own goal')
            self.assertIs(result.exercise, ownGoalExercise)
            self.assertIsInstance(result.seed, int)

            result = next(result_iter)
            self.assertEqual(result.exercise.get_name(), 'BallInFrontOfCar(sideways)')
            self.assertIsInstance(result.grade, Fail)
            self.assertIsInstance(result.grade, FailDueToExerciseException)
            self.assertIsInstance(result.grade.exception, Exception)
            self.assertIsInstance(result.grade.exception, ArithmeticError) # 1/0

            try:
                next(result_iter)
                self.Fail('expected the result_iter to be finished.')
            except StopIteration:
                pass

    def test_render_call(self):
        test_self = self
        class RenderTestExercise(Exercise):
            def get_name(self):
                return 'RenderTestExercise'
            def get_match_config(self) -> MatchConfig:
                return read_match_config_from_file(Path(__file__).parent / 'training_test.cfg')
            def setup(self, rng: random.Random) -> GameState:
                self.num_render_calls = 0
                self.num_on_tick_calls = 0
                return GameState()
            def on_tick(self, game_tick_packet: GameTickPacket) -> Optional[Result]:
                self.num_on_tick_calls += 1
                if self.num_on_tick_calls >= 100:
                    nonlocal test_self
                    test_self.assertEqual(self.num_on_tick_calls-1, self.num_render_calls)
                    return Pass()
            def render(self, renderer: RenderingManager):
                self.num_render_calls += 1

        with setup_manager_context() as setup_manager:
            results = list(run_exercises(setup_manager, [RenderTestExercise()], 4))
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertIsInstance(result.grade, Pass)


if __name__ == '__main__':
    unittest.main()
