from RLBotFramework.setup_manager import SetupManager
import configparser
from RLBotFramework.parsing.rlbot_config_parser import create_bot_config_layout
from RLBotFramework.utils.logging_utils import log
from integration_test.history import HistoryIO
import multiprocessing
import psutil

RLBOT_CONFIG_FILE = 'integration_test/rlbot.cfg'


def record_atba():
    raw_config_parser = configparser.RawConfigParser()
    raw_config_parser.read(RLBOT_CONFIG_FILE)
    framework_config = create_bot_config_layout()
    framework_config.parse_file(raw_config_parser, max_index=10)

    manager = SetupManager()
    manager.startup()
    manager.load_config(framework_config=framework_config)
    manager.launch_bot_processes()
    manager.run()

def ensure_dll_is_injected():
    manager = SetupManager()
    manager.startup()


def KILL(process):
    try:
        process.kill()
    except psutil._exceptions.NoSuchProcess as e:
        return
def kill_proc_tree(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    KILL(parent) # THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE
    for child in children: # THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE
        KILL(child)  # THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE THIS CAN NOT CONTINUE
    gone, still_alive = psutil.wait_procs(children, timeout=5)


def gather_data(timeout=20.0):
    log("Gathering data...")
    HistoryIO().clear()

     # Do this synchonously, the time the process needs to startup is more consistent.
    ensure_dll_is_injected()

    proc = multiprocessing.Process(target=record_atba)
    log("Starting data gethering process...")
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        log("Stopping data gathering...")
        # TODO: Find a nicer way. maybe we should exit out of the match too
        kill_proc_tree(proc.pid)
        proc.join()
    log("Data gathering finished.")
