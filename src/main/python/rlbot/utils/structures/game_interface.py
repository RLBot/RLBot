import ctypes
import os
import subprocess
import sys
import time

from rlbot.messages.flat.BallPrediction import BallPrediction as BallPredictionPacket
from rlbot.messages.flat.FieldInfo import FieldInfo
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.file_util import get_python_root
from rlbot.utils.rlbot_exception import get_exception_from_error_code
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import GameTickPacket, ByteBuffer, FieldInfoPacket
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_status import RLBotCoreStatus
from rlbot.utils.structures.start_match_structures import MatchSettings
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick


def wrap_callback(callback_func):
    def caller(id, status):
        callback_func(id, status)

    return caller


def get_dll_location():
    return os.path.join(get_dll_directory(), 'RLBot_Core_Interface.dll')

def get_dll_32_location():
    return os.path.join(get_dll_directory(), 'RLBot_Core_Interface_32.dll')


def is_32_bit_python():
    return sys.maxsize <= 2**32


def get_dll_directory():
    return os.path.join(get_python_root(), 'rlbot', 'dll')


class GameInterface:
    game = None
    participants = None
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
        func.argtypes = [MatchSettings, self.game_status_callback_type, ctypes.c_void_p]
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

        # set game state
        func = self.game.SetGameState
        func.argtypes = [ctypes.c_void_p, ctypes.c_int]
        func.restype = ctypes.c_int

        self.renderer.setup_function_types(self.game)
        self.logger.debug('game interface functions are setup')

        # free the memory at the given pointer
        func = self.game.Free
        func.argtypes = [ctypes.c_void_p]

    def update_live_data_packet(self, game_tick_packet: GameTickPacket):
        rlbot_status = self.game.UpdateLiveDataPacket(game_tick_packet)
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
        rlbot_status = self.game.StartMatch(self.start_match_configuration,
                                            self.create_status_callback(
                                                None if self.extension is None else self.extension.onMatchStart), None)

        if rlbot_status != 0:
            exception_class = get_exception_from_error_code(rlbot_status)
            raise exception_class()

        self.logger.debug('Starting match with status: %s', RLBotCoreStatus.status_list[rlbot_status])

    def update_player_input(self, player_input, index):
        rlbot_status = self.game.UpdatePlayerInput(player_input, index)
        self.game_status(None, rlbot_status)

    def send_chat(self, index, team_only, message_details):
        rlbot_status = self.game.SendChat(message_details, index, team_only, self.create_status_callback(), None)
        self.game_status(None, rlbot_status)

    def send_chat_flat(self, chat_message_builder):
        buf = chat_message_builder.Output()
        rlbot_status = self.game.SendQuickChat(bytes(buf), len(buf))
        self.game_status(None, rlbot_status)
        return rlbot_status

    def create_callback(self):
        return

    def game_status(self, id, rlbot_status):
        if rlbot_status != RLBotCoreStatus.Success and rlbot_status != RLBotCoreStatus.BufferOverfilled:
            self.logger.debug("bad status %s", RLBotCoreStatus.status_list[rlbot_status])

    def wait_until_loaded(self):
        self.game.IsInitialized.restype = ctypes.c_bool
        is_loaded = self.game.IsInitialized()
        if is_loaded:
            self.logger.debug('DLL is loaded!')
        if not is_loaded:
            time.sleep(1)
            self.wait_until_loaded()

    def load_interface(self):
        self.game_status_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint)
        self.callback_func = self.game_status_callback_type(wrap_callback(self.game_status))
        self.game = ctypes.CDLL(self.dll_path)
        time.sleep(1)
        self.setup_function_types()

    def inject_dll(self):
        """
        Calling this function will inject the DLL without GUI
        DLL will return status codes from 0 to 5 which correspond to injector_codes
        DLL injection is only valid if codes are 0->'INJECTION_SUCCESSFUL' or 3->'RLBOT_DLL_ALREADY_INJECTED'
        It will print the output code and if it's not valid it will kill runner.py
        If RL isn't running the Injector will stay hidden waiting for RL to open and inject as soon as it does
        """

        self.logger.info('Injecting DLL')
        # Inject DLL
        injector_dir = os.path.join(get_dll_directory(), 'RLBot_Injector.exe')

        for file in ['RLBot_Injector.exe', 'RLBot_Core.dll', 'RLBot_Core_Interface.dll', 'RLBot_Core_Interface_32.dll']:
            file_path = os.path.join(get_dll_directory(), file)
            if not os.path.isfile(file_path):
                raise FileNotFoundError('{} was not found in {}. '
                                        'Please check that the file exists and your antivirus '
                                        'is not removing it.'.format(file, get_dll_directory()))

        incode = subprocess.call([injector_dir, 'hidden'])
        injector_codes = ['INJECTION_SUCCESSFUL',
                          'INJECTION_FAILED',
                          'MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND',
                          'RLBOT_DLL_ALREADY_INJECTED',
                          'RLBOT_DLL_NOT_FOUND',
                          'MULTIPLE_RLBOT_DLL_FILES_FOUND']
        injector_valid_codes = ['INJECTION_SUCCESSFUL',
                                'RLBOT_DLL_ALREADY_INJECTED']
        injection_status = injector_codes[incode]
        if injection_status in injector_valid_codes:
            self.logger.info('Finished Injecting DLL')
            if injection_status == 'INJECTION_SUCCESSFUL':
                # We need to wait for the injections to be finished
                self.countdown(20)
            return injection_status
        else:
            self.logger.error('Failed to inject DLL: ' + injection_status)
            sys.exit()

    def countdown(self, countdown_timer):
        self.logger.info("Waiting {} seconds for DLL to load".format(countdown_timer))
        for i in range(countdown_timer):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        print('')

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
        self.game_status(None, rlbot_status)

    def set_game_state(self, set_state_builder):
        buf = set_state_builder.Output()
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
