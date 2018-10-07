from rlbot.agents.base_agent import BaseAgent
from rlbot.botmanager.bot_manager import BotManager
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures import ball_prediction_struct as bp
from rlbot.utils.structures import game_data_struct as gd
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick


class BotManagerStruct(BotManager):
    def __init__(self, terminate_request_event, termination_complete_event, reload_request_event, bot_configuration,
                 name, team, index, agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        See documentation on BotManager.
        """
        super().__init__(terminate_request_event, termination_complete_event, reload_request_event, bot_configuration,
                         name, team, index, agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder)
        self.rigid_body_tick = None

    def prepare_for_run(self):
        # Set up shared memory map (offset makes it so bot only writes to its own input!) and map to buffer
        self.bot_input = PlayerInput()
        # Set up shared memory for game data
        self.game_tick_packet = gd.GameTickPacket()  # We want to do a deep copy for game inputs so people don't mess with em
        # Set up shared memory for Ball prediction
        self.ball_prediction = bp.BallPrediction()
        # Set up shared memory for rigid body tick
        self.rigid_body_tick = RigidBodyTick()

    def get_field_info(self):
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
        self.game_interface.update_player_input(player_input, self.index)

    def get_game_time(self):
        return self.game_tick_packet.game_info.seconds_elapsed

    def pull_data_from_game(self):
        self.game_interface.update_live_data_packet(self.game_tick_packet)

    def get_ball_prediction_struct(self):
        return self.game_interface.update_ball_prediction(self.ball_prediction)
