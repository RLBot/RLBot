from __future__ import print_function
import ctypes
import logging

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


class GameInterface:

    game = None
    participants = None
    game_input_packet = None
    status_callback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)

    def __init__(self):
        self.logger = logging.getLogger('rlbot')
        self.dll_path = os.path.join(get_base_repo_path(), 'RLBot_Core_Interface.dll')
        # wait for the dll to load
        self.rlbot_status_callback = self.status_callback(self.game_status)

    def update_live_data_packet(self):
        pass

    def update_match_data_packet(self):
        pass

    def start_match(self):
        self.wait_until_loaded()

        # self.game_input_packet.bStartMatch = True
        func = self.game.StartMatch
        list_of_10 = get_player_input_list_type()
        func.argtypes = [list_of_10, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
        func.restype = ctypes.c_int
        rlbot_status = self.game.StartMatch(self.game_input_packet.sPlayerConfiguration, self.participants,
                             self.rlbot_status_callback, None)

        self.logger.debug(RLBotCoreStatus.status_list[rlbot_status])

    def update_player_input(self):
        pass

    def send_chat(self):
        pass

    def create_callback(self):
        return

    def game_status(self, rlbot_status):
        self.logger.info(RLBotCoreStatus.status_list[rlbot_status])

    def wait_until_loaded(self):
        self.game.IsInitialized.restype = ctypes.c_bool
        is_loaded = self.game.IsInitialized()
        self.logger.debug('dll is loaded', is_loaded)
        if not is_loaded:
            time.sleep(1)
            self.wait_until_loaded()

    def load_interface(self):
        self.game = ctypes.WinDLL(self.dll_path)
        time.sleep(1)

    def inject_dll(self):
        """
        Calling this function will inject the DLL without GUI
        DLL will return status codes from 0 to 5 which correspond to injector_codes
        DLL injection is only valid if codes are 0->'INJECTION_SUCCESSFUL' or 3->'RLBOT_DLL_ALREADY_INJECTED'
        It will print the output code and if it's not valid it will kill runner.py
        If RL isn't running the Injector will stay hidden waiting for RL to open and inject as soon as it does
        """

        self.logger.debug('Injecting DLL')
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
        if injection_status in injector_valid_codes:
            self.logger.debug('Finished Injecting DLL')
            if injection_status == 'INJECTION_SUCCESSFUL':
                # We need to wait for the injections to be finished
                #countdown(11)
                pass
            return injection_status
        else:
            self.logger.error('Failed to inject DLL: ' + injection_status)
            sys.exit()
