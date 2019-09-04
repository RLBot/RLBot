from rlbot.setup_manager import SetupManager
from rlbot.utils.python_version_check import check_python_version


def main():

    print("starting")
    check_python_version()
    manager = SetupManager()
    manager.load_config()
    manager.connect_to_game()
    manager.launch_early_start_bot_processes()
    manager.start_match()
    manager.launch_bot_processes()
    manager.infinite_loop()  # Runs forever until interrupted


if __name__ == '__main__':
    main()
