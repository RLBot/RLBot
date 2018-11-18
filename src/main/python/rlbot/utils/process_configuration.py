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


def extract_all_pids(agent_metadata_map):
    pids = set()
    for player_index, data in agent_metadata_map.items():
        pids.update(data.pids)
    return pids


def is_process_running(program, scriptname):
    if not optional_packages_installed:
        return True
    for pid in psutil.process_iter(attrs=['name', 'exe']):
        try:
            p = pid.info.values()
            if program in p or scriptname in p:
                return True
        except psutil.NoSuchProcess:
            continue
    return False
