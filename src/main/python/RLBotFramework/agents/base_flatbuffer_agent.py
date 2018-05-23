import flatbuffers
from RLBotFramework.agents.base_agent import BaseAgent
from RLBotMessages.flat import ControllerState
from RLBotMessages.flat import PlayerInput
from RLBotMessages.flat import GameTickPacket


class SimpleControllerState:
    """
    Building flatbuffer objects is verbose and error prone. This class provides a friendlier
    interface to bot makers.
    """

    def __init__(self):
        self.steer = 0.0
        self.throttle = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.jump = False
        self.boost = False
        self.handbrake = False


class BaseFlatbufferAgent(BaseAgent):
    """
    Extend this class if you want to get your game data in flatbuffers format.
    """

    def get_output_flatbuffer(self, game_tick_flatbuffer):
        if game_tick_flatbuffer is None or game_tick_flatbuffer.PlayersLength() - 1 < self.index:
            friendly_state = SimpleControllerState()
        else:
            friendly_state = self.get_output(game_tick_flatbuffer)

        builder = flatbuffers.Builder(0)

        ControllerState.ControllerStateStart(builder)
        ControllerState.ControllerStateAddSteer(builder, friendly_state.steer)
        ControllerState.ControllerStateAddThrottle(builder, friendly_state.throttle)
        ControllerState.ControllerStateAddPitch(builder, friendly_state.pitch)
        ControllerState.ControllerStateAddYaw(builder, friendly_state.yaw)
        ControllerState.ControllerStateAddRoll(builder, friendly_state.roll)
        ControllerState.ControllerStateAddJump(builder, friendly_state.jump)
        ControllerState.ControllerStateAddBoost(builder, friendly_state.boost)
        ControllerState.ControllerStateAddHandbrake(builder, friendly_state.handbrake)
        controller_state = ControllerState.ControllerStateEnd(builder)

        PlayerInput.PlayerInputStart(builder)
        PlayerInput.PlayerInputAddPlayerIndex(builder, self.index)
        PlayerInput.PlayerInputAddControllerState(builder, controller_state)
        player_input = PlayerInput.PlayerInputEnd(builder)

        builder.Finish(player_input)

        return builder

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        Override this to implement your bot
        :param packet: A flatbuffers object with all the game state.
        :return: Controller state to be sent back to the game.
        """

        return SimpleControllerState()
