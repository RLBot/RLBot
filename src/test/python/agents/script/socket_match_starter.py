from pathlib import Path
from threading import Thread
from time import sleep

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.socket.socket_manager import SocketRelay


class SampleScript:

    def __init__(self):
        self.socket_relay = SocketRelay()

    def run(self):
        thread = Thread(target=self.socket_relay.connect_and_run, args=(True, True, True))
        thread.start()
        while not self.socket_relay.is_connected:
            print('Waiting for connection...')
            sleep(1)
        match_config = read_match_config_from_file(Path(__file__).parent.parent.parent.parent.parent.parent / 'rlbot.cfg')
        print("Sending match config")
        self.socket_relay.send_match_config(match_config)
        self.socket_relay.disconnect()
        thread.join()


# You can use this __name__ == '__main__' thing to ensure that the script doesn't start accidentally if you
# merely reference its module from somewhere
if __name__ == '__main__':
    print("Start match script starting...")
    script = SampleScript()
    script.run()
