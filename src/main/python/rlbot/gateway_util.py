import os
import platform
import socket
import stat
import subprocess
from dataclasses import dataclass
from enum import IntEnum

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
elif platform.system() == 'Darwin':
    executable_name = 'RLBot_mac'


class NetworkingRole(IntEnum):
    none = 0
    lan_client = 1
    remote_rlbot_server = 2
    remote_rlbot_client = 3


@dataclass
class LaunchOptions:
    networking_role: NetworkingRole = NetworkingRole.none
    remote_address: str = '127.0.0.1'


def launch(launch_options: LaunchOptions = None):
    port = DEFAULT_RLBOT_PORT
    try:
        desired_port = find_usable_port()
        port = desired_port
    except Exception as e:
        print(str(e))

    path = os.path.join(get_dll_directory(), executable_name)
    if not os.access(path, os.F_OK):
        raise FileNotFoundError(f'Unable to find RLBot binary at {path}! Is your antivirus messing you up? Check '
                            'https://github.com/RLBot/RLBot/wiki/Antivirus-Notes.')
    if not os.access(path, os.X_OK):
        os.chmod(path, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not os.access(path, os.X_OK):
        raise PermissionError('Unable to execute RLBot binary due to file permissions! Is your antivirus messing you up? '
                              f'Check https://github.com/RLBot/RLBot/wiki/Antivirus-Notes. The exact path is {path}')

    args = [path, str(port)]
    if launch_options is not None:
        args.append(launch_options.remote_address)
        args.append(str(int(launch_options.networking_role)))
    print(f"Launching RLBot binary with args {args}")
    if platform.system() != 'Windows':
        # Unix only works this way, not sure why. Windows works better with the array, guards against spaces in path.
        args = ' '.join(args)
    return subprocess.Popen(args, shell=True, cwd=get_dll_directory()), port


def find_existing_process():
    logger = get_logger(DEFAULT_LOGGER)
    for proc in psutil.process_iter():
        try:
            if proc.name() == executable_name:
                if len(proc.cmdline()) > 1:
                    port = int(proc.cmdline()[1])
                    return proc, port
                logger.error(f"Failed to find the RLBot port being used in the process args! Guessing "
                             f"{IDEAL_RLBOT_PORT}.")
                return proc, IDEAL_RLBOT_PORT
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
