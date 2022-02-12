import re
import psutil
from typing import Set, Tuple, Union, List, Dict
import platform
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.botmanager.agent_metadata import AgentMetadata


def configure_processes(agent_metadata_map: Dict[int, AgentMetadata], logger):
    """
    This will update the priority and CPU affinity of the processes owned by bots to try to achieve fairness and
    good performance.

    :param agent_metadata_map: A mapping of player index to agent metadata, including a list of owned process ids.
    """

    team_pids_map = {}

    for player_index, data in agent_metadata_map.items():
        team = data.team
        if team not in team_pids_map:
            team_pids_map[team] = set()
        team_pids_map[team].update(data.pids)

    shared_pids = set()

    if len(team_pids_map) >= 2 and len(get_team_cpus(0)) > 0:
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
            team_cpus = get_team_cpus(team)
            for pid in team_pids:
                try:
                    p = psutil.Process(pid)
                    configure_process(p, team_cpus)
                except Exception as e:
                    get_logger(DEFAULT_LOGGER).info(e)
    else:
        # Consider everything a shared pid, because we are not in a position to split up cpus.
        for team, team_set in team_pids_map.items():
            shared_pids.update(team_set)

    for pid in shared_pids:
        try:
            p = psutil.Process(pid)  # Allow the process to run at high priority
            if platform.system() == 'Windows':
                p.nice(psutil.HIGH_PRIORITY_CLASS)
        except Exception as e:
            get_logger(DEFAULT_LOGGER).info(e)


def configure_process(proc: psutil.Process, cores: List[int], infer_multi_team=False):
    try:
        if infer_multi_team:
            existing_affinity = proc.cpu_affinity()
            if len(existing_affinity) < psutil.cpu_count():
                # The process in question has already been pinned to a subset of the CPUs.
                # This might be a process spanning multiple teams, so we will set affinity to
                # the combination of existing and newly requested cores.
                cores = sorted(set(existing_affinity + cores))
        proc.cpu_affinity(cores)

        if platform.system() == 'Windows':
            proc.nice(psutil.HIGH_PRIORITY_CLASS)  # Allow the process to run at high priority
    except Exception as e:
        get_logger(DEFAULT_LOGGER).info(e)


def get_team_cpus(team: int) -> List[int]:
    cpu_count = psutil.cpu_count()
    cpus_per_team = cpu_count // 3
    team_cpu_offset = cpus_per_team * team
    return list(range(cpu_count - cpus_per_team - team_cpu_offset, cpu_count - team_cpu_offset))


def extract_all_pids(agent_metadata_map):
    pids = set()
    for player_index, data in agent_metadata_map.items():
        pids.update(data.pids)
    return pids


def get_process(program, scriptname, required_args: Set[str]) -> Union[psutil.Process, None]:
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
        mismatch_found = False
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
                    return process
                mismatch_found = True
            except psutil.AccessDenied:
                print(f"Access denied when trying to look at cmdline of {process}!")
            except psutil.NoSuchProcess:
                # process died whilst we were looking at it, so pretend we found none, it will get handles another time
                pass
        if mismatch_found:
            # If we didn't return yet it means all matching programs were skipped.
            raise WrongProcessArgs(f"{program} is not running with required arguments: {required_args}!")
    # No matching processes.
    return None


def is_process_running(program, scriptname, required_args: Set[str]) -> Tuple[bool, Union[psutil.Process, None]]:
    process = get_process(program, scriptname, required_args)
    return process is not None, process


def append_child_pids(agent_metadata_map: Dict[int, AgentMetadata]) -> bool:
    found_unreported_pids = False
    for md in agent_metadata_map.values():
        traversed_pids = set()
        for pid in md.pids:
            if pid not in traversed_pids:
                traversed_pids.add(pid)
                try:
                    process = psutil.Process(pid)
                    child_pids = [c.pid for c in  process.children(recursive=True)]
                    traversed_pids.update(child_pids)
                except:
                    pass
        if len(md.pids) < len(traversed_pids):
            found_unreported_pids = True
        md.pids = list(traversed_pids)
    return found_unreported_pids


class WrongProcessArgs(UserWarning):
    pass
