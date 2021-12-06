import time

import re

import json
import os
import subprocess
import webbrowser
from pathlib import Path
from time import sleep
from typing import Optional, List

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


def launch_with_epic_login_trick(ideal_args: List[str]) -> bool:
    try:
        logger = get_logger(DEFAULT_LOGGER)

        launch_with_epic_simple(ideal_args)
        time_limit = 20
        process = None
        for i in range(time_limit):
            sleep(1)
            rl_running, process = is_process_running('RocketLeague.exe', 'RocketLeague.exe', set())
            if rl_running:
                break

        if process is None:
            logger.warn(f"Rocket League didn't open within {time_limit} seconds.")
            return False

        for _ in range(60):
            log_file = get_rocket_league_log_path()
            log_text = log_file.read_text()
            match = re.search("^Log: Command line: (.*)$", log_text, re.MULTILINE)
            if match is not None:
                break
            time.sleep(1)

        if match is not None:
            args_str = match.group(1)
            all_args = args_str.split(' ')
            rl_running, process = is_process_running('RocketLeague.exe', 'RocketLeague.exe', set())
            process.kill()
            modified_args = ideal_args + all_args
            logger.info(f"Killed old rocket league, reopening with {modified_args}")
            launch_with_epic_simple(modified_args)
            subprocess.Popen(all_args, shell=True)
            return True
        logger.warn(f"Was not  able to find command line args in the log file!")
        return False
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
