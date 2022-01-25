import psutil
import time

import re

import json
import os
import subprocess
import webbrowser
from pathlib import Path
from time import sleep
from typing import Optional, List, Union

from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.process_configuration import is_process_running


def launch_with_epic_simple(ideal_args: List[str]) -> bool:
    logger = get_logger(DEFAULT_LOGGER)
    try:
        # Try launch via Epic Games
        epic_exe_path = locate_epic_games_launcher_rocket_league_binary()
        if epic_exe_path is not None:
            exe_and_args = [str(epic_exe_path)] + ideal_args
            logger.info(f'Launching Rocket League with: {exe_and_args}')
            try:
                _ = subprocess.Popen(exe_and_args)
                return True
            except Exception as e:
                logger.info(f'Unable to launch via Epic due to: {e}')
    except:
        logger.debug('Unable to launch via Epic.')
    return False


def get_my_documents_folder() -> Path:
    """
    https://stackoverflow.com/a/30924555/280852
    """
    import ctypes.wintypes
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return Path(str(buf.value))


def get_rocket_league_log_path() -> Path:
    return get_my_documents_folder() / 'My Games' / 'Rocket League' / 'TAGame' / 'Logs' / 'Launch.log'


def args_contain_auth_info(args: List[str]) -> bool:
    return True in ["AUTH_LOGIN" in arg for arg in args]

def get_auth_args_from_process() -> Union[List[str], None]:
    rl_running, process = is_process_running('RocketLeague.exe', 'RocketLeague.exe', set())
    if rl_running:
        try:
            all_args = process.cmdline()
        except psutil.NoSuchProcess:
            return None
        if args_contain_auth_info(all_args):
            return all_args[1:]  # Snip off the executable arg
    return None

def get_auth_args_from_logs() -> Union[List[str], None]:
    # Log: Command line: -AUTH_LOGIN=unused -AUTH_PASSWORD=f7a32f56ea -AUTH_TYPE=exchangecode -epicapp=Sugar -epicenv=Prod -EpicPortal  -epicusername="tare-hart" -epicuserid=41276a00c2c54f -epiclocale=en -epicsandboxid=9773aa1aa54f4f
    rl_running, process = is_process_running('RocketLeague.exe', 'RocketLeague.exe', set())
    if rl_running:
        log_file = get_rocket_league_log_path()
        if log_file.exists():
            log_text = log_file.read_text()
            match = re.search("^Log: Command line: (.*)$", log_text, re.MULTILINE)
            if match is not None:
                args_str = match.group(1)
                all_args = args_str.split(' ')
                if args_contain_auth_info(all_args):
                    return all_args
    return None

def launch_with_epic_login_trick(ideal_args: List[str]) -> bool:
    """
    This needs to fail gracefully! Sometimes people only have the Steam version,
    so we want to be able to fall back to Steam if Epic is going nowhere.
    """
    try:
        logger = get_logger(DEFAULT_LOGGER)

        if not launch_with_epic_simple(ideal_args):
            return False

        process = None
        while True:
            sleep(1)
            rl_running, process = is_process_running('RocketLeague.exe', 'RocketLeague.exe', set())
            if rl_running:
                break
            logger.info("Waiting for RocketLeague.exe to start...")

        while True:
            all_args = get_auth_args_from_process()
            if all_args is not None:
                break
            all_args = get_auth_args_from_logs()
            if all_args is not None:
                break
            time.sleep(1)
            logger.info("Waiting for Rocket League args...")

        process.kill()
        modified_args = ideal_args + all_args
        logger.info(f"Killed old rocket league, reopening with {modified_args}")
        launch_with_epic_simple(modified_args)
        return True
    except Exception as ex:
        logger.warn(f"Trouble with epic launch: {ex}")
        return False


def locate_epic_games_launcher_rocket_league_binary() -> Optional[Path]:
    # Make sure we're on windows, this will go poorly otherwise
    try:
        import winreg
    except ImportError:
        return

    # List taken from https://docs.unrealengine.com/en-US/GettingStarted/Installation/MultipleLauncherInstalls/index.html
    possible_registry_locations = (
        (winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Epic Games\\EpicGamesLauncher'),
        (winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Epic Games\\EpicGamesLauncher'),
        (winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Epic Games\\EpicGamesLauncher'),
        (winreg.HKEY_CURRENT_USER, 'SOFTWARE\\WOW6432Node\\Epic Games\\EpicGamesLauncher')
    )

    def search_for_manifest_file(app_data_path: Path) -> Optional[Path]:
        # Loop through the files ending in *.item in app_data_path/Manifests
        # Parse them as JSON and locate the one where MandatoryAppFolderName is 'rocketleague'
        # Extract the binary location and return it.
        for file in app_data_path.glob("*.item"):
            with open(app_data_path / file, 'r') as f:
                try:
                    data = json.load(f)
                except Exception:
                    continue

            if data.get('MandatoryAppFolderName') == 'rocketleague':
                return data

    for possible_location in possible_registry_locations:
        try:
            # get the path to the launcher's game data stuff
            path = Path(winreg.QueryValueEx(winreg.OpenKey(possible_location[0], possible_location[1]), "AppDataPath")[0]) / 'Manifests'
        except Exception:
            # the path, or the key, might not exist
            # in this case, we'll just skip over it
            continue

        binary_data = search_for_manifest_file(path)

        if binary_data is not None:
            return Path(binary_data['InstallLocation']) / binary_data['LaunchExecutable']

    # Nothing found in registry? Try C:\ProgramData\Epic\EpicGamesLauncher
    # Or consider using %programdata%
    path = Path(os.getenv("programdata")) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"

    if os.path.isdir(path):
        binary_data = search_for_manifest_file(path)

        if binary_data is not None:
            return Path(binary_data['InstallLocation']) / binary_data['LaunchExecutable']
