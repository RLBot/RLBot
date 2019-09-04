import os
import platform
import socket
import subprocess

import psutil

from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.structures.game_interface import get_dll_directory

# Generated randomly by Kipje13, and confirmed to have no conflict with any common programs
# https://www.adminsub.net/tcp-udp-port-finder/23233
IDEAL_RLBOT_PORT = 23233

# This is the port that Rocket League will use by default if we cannot override it.
DEFAULT_RLBOT_PORT = 50000

if platform.system() == 'Windows':
    executable_name = 'RLBot.exe'
elif platform.system() == 'Linux':
    executable_name = 'RLBot'

def launch():
    port = DEFAULT_RLBOT_PORT
    try:
        desired_port = find_usable_port()
        port = desired_port
    except Exception as e:
        print(str(e))

    print("Launching RLBot.exe...")
    path = os.path.join(get_dll_directory(), executable_name)
    if os.access(path, os.X_OK):
        return subprocess.Popen([path, str(port)], shell=True), port
    if os.access(path, os.F_OK):
        raise PermissionError('Unable to execute RLBot.exe due to file permissions! Is your antivirus messing you up? '
                              f'Check https://github.com/RLBot/RLBot/wiki/Antivirus-Notes. The exact path is {path}')
    raise FileNotFoundError(f'Unable to find RLBot.exe at {path}! Is your antivirus messing you up? Check '
                            'https://github.com/RLBot/RLBot/wiki/Antivirus-Notes.')


def find_existing_process():
    logger = get_logger(DEFAULT_LOGGER)
    for proc in psutil.process_iter():
        try:
            if proc.name() == "RLBot.exe":
                if len(proc.cmdline()) > 1:
                    port = int(proc.cmdline()[1])
                    return proc, port
                logger.error(f"Failed to find the RLBot port being used in the process args! Guessing "
                             f"{DEFAULT_RLBOT_PORT}.")
                return proc, DEFAULT_RLBOT_PORT
        except Exception as e:
            logger.error(f"Failed to read the name of a process while hunting for RLBot.exe: {e}")
    return None, None


def find_usable_port():
    for port_to_test in range(IDEAL_RLBOT_PORT, 65535):
        if is_port_accessible(port_to_test):
            return port_to_test
    raise PermissionError('Unable to find a usable port for running RLBot! Is your antivirus messing you up? '
                          'Check https://github.com/RLBot/RLBot/wiki/Antivirus-Notes')


def is_port_accessible(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('127.0.0.1', port))
            return True
        except:
            return False
