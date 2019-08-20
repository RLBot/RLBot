import fileinput
import os
import socket
import subprocess
import sys

from rlbot.utils.structures.game_interface import get_dll_directory

# Generated randomly by Kipje13, and confirmed to have no conflict with any common programs
# https://www.adminsub.net/tcp-udp-port-finder/23233
IDEAL_RLBOT_PORT = 23233

# This is the port that Rocket League will use by default if we cannot override it.
DEFAULT_RLBOT_PORT = 50000


def launch():
    port = DEFAULT_RLBOT_PORT
    try:
        rlbot_ini = find_rlbot_ini()
        if rlbot_ini is not None:
            desired_port = find_usable_port()
            # TODO: instead of manipulating the ini, start Rocket League with special args once they become available.
            write_port_to_ini(desired_port, rlbot_ini)
            port = desired_port
    except Exception as e:
        print(str(e))

    print("Launching RLBot.exe...")
    path = os.path.join(get_dll_directory(), "RLBot.exe")
    if os.access(path, os.X_OK):
        return subprocess.Popen([path, str(port)])
    if os.access(path, os.F_OK):
        raise PermissionError('Unable to execute RLBot.exe due to file permissions! Is your antivirus messing you up? '
                              f'Check https://github.com/RLBot/RLBot/wiki/Antivirus-Notes. The exact path is {path}')
    raise FileNotFoundError(f'Unable to find RLBot.exe at {path}! Is your antivirus messing you up? Check '
                            'https://github.com/RLBot/RLBot/wiki/Antivirus-Notes.')


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


def find_rlbot_ini():
    for games_folder in ['~/Documents/My Games', '~/OneDrive/Documents/My Games']:
        path_to_test = os.path.expanduser(f'{games_folder}/Rocket League/TAGame/Config/TARLBot.ini')
        if os.access(path_to_test, os.F_OK):
            return path_to_test
    return None


def write_port_to_ini(port, ini_path):
    print(f"Setting port in RLBot ini file at {ini_path} to {port}")
    replace_all(ini_path, 'ControllerURL=', f'ControllerURL=127.0.0.1:{port}\n')


def replace_all(file, prefix, replacement):
    for line in fileinput.input(file, inplace=1):
        if line.startswith(prefix):
            line = replacement
        sys.stdout.write(line)
