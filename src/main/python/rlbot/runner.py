from rlbot.setup_manager import SetupManager
from rlbot.utils.python_version_check import check_python_version


def main():

    print("starting")
    check_python_version()
    manager = SetupManager()
    manager.connect_to_game()
    manager.load_config()
    manager.launch_ball_prediction()
    manager.launch_quick_chat_manager()
    manager.launch_bot_processes()
    manager.start_match()
    manager.infinite_loop()  # Runs forever until interrupted


if __name__ == '__main__':
    main()
