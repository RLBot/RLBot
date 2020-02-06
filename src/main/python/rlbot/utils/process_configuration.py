import re
from typing import Set, Tuple, Union
import platform
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER

optional_packages_installed = False
try:
    import psutil
    optional_packages_installed = True
except ImportError:
    pass


def configure_processes(agent_metadata_map, logger):
    """
    This will update the priority and CPU affinity of the processes owned by bots to try to achieve fairness and
    good performance.

    :param agent_metadata_map: A mapping of player index to agent metadata, including a list of owned process ids.
    """

    if not optional_packages_installed:
        logger.warning("\n#### WARNING ####\n"
                       "You are missing some optional packages which will become mandatory in the future!\n"
                       "Please run `pip install -r requirements.txt` to enjoy optimal functionality "
                       "and future-proof yourself!\n")

    if not optional_packages_installed:
        return

    team_pids_map = {}

    for player_index, data in agent_metadata_map.items():
        team = data.team
        if team not in team_pids_map:
            team_pids_map[team] = set()
        team_pids_map[team].update(data.pids)

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
                try:
                    p = psutil.Process(pid)
                    p.cpu_affinity(team_cpus)  # Restrict the process to run on the cpus assigned to the team
                    if platform.system() == 'Windows': # TODO only works on windows
                        p.nice(psutil.HIGH_PRIORITY_CLASS)  # Allow the process to run at high priority
                except Exception as e:
                    get_logger(DEFAULT_LOGGER).info(e)
    else:
        # Consider everything a shared pid, because we are not in a position to split up cpus.
        for team, team_set in team_pids_map.items():
            shared_pids.update(team_set)

    for pid in shared_pids:
        try:
            p = psutil.Process(pid)  # Allow the process to run at high priority
            if platform.system() == 'Windows': # TODO only works on windows
                p.nice(psutil.HIGH_PRIORITY_CLASS)
        except Exception as e:
            get_logger(DEFAULT_LOGGER).info(e)


def extract_all_pids(agent_metadata_map):
    pids = set()
    for player_index, data in agent_metadata_map.items():
        pids.update(data.pids)
    return pids


def is_process_running(program, scriptname, required_args: Set[str]) -> Tuple[bool, Union[psutil.Process, None]]:
    if not optional_packages_installed:
        return True, None
    # Find processes which contain the program or script name.
    matching_processes = []
    for process in psutil.process_iter():
        try:
            p = process.name()
            if program in p or scriptname in p:
                matching_processes.append(process)
        except psutil.NoSuchProcess:
            continue
    # If matching processes were found, check for correct arguments.
    if len(matching_processes) != 0:
        for process in matching_processes:
            try:
                args = process.cmdline()[1:]
                for required_arg in required_args:
                    matching_args = [arg for arg in args if re.match(required_arg, arg, flags=re.IGNORECASE) is not None]
                    # Skip this process because it does not have a matching required argument.
                    if len(matching_args) == 0:
                        break
                else:
                    # If this process has not been skipped, it matches all arguments.
                    return True, process
            except psutil.AccessDenied:
                print(f"Access denied when trying to look at cmdline of {process}!")
        # If we didn't return yet it means all matching programs were skipped.
        raise WrongProcessArgs(f"{program} is not running with required arguments: {required_args}!")
    # No matching processes.
    return False, None


class WrongProcessArgs(UserWarning):
    pass
