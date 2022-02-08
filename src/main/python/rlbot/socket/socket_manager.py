from enum import IntEnum
from socket import socket, SHUT_RDWR, SHUT_WR
from time import sleep
from typing import List, Callable, TYPE_CHECKING

from rlbot.utils.game_state_util import GameState

from flatbuffers.builder import Builder
from rlbot.agents.base_agent import SimpleControllerState
if TYPE_CHECKING:
    from rlbot.matchconfig.match_config import MatchConfig
from rlbot.messages.flat import ReadyMessage
from rlbot.messages.flat.BallPrediction import BallPrediction
from rlbot.messages.flat.DesiredGameState import DesiredGameState
from rlbot.messages.flat.FieldInfo import FieldInfo
from rlbot.messages.flat.GameMessage import GameMessage
from rlbot.messages.flat.GameTickPacket import GameTickPacket
from rlbot.messages.flat.MatchSettings import MatchSettings
from rlbot.messages.flat.MessagePacket import MessagePacket
from rlbot.messages.flat.PlayerInputChange import PlayerInputChange
from rlbot.messages.flat.PlayerSpectate import PlayerSpectate
from rlbot.messages.flat.PlayerStatEvent import PlayerStatEvent
from rlbot.messages.flat.QuickChat import QuickChat
from rlbot.utils.logging_utils import get_logger

# We can connect to RLBot.exe on this port.
RLBOT_SOCKETS_PORT = 23234

class SocketDataType(IntEnum):
    GAME_TICK_PACKET = 1
    FIELD_INFO = 2
    MATCH_SETTINGS = 3
    PLAYER_INPUT = 4
    ACTOR_MAPPING = 5
    COMPUTER_ID = 6
    DESIRED_GAME_STATE = 7
    RENDER_GROUP = 8
    QUICK_CHAT = 9
    BALL_PREDICTION = 10
    READY_MESSAGE = 11
    MESSAGE_PACKET = 12


def int_to_bytes(val: int) -> bytes:
    return val.to_bytes(2, byteorder='big')


def int_from_bytes(bytes: bytes) -> int:
    return int.from_bytes(bytes, 'big')


class SocketMessage:
    def __init__(self, type: SocketDataType, data: bytes):
        self.type = type
        self.data = data


def read_from_socket(s: socket) -> SocketMessage:
    type_int = int_from_bytes(s.recv(2))
    if type_int == 0:
        raise EOFError()
    data_type = SocketDataType(type_int)
    size = int_from_bytes(s.recv(2))
    data = s.recv(size)
    return SocketMessage(data_type, data)


class SocketRelay:
    def __init__(self, connection_timeout:float=120):
        self.connection_timeout = connection_timeout
        self.logger = get_logger('socket_man')
        self.socket = socket()
        self.is_connected = False
        self._should_continue = True
        self.on_connect_handlers: List[Callable[[], None]] = []
        self.packet_handlers: List[Callable[[GameTickPacket], None]] = []
        self.field_info_handlers: List[Callable[[FieldInfo], None]] = []
        self.match_settings_handlers: List[Callable[[MatchSettings], None]] = []
        self.quick_chat_handlers: List[Callable[[QuickChat], None]] = []
        self.ball_prediction_handlers: List[Callable[[BallPrediction], None]] = []
        self.player_input_change_handlers: List[Callable[[PlayerInputChange, float, int], None]] = []
        self.player_stat_handlers: List[Callable[[PlayerStatEvent, float, int], None]] = []
        self.player_spectate_handlers: List[Callable[[PlayerSpectate, float, int], None]] = []
        self.raw_handlers: List[Callable[[SocketMessage], None]] = []

    def send_flatbuffer(self, builder: Builder, data_type: SocketDataType):
        flatbuffer_bytes = builder.Output()
        size = len(flatbuffer_bytes)
        message = int_to_bytes(data_type) + int_to_bytes(size) + flatbuffer_bytes
        self.socket.sendall(message)

    def send_player_input(self, player_index: int, input: SimpleControllerState):
        builder = input.to_flatbuffer(player_index)
        self.send_flatbuffer(builder, SocketDataType.PLAYER_INPUT)

    def send_match_config(self, mc: 'MatchConfig'):
        builder = mc.create_flatbuffer()
        self.send_flatbuffer(builder, SocketDataType.MATCH_SETTINGS)

    def send_game_state(self, state: GameState):
        builder = Builder(400)
        game_state_offset = state.convert_to_flat(builder)
        if game_state_offset is None:
            return  # There are no values to be set, so just skip it
        builder.Finish(game_state_offset)
        self.send_flatbuffer(builder, SocketDataType.DESIRED_GAME_STATE)
        pass

    def connect_and_run(self, wants_quick_chat, wants_game_messages, wants_ball_predictions):
        """
        Connects to the socket and begins a loop that reads messages and calls any handlers
        that have been registered. Connect and run are combined into a single method because
        currently bad things happen if the buffer is allowed to fill up.
        """
        self.socket.settimeout(self.connection_timeout)
        for i in range(int(self.connection_timeout * 10)):
            try:
                self.socket.connect(('127.0.0.1', RLBOT_SOCKETS_PORT))
                break
            except ConnectionRefusedError:
                sleep(.1)

        self.socket.settimeout(None)
        self.is_connected = True
        self.logger.info(f"Socket manager connected to port {RLBOT_SOCKETS_PORT} from port {self.socket.getsockname()[1]}!")
        for handler in self.on_connect_handlers:
            handler()

        builder = self.make_ready_message(wants_ball_predictions, wants_game_messages, wants_quick_chat)
        self.send_flatbuffer(builder, SocketDataType.READY_MESSAGE)

        while self._should_continue:
            incoming_message = read_from_socket(self.socket)
            self.handle_incoming_message(incoming_message)

        self.socket.shutdown(SHUT_WR)

        # Now wait for the other end to send its own shutdown signal.
        try:
            while True:
                read_from_socket(self.socket)
        except EOFError:
            # We've succeeded with our graceful shutdown.
            pass

        self.socket.close()

    def make_ready_message(self, wants_ball_predictions, wants_game_messages, wants_quick_chat):
        builder = Builder(50)
        ReadyMessage.ReadyMessageStart(builder)
        ReadyMessage.ReadyMessageAddWantsBallPredictions(builder, wants_ball_predictions)
        ReadyMessage.ReadyMessageAddWantsQuickChat(builder, wants_quick_chat)
        ReadyMessage.ReadyMessageAddWantsGameMessages(builder, wants_game_messages)
        offset = ReadyMessage.ReadyMessageEnd(builder)
        builder.Finish(offset)
        return builder

    def handle_incoming_message(self, incoming_message: SocketMessage):
        for raw_handler in self.raw_handlers:
            raw_handler(incoming_message)
        if incoming_message.type == SocketDataType.GAME_TICK_PACKET and len(self.packet_handlers) > 0:
            packet = GameTickPacket.GetRootAsGameTickPacket(incoming_message.data, 0)
            for handler in self.packet_handlers:
                handler(packet)
        elif incoming_message.type == SocketDataType.FIELD_INFO and len(self.field_info_handlers) > 0:
            field_info = FieldInfo.GetRootAsFieldInfo(incoming_message.data, 0)
            for handler in self.field_info_handlers:
                handler(field_info)
        elif incoming_message.type == SocketDataType.MATCH_SETTINGS and len(self.match_settings_handlers) > 0:
            match_settings = MatchSettings.GetRootAsMatchSettings(incoming_message.data, 0)
            for handler in self.match_settings_handlers:
                handler(match_settings)
        elif incoming_message.type == SocketDataType.QUICK_CHAT and len(self.quick_chat_handlers) > 0:
            quick_chat = QuickChat.GetRootAsQuickChat(incoming_message.data, 0)
            for handler in self.quick_chat_handlers:
                handler(quick_chat)
        elif incoming_message.type == SocketDataType.BALL_PREDICTION and len(self.ball_prediction_handlers) > 0:
            ball_prediction = BallPrediction.GetRootAsBallPrediction(incoming_message.data, 0)
            for handler in self.ball_prediction_handlers:
                handler(ball_prediction)
        elif incoming_message.type == SocketDataType.MESSAGE_PACKET:
            if len(self.player_stat_handlers) > 0 or len(self.player_input_change_handlers) > 0 or len(
                    self.player_spectate_handlers) > 0:
                msg_packet = MessagePacket.GetRootAsMessagePacket(incoming_message.data, 0)
                for i in range(msg_packet.MessagesLength()):
                    msg = msg_packet.Messages(i)
                    msg_type = msg.MessageType()
                    if msg_type == GameMessage.PlayerSpectate and len(self.player_spectate_handlers) > 0:
                        spectate = PlayerSpectate()
                        spectate.Init(msg.Message().Bytes, msg.Message().Pos)
                        for handler in self.player_spectate_handlers:
                            handler(spectate, msg_packet.GameSeconds(), msg_packet.FrameNum())
                    elif msg_type == GameMessage.PlayerStatEvent and len(self.player_stat_handlers) > 0:
                        stat_event = PlayerStatEvent()
                        stat_event.Init(msg.Message().Bytes, msg.Message().Pos)
                        for handler in self.player_stat_handlers:
                            handler(stat_event, msg_packet.GameSeconds(), msg_packet.FrameNum())
                    elif msg_type == GameMessage.PlayerInputChange and len(
                            self.player_input_change_handlers) > 0:
                        input_change = PlayerInputChange()
                        input_change.Init(msg.Message().Bytes, msg.Message().Pos)
                        for handler in self.player_input_change_handlers:
                            handler(input_change, msg_packet.GameSeconds(), msg_packet.FrameNum())

    def disconnect(self):
        self._should_continue = False
