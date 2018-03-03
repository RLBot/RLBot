import ctypes

from utils.agent_creator import get_base_repo_path


class GameInterface:
    def __init__(self):
        self.game = ctypes.WinDLL(get_base_repo_path() + 'RLBot_Core.dll')

    def update_live_data_packet(self):
        pass

    def update_match_data_packet(self):
        pass

    def start_match(self):
        pass

    def update_player_input(self):
        pass

    def send_chat(self):
        pass

