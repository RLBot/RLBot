from RLBotFramework.setup_manager import SetupManager

if __name__ == '__main__':
    manager = SetupManager()
    manager.startup()
    manager.load_config()
    manager.launch_bot_processes()
    manager.run()
