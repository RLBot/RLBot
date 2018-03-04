import ctypes

import os
import subprocess
import sys

from utils.agent_creator import get_base_repo_path
from utils.structures.bot_input_struct import get_player_input_list_type
import time

from utils.structures.game_status import RLBotCoreStatus


def countdown(countdown_timer):
    for i in range(countdown_timer):
        print(countdown_timer - i)
        time.sleep(1)


def injectDLL():
    """
    Calling this function will inject the DLL without GUI
    DLL will return status codes from 0 to 5 which correspond to injector_codes
    DLL injection is only valid if codes are 0->'INJECTION_SUCCESSFUL' or 3->'RLBOT_DLL_ALREADY_INJECTED'
    It will print the output code and if it's not valid it will kill runner.py
    If RL isn't running the Injector will stay hidden waiting for RL to open and inject as soon as it does
    """
    print('Injecting DLL')
    # Inject DLL
    injector_dir = os.path.join(get_base_repo_path(), "RLBot_Injector.exe")
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
    print(injection_status)
    if injection_status in injector_valid_codes:
        if injection_status == 'INJECTION_SUCCESSFUL':
            # We need to wait for the injections to be finished
            countdown(11)
        return injection_status
    else:
        print(injection_status)
        sys.exit()


class GameInterface:

    status_callback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)

    def __init__(self, game_input_packet, participants):
        self.participants = participants
        self.game_input_packet = game_input_packet
        dll_path = get_base_repo_path() + '\\RLBot_Core_Interface.dll'
        self.game = ctypes.WinDLL(dll_path)
        # wait for the dll to load
        time.sleep(1)
        self.rlbot_status_callback = self.status_callback(self.game_status)

    def update_live_data_packet(self):
        pass

    def update_match_data_packet(self):
        pass

    def start_match(self):

        # self.game_input_packet.bStartMatch = True
        func = self.game.StartMatch
        list_of_10 = get_player_input_list_type()
        func.argtypes = [list_of_10, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
        func.restype = ctypes.c_int
        rlbot_status = self.game.StartMatch(self.game_input_packet.sPlayerConfiguration, self.participants,
                             self.rlbot_status_callback, None)

        print(RLBotCoreStatus.status_list[rlbot_status])

    def update_player_input(self):
        pass

    def send_chat(self):
        pass

    def create_callback(self):
        return

    def game_status(self, rlbot_status):
        print(RLBotCoreStatus.status_list[rlbot_status])
