import logging

from RLBotFramework.utils.structures import bot_input_struct as bi
import bot_manager
import configparser
import multiprocessing as mp
import queue
import msvcrt
from RLBotFramework.utils.rlbot_config_parser import create_bot_config_layout, parse_configurations

# These packages enhance RLBot but they are not critical to its proper functioning.
# We have a lot of users who don't have these extra packages installed and we don't want to break them unexpectedly.
# We also have some setup instructions that will take some time to update.
# Until we get all of that up to speed, we will work around any missing optional packages and print warning messages.
from RLBotFramework.utils.structures.game_interface import GameInterface

optional_packages_installed = False
try:
    import psutil
    optional_packages_installed = True
except ImportError:
    pass

RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


def main(framework_config=None, bot_configs=None):
    logger = logging.getLogger('rlbot')
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.INFO)
    logger.debug('reading the configs')
    if bot_configs is None:
        bot_configs = {}
    callbacks = []
    # Inject DLL
    game_interface = GameInterface()
    game_interface.inject_dll()

    if not optional_packages_installed:
        logger.warning("\n#### WARNING ####\nYou are missing some optional packages which will become mandatory in the future!\n"
              "Please run `pip install -r requirements.txt` to enjoy optimal functionality and future-proof yourself!\n")

    # Set up RLBot.cfg
    if framework_config is None:
        raw_config_parser = configparser.RawConfigParser()
        raw_config_parser.read(RLBOT_CONFIG_FILE)

        framework_config = create_bot_config_layout()
        framework_config.parse_file(raw_config_parser, max_index=10)

    # Open anonymous shared memory for entire GameInputPacket and map buffer
    gameInputPacket = bi.GameInputPacket()

    num_participants, names, teams, modules, parameters = parse_configurations(gameInputPacket,
                                                                               framework_config, bot_configs)

    game_interface.load_interface()

    game_interface.participants = num_participants
    game_interface.game_input_packet = gameInputPacket

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
                                 args=(quit_event, callback, parameters[i],
                                       str(gameInputPacket.sPlayerConfiguration[i].wName),
                                       teams[i], i, modules[i], agent_metadata_queue))

            process.start()

    logger.debug("Successfully configured bots. Setting flag for injected dll.")
    game_interface.start_match()

    logger.info("Press any character to exit")
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

    logger.info("Shutting Down")
    quit_event.set()
    # Wait for all processes to terminate before terminating main process
    terminated = False
    while not terminated:
        terminated = True
        for callback in callbacks:
            if not callback.is_set():
                terminated = False


def run_agent(terminate_event, callback_event, config_file, name, team, index, module_name, agent_telemetry_queue):
    bm = bot_manager.BotManager(terminate_event, callback_event, config_file, name, team,
                                index, module_name, agent_telemetry_queue)
    bm.run()


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
        if not team in team_pids_map:
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
