from RLBotFramework.botmanager.bot_manager import BotManager
from RLBotFramework.utils.structures import game_data_struct as gd
from RLBotFramework.utils.structures.bot_input_struct import PlayerInput


class BotManagerStruct(BotManager):
    def __init__(self, terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                 agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        See documentation on BotManager.
        """
        super().__init__(terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                         agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder)
        self.game_tick_proto = None

    def prepare_for_run(self):
        # Set up shared memory map (offset makes it so bot only writes to its own input!) and map to buffer
        self.bot_input = PlayerInput()
        # Set up shared memory for game data
        self.game_tick_packet = gd.GameTickPacket()  # We want to do a deep copy for game inputs so people don't mess with em

    def call_agent(self, agent, agent_class):
        controller_input = agent.get_output_vector(self.game_tick_packet)
        if not controller_input:
            raise Exception('Agent "{}" did not return a player_input tuple.'.format(agent_class.__name__))

        player_input = self.bot_input

        # Write all player inputs
        player_input.fThrottle = controller_input[0]
        player_input.fSteer = controller_input[1]
        player_input.fPitch = controller_input[2]
        player_input.fYaw = controller_input[3]
        player_input.fRoll = controller_input[4]
        player_input.bJump = controller_input[5]
        player_input.bBoost = controller_input[6]
        player_input.bHandbrake = controller_input[7]
        self.game_interface.update_player_input(player_input, self.index)

    def get_game_time(self):
        return self.game_tick_packet.gameInfo.TimeSeconds

    def pull_data_from_game(self):
        self.game_interface.update_live_data_packet(self.game_tick_packet)