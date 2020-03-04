from time import sleep

from rlbot.agents.base_agent import BaseAgent
from rlbot.botmanager.bot_manager import BotManager
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures import ball_prediction_struct as bp
from rlbot.utils.structures import game_data_struct as gd
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick


class BotManagerStruct(BotManager):
    def __init__(self, *args, **kwargs):
        """
        See documentation on BotManager.
        """
        super().__init__(*args, **kwargs)
        self.rigid_body_tick = None

    def prepare_for_run(self):
        # Set up shared memory map (offset makes it so bot only writes to its own input!) and map to buffer
        self.bot_input = PlayerInput()
        # Set up shared memory for game data
        # We want to do a deep copy for game inputs so people don't mess with em
        self.game_tick_packet = gd.GameTickPacket()
        # Set up shared memory for Ball prediction
        self.ball_prediction = bp.BallPrediction()
        # Set up shared memory for rigid body tick
        self.rigid_body_tick = RigidBodyTick()

    def get_field_info(self) -> gd.FieldInfoPacket:
        field_info = gd.FieldInfoPacket()
        self.game_interface.update_field_info_packet(field_info)
        return field_info

    def call_agent(self, agent: BaseAgent, agent_class):
        controller_input = agent.get_output(self.game_tick_packet)
        if controller_input is None:
            get_logger("BotManager" + str(self.index))\
                .error("Agent %s did not return any output.", str(agent_class.__name__))
            return

        player_input = self.bot_input

        if isinstance(controller_input, list):
            # Write all player inputs
            get_logger("BotManager" + str(self.index)).error("Sending legacy packet type, please convert to v4")
            controller_input = agent.convert_output_to_v4(controller_input)

        player_input.throttle = controller_input.throttle
        player_input.steer = controller_input.steer
        player_input.pitch = controller_input.pitch
        player_input.yaw = controller_input.yaw
        player_input.roll = controller_input.roll
        player_input.jump = controller_input.jump
        player_input.boost = controller_input.boost
        player_input.handbrake = controller_input.handbrake
        if hasattr(controller_input, 'use_item'):
            # This is needed for rare cases where bots don't conform to the spec,
            # e.g. Stick returns itself rather than a SimpleControllerState.
            player_input.use_item = controller_input.use_item
        self.game_interface.update_player_input(player_input, self.index)

    def get_game_time(self):
        return self.game_tick_packet.game_info.seconds_elapsed

    def pull_data_from_game(self):
        if self.match_config.enable_lockstep:
            # If we're using lockstep then fresh_live_data_packet is no good because when
            # lockstep freezes the game, we won't get a fresh packet and it'll wait the full timeout.
            # Instead do a clunky sleep here to limit the framerate. Not worried about precision because
            # lockstep will probably never be used in a competitive scenario.
            sleep(1 / self.maximum_tick_rate_preference)
            self.game_interface.update_live_data_packet(self.game_tick_packet)
        else:
            # Set a timeout of 30 milliseconds. It's slightly less than the number of milliseconds (33.33)
            # caused by MAX_AGENT_CALL_PERIOD defined in bot_manager.py
            self.game_interface.fresh_live_data_packet(self.game_tick_packet, 30, self.index)

    def get_ball_prediction_struct(self):
        return self.game_interface.update_ball_prediction(self.ball_prediction)

    def get_spawn_id(self):
        if self.game_tick_packet.num_cars <= self.index:
            return None
        return self.game_tick_packet.game_cars[self.index].spawn_id
