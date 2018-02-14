import bot_input_struct as bi
import bot_manager
import configparser
import ctypes
import game_data_struct as gd
import mmap
import multiprocessing as mp
import msvcrt
import rlbot_exception
import time
from utils.rlbot_config_parser import create_bot_config_parser, parse_configurations

RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
INPUT_SHARED_MEMORY_TAG = 'Local\\RLBotInput'
OUTPUT_SHARED_MEMORY_TAG = 'Local\\RLBotOutput'

def run_agent(terminate_event, callback_event, config_file, name, team, index, module_name):
    bm = bot_manager.BotManager(terminate_event, callback_event, config_file, name, team,
                                index, module_name)
    bm.run()


def main():
    callbacks = []
    # Set up RLBot.cfg
    framework_config = configparser.RawConfigParser()
    framework_config.read(RLBOT_CONFIG_FILE)

    config_parser = create_bot_config_parser()
    config_parser.parse_file(framework_config, max_index=10)

    # Open anonymous shared memory for entire GameInputPacket and map buffer
    buff = mmap.mmap(-1, ctypes.sizeof(bi.GameInputPacket), INPUT_SHARED_MEMORY_TAG)
    gameInputPacket = bi.GameInputPacket.from_buffer(buff)

    num_participants, names, teams, modules, parameters = parse_configurations(gameInputPacket, config_parser)

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
