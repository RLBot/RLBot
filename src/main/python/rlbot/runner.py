import sys

from rlbot.setup_manager import SetupManager


def main():

    if sys.maxsize <= 2**32:
        raise RuntimeError('You appear to have a 32 bit version of Python installed. RLBot only works with 64 bit!')

    print("starting")
    manager = SetupManager()
    manager.startup()
    manager.load_config()
    manager.launch_bot_processes()
    manager.run()  # Runs forever until interrupted
    manager.shut_down()


if __name__ == '__main__':
    main()
