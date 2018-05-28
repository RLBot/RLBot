from rlbot.setup_manager import SetupManager


def main():
    print("starting")
    manager = SetupManager()
    manager.startup()
    manager.load_config()
    manager.launch_bot_processes()
    manager.run()  # Runs forever until interrupted
    manager.shut_down()


if __name__ == '__main__':
    main()
