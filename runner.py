import bot_input_struct as bi
import bot_manager
import configparser
import ctypes
import game_data_struct as gd
import mmap
import multiprocessing as mp
import queue
import msvcrt
import rlbot_exception
import time
import os
import sys
import subprocess

# These packages enhance RLBot but they are not critical to its proper functioning.
# We have a lot of users who don't have these extra packages installed and we don't want to break them unexpectedly.
# We also have some setup instructions that will take some time to update.
# Until we get all of that up to speed, we will work around any missing optional packages and print warning messages.
optional_packages_installed = False
try:
    import psutil
    optional_packages_installed = True
except ImportError:
    pass

PARTICPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICPANT_BOT_KEY_PREFIX = 'participant_is_bot_'
PARTICPANT_RLBOT_KEY_PREFIX = 'participant_is_rlbot_controlled_'
PARTICPANT_CONFIG_KEY_PREFIX = 'participant_config_'
PARTICPANT_BOT_SKILL_KEY_PREFIX = 'participant_bot_skill_'
PARTICPANT_TEAM_PREFIX = 'participant_team_'
RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
INPUT_SHARED_MEMORY_TAG = 'Local\\RLBotInput'
OUTPUT_SHARED_MEMORY_TAG = 'Local\\RLBotOutput'
BOT_CONFIG_LOADOUT_HEADER = 'Participant Loadout'
BOT_CONFIG_LOADOUT_ORANGE_HEADER = 'Participant Loadout Orange'
BOT_CONFIG_MODULE_HEADER = 'Bot Location'
BOT_CONFIG_AGENT_HEADER = 'Bot Parameters'


def get_bot_config_file_list(botCount, config):
    config_file_list = []
    for i in range(botCount):
        config_file_list.append(config.get(PARTICPANT_CONFIGURATION_HEADER, PARTICPANT_CONFIG_KEY_PREFIX + str(i)))
    return config_file_list


# Cut off at 31 characters and handle duplicates
def get_sanitized_bot_name(dict, name):
    if name not in dict:
        new_name = name[:31]  # Make sure name does not exceed 31 characters
        dict[name] = 1
    else:
        count = dict[name]
        new_name = name[:27] + "(" + str(count + 1) + ")"  # Truncate at 27 because we can have up to '(10)' appended
        dict[name] = count + 1

    return new_name


def get_file_path(modulename):
    # Converting a module name to a file path, e.g. mybot.util -> mybot\util.py.
    # We're doing it this way to be backwards-compatible with existing bot configs.
    return str(modulename).replace(".", "\\") + ".py"


def run_agent(terminate_event, callback_event, config_file, name, team, index, module_path, agent_telemetry_queue):
    bm = bot_manager.BotManager(terminate_event, callback_event, config_file, name, team,
                                index, module_path, agent_telemetry_queue)
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
    incode = subprocess.call([injector_dir, 'hidden'])
    injector_codes = ['INJECTION_SUCCESSFUL', 'INJECTION_FAILED', 'MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND',
                      'RLBOT_DLL_ALREADY_INJECTED', 'RLBOT_DLL_NOT_FOUND', 'MULTIPLE_RLBOT_DLL_FILES_FOUND']
    injector_valid_codes = ['INJECTION_SUCCESSFUL', 'RLBOT_DLL_ALREADY_INJECTED']
    injection_status = injector_codes[incode]
    print(injection_status)
    if injection_status in injector_valid_codes:
        return injection_status
    else:
        sys.exit()


def main():
    if not optional_packages_installed:
        print("\n#### WARNING ####\nYou are missing some optional packages which will become mandatory in the future!\n"
              "Please run `pip install -r requirements.txt` to enjoy optimal functionality and future-proof yourself!\n")

    injectDLL()

    # Set up RLBot.cfg
    framework_config = configparser.RawConfigParser()
    framework_config.read(RLBOT_CONFIG_FILE)

    # Open anonymous shared memory for entire GameInputPacket and map buffer
    buff = mmap.mmap(-1, ctypes.sizeof(bi.GameInputPacket), INPUT_SHARED_MEMORY_TAG)
    gameInputPacket = bi.GameInputPacket.from_buffer(buff)

    # Determine number of participants
    num_participants = framework_config.getint(RLBOT_CONFIGURATION_HEADER, 'num_participants')

    # Retrieve bot config files
    participant_configs = get_bot_config_file_list(num_participants, framework_config)

    # Create empty lists
    bot_names = []
    bot_teams = []
    bot_module_paths = []
    processes = []
    callbacks = []
    bot_parameter_list = []
    name_dict = dict()

    gameInputPacket.iNumPlayers = num_participants

    # Set configuration values for bots and store name and team
    for i in range(num_participants):
        bot_config_path = participant_configs[i]
        bot_config = configparser.RawConfigParser()
        bot_config.read(bot_config_path)

        team_num = framework_config.getint(PARTICPANT_CONFIGURATION_HEADER,
                                           PARTICPANT_TEAM_PREFIX + str(i))

        loadout_header = BOT_CONFIG_LOADOUT_HEADER
        if (team_num == 1 and bot_config.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER)):
            loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

        gameInputPacket.sPlayerConfiguration[i].bBot = framework_config.getboolean(PARTICPANT_CONFIGURATION_HEADER,
                                                                                   PARTICPANT_BOT_KEY_PREFIX + str(i))
        gameInputPacket.sPlayerConfiguration[i].bRLBotControlled = framework_config.getboolean(
            PARTICPANT_CONFIGURATION_HEADER,
            PARTICPANT_RLBOT_KEY_PREFIX + str(i))
        gameInputPacket.sPlayerConfiguration[i].fBotSkill = framework_config.getfloat(PARTICPANT_CONFIGURATION_HEADER,
                                                                                      PARTICPANT_BOT_SKILL_KEY_PREFIX
                                                                                      + str(i))
        gameInputPacket.sPlayerConfiguration[i].iPlayerIndex = i

        gameInputPacket.sPlayerConfiguration[i].wName = get_sanitized_bot_name(name_dict,
                                                                               bot_config.get(loadout_header, 'name'))
        gameInputPacket.sPlayerConfiguration[i].ucTeam = team_num
        gameInputPacket.sPlayerConfiguration[i].ucTeamColorID = bot_config.getint(loadout_header,
                                                                                  'team_color_id')
        gameInputPacket.sPlayerConfiguration[i].ucCustomColorID = bot_config.getint(loadout_header,
                                                                                    'custom_color_id')
        gameInputPacket.sPlayerConfiguration[i].iCarID = bot_config.getint(loadout_header, 'car_id')
        gameInputPacket.sPlayerConfiguration[i].iDecalID = bot_config.getint(loadout_header, 'decal_id')
        gameInputPacket.sPlayerConfiguration[i].iWheelsID = bot_config.getint(loadout_header, 'wheels_id')
        gameInputPacket.sPlayerConfiguration[i].iBoostID = bot_config.getint(loadout_header, 'boost_id')
        gameInputPacket.sPlayerConfiguration[i].iAntennaID = bot_config.getint(loadout_header, 'antenna_id')
        gameInputPacket.sPlayerConfiguration[i].iHatID = bot_config.getint(loadout_header, 'hat_id')
        gameInputPacket.sPlayerConfiguration[i].iPaintFinish1ID = bot_config.getint(loadout_header,
                                                                                    'paint_finish_1_id')
        gameInputPacket.sPlayerConfiguration[i].iPaintFinish2ID = bot_config.getint(loadout_header,
                                                                                    'paint_finish_2_id')
        gameInputPacket.sPlayerConfiguration[i].iEngineAudioID = bot_config.getint(loadout_header,
                                                                                   'engine_audio_id')
        gameInputPacket.sPlayerConfiguration[i].iTrailsID = bot_config.getint(loadout_header, 'trails_id')
        gameInputPacket.sPlayerConfiguration[i].iGoalExplosionID = bot_config.getint(loadout_header,
                                                                                     'goal_explosion_id')
        if bot_config.has_section(BOT_CONFIG_AGENT_HEADER):
            bot_parameter_list.append(bot_config[BOT_CONFIG_AGENT_HEADER])
        else:
            bot_parameter_list.append(None)

        bot_names.append(bot_config.get(loadout_header, 'name'))
        bot_teams.append(framework_config.getint(PARTICPANT_CONFIGURATION_HEADER, PARTICPANT_TEAM_PREFIX + str(i)))
        if gameInputPacket.sPlayerConfiguration[i].bRLBotControlled:
            module_name = bot_config.get(BOT_CONFIG_MODULE_HEADER, 'agent_module')
            module_path = os.path.join(os.path.dirname(bot_config_path), get_file_path(module_name))
            bot_module_paths.append(module_path)
        else:
            bot_module_paths.append('NO_MODULE_FOR_PARTICIPANT')

    # Create Quit event
    quit_event = mp.Event()

    agent_metadata_map = {}
    agent_metadata_queue = mp.Queue()

    # Launch processes
    for i in range(num_participants):
        if gameInputPacket.sPlayerConfiguration[i].bRLBotControlled:
            callback = mp.Event()
            callbacks.append(callback)
            process = mp.Process(target=run_agent,
                                 args=(quit_event, callback, bot_parameter_list[i],
                                       str(gameInputPacket.sPlayerConfiguration[i].wName),
                                       bot_teams[i], i, bot_module_paths[i], agent_metadata_queue))
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
    while True:
        if msvcrt.kbhit():
            msvcrt.getch()
            break
        try:
            single_agent_metadata = agent_metadata_queue.get(timeout=1)
            agent_metadata_map[single_agent_metadata['index']] = single_agent_metadata
            configure_processes(agent_metadata_map)
        except queue.Empty:
            pass
        except Exception as ex:
            print(ex)
            pass

    print("Shutting Down")
    quit_event.set()
    # Wait for all processes to terminate before terminating main process
    terminated = False
    while not terminated:
        terminated = True
        for callback in callbacks:
            if not callback.is_set():
                terminated = False


def configure_processes(agent_metadata_map):
    """
    This will update the priority and CPU affinity of the processes owned by bots to try to achieve fairness and
    good performance.

    :param agent_metadata_map: A mapping of player index to agent metadata, including a list of owned process ids.
    """

    if not optional_packages_installed:
        return

    team_pids_map = {}

    for player_index, data in agent_metadata_map.items():
        team = data['team']
        if team not in team_pids_map:
            team_pids_map[team] = set()
        team_pids_map[team].update(data['pids'])

    shared_pids = set()
    cpu_count = psutil.cpu_count()
    cpus_per_team = cpu_count // 3

    if len(team_pids_map) >= 2 and cpus_per_team > 0:
        # Sort into three sets of pids: team 0 exclusives, team 1 exclusives, and shared pids
        # All pids will be assigned high priority
        # Team exclusive pids will be bound to a subset of cpus so they can't adversely affect the opposite team.

        for team, team_set in team_pids_map.items():
            if not shared_pids:
                shared_pids.update(team_set)
            else:
                shared_pids.intersection_update(team_set)

        for team, team_set in team_pids_map.items():
            team_set -= shared_pids

        for team, team_pids in team_pids_map.items():
            team_cpu_offset = cpus_per_team * team
            team_cpus = list(range(cpu_count - cpus_per_team - team_cpu_offset, cpu_count - team_cpu_offset))
            for pid in team_pids:
                p = psutil.Process(pid)
                p.cpu_affinity(team_cpus)  # Restrict the process to run on the cpus assigned to the team
                p.nice(psutil.HIGH_PRIORITY_CLASS)  # Allow the process to run at high priority
    else:
        # Consider everything a shared pid, because we are not in a position to split up cpus.
        for team, team_set in team_pids_map.items():
            shared_pids.update(team_set)

    for pid in shared_pids:
        p = psutil.Process(pid)  # Allow the process to run at high priority
        p.nice(psutil.HIGH_PRIORITY_CLASS)


if __name__ == '__main__':
    main()
