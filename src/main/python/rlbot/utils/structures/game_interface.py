import ctypes
import os
import sys
import time
import platform
from logging import DEBUG, WARNING

import flatbuffers
from rlbot.messages.flat.MatchSettings import MatchSettings as MatchSettingsPacket
from rlbot.messages.flat.BallPrediction import BallPrediction as BallPredictionPacket
from rlbot.messages.flat.FieldInfo import FieldInfo
from rlbot.messages.flat.QuickChatMessages import QuickChatMessages
from rlbot.utils.file_util import get_python_root
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.rlbot_exception import get_exception_from_error_code, EmptyDllResponse
from rlbot.utils.structures import game_data_struct
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import GameTickPacket, ByteBuffer, FieldInfoPacket
from rlbot.utils.structures.game_status import RLBotCoreStatus
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick
from rlbot.utils.structures.start_match_structures import MatchSettings

if platform.system() == 'Windows':
    dll_name_64 = 'RLBot_Core_Interface.dll'
    dll_name_32 = 'RLBot_Core_Interface_32.dll'
elif platform.system() == 'Linux':
    dll_name_64 = 'libRLBotInterface.so'
    dll_name_32 = 'libRLBotInterface32.so'
elif platform.system() == 'Darwin':
    dll_name_64 = 'libRLBotInterface.dylib'
    dll_name_32 = 'libRLBotInterface32.dylib'

def wrap_callback(callback_func):
    def caller(id, status):
        callback_func(id, status)

    return caller


def get_dll_location():
    return os.path.join(get_dll_directory(), dll_name_64)


def get_dll_32_location():
    return os.path.join(get_dll_directory(), dll_name_32)


def is_32_bit_python():
    return sys.maxsize <= 2**32


def get_dll_directory():
    return os.path.join(get_python_root(), 'rlbot', 'dll')


class GameInterface:
    game = None
    start_match_configuration = None
    game_status_callback_type = None
    callback_func = None
    extension = None

    def __init__(self, logger):
        self.logger = logger
        self.dll_path = get_dll_32_location() if is_32_bit_python() else get_dll_location()
        self.renderer = RenderingManager()
        # wait for the dll to load

    def setup_function_types(self):
        self.wait_until_loaded()
        # update live data packet
        func = self.game.UpdateLiveDataPacket
        func.argtypes = [ctypes.POINTER(GameTickPacket)]
        func.restype = ctypes.c_int

        func = self.game.UpdateFieldInfo
        func.argtypes = [ctypes.POINTER(FieldInfoPacket)]
        func.restype = ctypes.c_int

        func = self.game.UpdateLiveDataPacketFlatbuffer
        func.argtypes = []
        func.restype = ByteBuffer

        func = self.game.UpdateRigidBodyTick
        func.argtypes = [ctypes.POINTER(RigidBodyTick)]
        func.restype = ctypes.c_int

        func = self.game.UpdateFieldInfoFlatbuffer
        func.argtypes = []
        func.restype = ByteBuffer

        func = self.game.GetBallPredictionStruct
        func.argtypes = [ctypes.POINTER(BallPrediction)]
        func.restype = ctypes.c_int

        func = self.game.GetBallPrediction
        func.argtypes = []
        func.restype = ByteBuffer

        # start match
        func = self.game.StartMatch
        func.argtypes = [MatchSettings]
        func.restype = ctypes.c_int

        # update player input
        func = self.game.UpdatePlayerInput
        func.argtypes = [PlayerInput, ctypes.c_int]
        func.restype = ctypes.c_int

        # update player input
        func = self.game.UpdatePlayerInputFlatbuffer
        func.argtypes = [ctypes.c_void_p, ctypes.c_int]
        func.restype = ctypes.c_int

        # send chat
        func = self.game.SendChat
        func.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_bool, self.game_status_callback_type, ctypes.c_void_p]
        func.restype = ctypes.c_int

        func = self.game.SendQuickChat
        func.argtypes = [ctypes.c_void_p, ctypes.c_int]
        func.restype = ctypes.c_int

        func = self.game.ReceiveChat
        func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        func.restype = ByteBuffer

        # set game state
        func = self.game.SetGameState
        func.argtypes = [ctypes.c_void_p, ctypes.c_int]
        func.restype = ctypes.c_int

        func = self.game.GetMatchSettings
        func.argtypes = []
        func.restype = ByteBuffer

        func = self.game.FreshLiveDataPacket
        func.argtypes = [ctypes.POINTER(GameTickPacket), ctypes.c_int, ctypes.c_int]
        func.restype = ctypes.c_int

        func = self.game.FreshLiveDataPacketFlatbuffer
        func.argtypes = [ctypes.c_int, ctypes.c_int]
        func.restype = ByteBuffer

        self.renderer.setup_function_types(self.game)
        self.logger.debug('game interface functions are setup')

        # free the memory at the given pointer
        func = self.game.Free
        func.argtypes = [ctypes.c_void_p]

    def update_live_data_packet(self, game_tick_packet: GameTickPacket):
        rlbot_status = self.game.UpdateLiveDataPacket(game_tick_packet)
        self.game_status(None, rlbot_status)
        return game_tick_packet

    def fresh_live_data_packet(self, game_tick_packet: GameTickPacket, timeout_millis: int, key: int):
        rlbot_status = self.game.FreshLiveDataPacket(game_tick_packet, timeout_millis, key)
        self.game_status(None, rlbot_status)
        return game_tick_packet

    def update_field_info_packet(self, field_info_packet: FieldInfoPacket):
        rlbot_status = self.game.UpdateFieldInfo(field_info_packet)
        self.game_status(None, rlbot_status)
        return field_info_packet

    def update_match_data_packet(self):
        pass

    def start_match(self):
        self.wait_until_loaded()
        # self.game_input_packet.bStartMatch = True
        rlbot_status = self.game.StartMatch(self.start_match_configuration)

        if rlbot_status != 0:
            exception_class = get_exception_from_error_code(rlbot_status)
            raise exception_class()

        self.logger.debug('Starting match with status: %s', RLBotCoreStatus.status_list[rlbot_status])

    def update_player_input(self, player_input, index):
        rlbot_status = self.game.UpdatePlayerInput(player_input, index)
        self.game_status(None, rlbot_status, WARNING)

    def send_chat(self, index, team_only, message_details):
        rlbot_status = self.game.SendChat(message_details, index, team_only, self.create_status_callback(), None)
        self.game_status(None, rlbot_status)

    def send_chat_flat(self, chat_message_builder):
        buf = chat_message_builder.Output()
        rlbot_status = self.game.SendQuickChat(bytes(buf), len(buf))
        self.game_status(None, rlbot_status)
        return rlbot_status

    def receive_chat(self, index, team, last_message_index) -> QuickChatMessages:
        byte_buffer = self.game.ReceiveChat(index, team, last_message_index)
        if byte_buffer.size >= 4:  # GetRootAsGameTickPacket gets angry if the size is less than 4
            # We're counting on this copying the data over to a new memory location so that the original
            # pointer can be freed safely.
            proto_string = ctypes.string_at(byte_buffer.ptr, byte_buffer.size)
            self.game.Free(byte_buffer.ptr)  # Avoid a memory leak
            return QuickChatMessages.GetRootAsQuickChatMessages(proto_string, 0)
        else:
            raise EmptyDllResponse()

    def create_callback(self):
        return

    def game_status(self, id, rlbot_status, level=DEBUG):
        if rlbot_status != RLBotCoreStatus.Success and rlbot_status != RLBotCoreStatus.BufferOverfilled:
            self.logger.log(level, "bad status %s", RLBotCoreStatus.status_list[rlbot_status])

    def wait_until_loaded(self):
        for i in range(0, 120):
            self.game.IsInitialized.restype = ctypes.c_bool
            is_loaded = self.game.IsInitialized()
            if is_loaded:
                self.logger.info('DLL is initialized!')
                return
            else:
                time.sleep(1)
        raise TimeoutError("RLBot took too long to initialize! Was Rocket League started with the -rlbot flag? "
                           "If you're not sure, close Rocket League and let us open it for you next time!")

    def wait_until_valid_packet(self):
        self.logger.info('Waiting for valid packet...')
        for i in range(0, 60):
            packet = game_data_struct.GameTickPacket()
            self.update_live_data_packet(packet)
            if not packet.game_info.is_match_ended:
                spawn_ids = set()
                for k in range(0, self.start_match_configuration.num_players):
                    player_config = self.start_match_configuration.player_configuration[k]
                    if player_config.rlbot_controlled:
                        spawn_ids.add(player_config.spawn_id)

                for n in range(0, packet.num_cars):
                    try:
                        spawn_ids.remove(packet.game_cars[n].spawn_id)
                    except KeyError:
                        pass

                if len(spawn_ids) == 0:
                    self.logger.info('Packets are looking good, all spawn ids accounted for!')
                    return
                elif i > 4:
                    car_states = {}
                    for k in range(0, self.start_match_configuration.num_players):
                        player_info = packet.game_cars[k]
                        if player_info.spawn_id > 0:
                            car_states[k] = CarState(physics=Physics(velocity=Vector3(z=500)))
                    if len(car_states) > 0:
                        self.logger.info("Scooting bots out of the way to allow more to spawn!")
                        self.set_game_state(GameState(cars=car_states))

            time.sleep(0.5)
        self.logger.info('Gave up waiting for valid packet :(')

    def load_interface(self):
        self.game_status_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint)
        self.callback_func = self.game_status_callback_type(wrap_callback(self.game_status))
        self.game = ctypes.CDLL(self.dll_path)
        time.sleep(1)
        self.setup_function_types()

    def create_status_callback(self, callback=None):
        """
        Creates a callback for the rlbot status, uses default function if callback is none.
        :param callback:
        :return:
        """
        if callback is None:
            return self.callback_func

        def safe_wrapper(id, rlbotstatsus):
            callback(rlbotstatsus)

        return self.game_status_callback_type(wrap_callback(safe_wrapper))

    def set_extension(self, extension):
        self.game_status_callback_type(wrap_callback(self.game_status))
        self.extension = extension

    def update_player_input_flat(self, player_input_builder):
        buf = player_input_builder.Output()
        rlbot_status = self.game.UpdatePlayerInputFlatbuffer(bytes(buf), len(buf))
        self.game_status(None, rlbot_status, WARNING)

    def set_game_state(self, game_state: GameState) -> None:
        builder = flatbuffers.Builder(0)
        game_state_offset = game_state.convert_to_flat(builder)
        if game_state_offset is None:
            return  # There are no values to be set, so just skip it
        builder.Finish(game_state_offset)
        buf = builder.Output()
        rlbot_status = self.game.SetGameState(bytes(buf), len(buf))
        self.game_status(None, rlbot_status)

    def get_live_data_flat_binary(self):
        """
        Gets the live data packet in flatbuffer binary format. You'll need to do something like
        GameTickPacket.GetRootAsGameTickPacket(binary, 0) to get the data out.

        This is a temporary method designed to keep the integration test working. It returns the raw bytes
        of the flatbuffer so that it can be stored in a file. We can get rid of this once we have a first-class
        data recorder that lives inside the core dll.
        """
        byte_buffer = self.game.UpdateLiveDataPacketFlatbuffer()
        return self._process_live_flatbuffer(byte_buffer)

    def get_fresh_live_data_flat_binary(self, timeout_millis: int, key: int):
        """
        Gets the live data packet in flatbuffer binary format. You'll need to do something like
        GameTickPacket.GetRootAsGameTickPacket(binary, 0) to get the data out.
        This one blocks until a fresh frame is available, or until the timeout has elapsed.
        :param timeout_millis: will give up waiting for a fresh packet and just return a stale one
        after this number of milliseconds.
        :param key: answers the question "fresh from whose perspective?". Freshness will be
        tracked separately for whatever key you pass. Bot index is a reasonable choice.
        """
        byte_buffer = self.game.FreshLiveDataPacketFlatbuffer(timeout_millis, key)
        return self._process_live_flatbuffer(byte_buffer)

    def _process_live_flatbuffer(self, byte_buffer):
        if byte_buffer.size >= 4:  # GetRootAsGameTickPacket gets angry if the size is less than 4
            # We're counting on this copying the data over to a new memory location so that the original
            # pointer can be freed safely.
            proto_string = ctypes.string_at(byte_buffer.ptr, byte_buffer.size)
            self.game.Free(byte_buffer.ptr)  # Avoid a memory leak
            self.game_status(None, RLBotCoreStatus.Success)
            return proto_string

    def update_rigid_body_tick(self, rigid_body_tick: RigidBodyTick):
        """Get the most recent state of the physics engine."""
        rlbot_status = self.game.UpdateRigidBodyTick(rigid_body_tick)
        self.game_status(None, rlbot_status)
        return rigid_body_tick

    def get_field_info(self) -> FieldInfo:
        """
        Gets the field information from the interface.
        :return: The field information
        """
        byte_buffer = self.game.UpdateFieldInfoFlatbuffer()

        if byte_buffer.size >= 4:  # GetRootAsGameTickPacket gets angry if the size is less than 4
            # We're counting on this copying the data over to a new memory location so that the original
            # pointer can be freed safely.
            proto_string = ctypes.string_at(byte_buffer.ptr, byte_buffer.size)
            self.game.Free(byte_buffer.ptr)  # Avoid a memory leak
            self.game_status(None, RLBotCoreStatus.Success)
            return FieldInfo.GetRootAsFieldInfo(proto_string, 0)

    def update_ball_prediction(self, ball_prediction: BallPrediction):
        rlbot_status = self.game.GetBallPredictionStruct(ball_prediction)
        self.game_status(None, rlbot_status)
        return ball_prediction

    def get_ball_prediction(self) -> BallPredictionPacket:
        """
        Gets the latest ball prediction available in shared memory. Only works if BallPrediction.exe is running.
        """
        byte_buffer = self.game.GetBallPrediction()

        if byte_buffer.size >= 4:  # GetRootAsGameTickPacket gets angry if the size is less than 4
            # We're counting on this copying the data over to a new memory location so that the original
            # pointer can be freed safely.
            proto_string = ctypes.string_at(byte_buffer.ptr, byte_buffer.size)
            self.game.Free(byte_buffer.ptr)  # Avoid a memory leak
            self.game_status(None, RLBotCoreStatus.Success)
            return BallPredictionPacket.GetRootAsBallPrediction(proto_string, 0)

    def get_match_settings(self) -> MatchSettings:
        """
        Gets the current match settings in flatbuffer format. Useful for determining map, game mode, mutator settings,
        etc.
        """
        byte_buffer = self.game.GetMatchSettings()

        if byte_buffer.size >= 4:  # GetRootAsGameTickPacket gets angry if the size is less than 4
            # We're counting on this copying the data over to a new memory location so that the original
            # pointer can be freed safely.
            proto_string = ctypes.string_at(byte_buffer.ptr, byte_buffer.size)
            self.game.Free(byte_buffer.ptr)  # Avoid a memory leak
            self.game_status(None, RLBotCoreStatus.Success)
            return MatchSettingsPacket.GetRootAsMatchSettings(proto_string, 0)
