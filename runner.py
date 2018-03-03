from utils.structures import bot_input_struct as bi, game_data_struct as gd
import bot_manager
import configparser
import ctypes
import mmap
import multiprocessing as mp
import msvcrt
from utils import rlbot_exception
import time
from utils.rlbot_config_parser import create_bot_config_layout, parse_configurations
import os
import sys
import subprocess

RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
INPUT_SHARED_MEMORY_TAG = 'Local\\RLBotInput'
OUTPUT_SHARED_MEMORY_TAG = 'Local\\RLBotOutput'

def run_agent(terminate_event, callback_event, config_file, name, team, index, module_name):
    bm = bot_manager.BotManager(terminate_event, callback_event, config_file, name, team,
                                index, module_name)
    bm.run()

def injectDLL():
    """
    Calling this function will inject the DLL without GUI
    DLL will return status codes from 0 to 5 which correspond to injector_codes
    DLL injection is only valid if codes are 0->'INJECTION_SUCCESSFUL' or 3->'RLBOT_DLL_ALREADY_INJECTED'
    It will print the output code and if it's not valid it will kill runner.py
    If RL isn't running the Injector will stay hidden waiting for RL to open and inject as soon as it does
    """
    # Inject DLL
    injector_dir = os.path.join(os.path.dirname(__file__), "RLBot_Injector.exe")
    incode=subprocess.call([injector_dir, 'hidden'])
    injector_codes=['INJECTION_SUCCESSFUL','INJECTION_FAILED','MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND','RLBOT_DLL_ALREADY_INJECTED','RLBOT_DLL_NOT_FOUND','MULTIPLE_RLBOT_DLL_FILES_FOUND']
    injector_valid_codes=['INJECTION_SUCCESSFUL','RLBOT_DLL_ALREADY_INJECTED']
    injection_status=injector_codes[incode]
    print(injection_status)
    if injection_status in injector_valid_codes:
        return injection_status
    else:
        sys.exit()


def main(framework_config=None, bot_configs=None):
    if bot_configs is None:
        bot_configs = {}
    callbacks = []
    # Inject DLL
    injectDLL()

    # Set up RLBot.cfg
    if framework_config is None:
        raw_config_parser = configparser.RawConfigParser()
        raw_config_parser.read(RLBOT_CONFIG_FILE)

        framework_config = create_bot_config_layout()
        framework_config.parse_file(raw_config_parser, max_index=10)

    # Open anonymous shared memory for entire GameInputPacket and map buffer
    buff = mmap.mmap(-1, ctypes.sizeof(bi.GameInputPacket), INPUT_SHARED_MEMORY_TAG)
    gameInputPacket = bi.GameInputPacket.from_buffer(buff)

    num_participants, names, teams, modules, parameters = parse_configurations(gameInputPacket,
                                                                               framework_config, bot_configs)

    # Create Quit event
    quit_event = mp.Event()

    # Launch processes
    for i in range(num_participants):
        if gameInputPacket.sPlayerConfiguration[i].bRLBotControlled:
            callback = mp.Event()
            callbacks.append(callback)
            process = mp.Process(target=run_agent,
                                 args=(quit_event, callback, parameters[i],
                                       str(gameInputPacket.sPlayerConfiguration[i].wName),
                                       teams[i], i, modules[i]))
            process.start()

    print("Successfully configured bots. Setting flag for injected dll.")
    gameInputPacket.bStartMatch = True

    # Wait 100 milliseconds then check for an error code
    time.sleep(0.1)
    game_data_shared_memory = mmap.mmap(-1, ctypes.sizeof(gd.GameTickPacketWithLock), OUTPUT_SHARED_MEMORY_TAG)
    bot_output = gd.GameTickPacketWithLock.from_buffer(game_data_shared_memory)
    if not bot_output.iLastError == 0:
        # Terminate all process and then raise an exception
        quit_event.set()
        terminated = False
        while not terminated:
            terminated = True
            for callback in callbacks:
                if not callback.is_set():
                    terminated = False
        raise rlbot_exception.RLBotException().raise_exception_from_error_code(bot_output.iLastError)

    print("Press any character to exit")
    msvcrt.getch()

    print("Shutting Down")
    quit_event.set()
    # Wait for all processes to terminate before terminating main process
    terminated = False
    while not terminated:
        terminated = True
        for callback in callbacks:
            if not callback.is_set():
                terminated = False


if __name__ == '__main__':
    main()
