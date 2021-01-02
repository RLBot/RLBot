"""Standalone Bot Script

Usage:
    standalone [--player-index=0] [--config-file=C:/Users/t/code/myBot.cfg] [--name=MyBot] [--team=0] [--spawn-id=23245] [--matchcomms-url=ws://localhost:49468]

Options:
    --player-index=I             Index that the player is running under. Will be passed to your bot's constructor.
    --config-file=C              Absolute path to .cfg file, which could define the executable path, preferred tick rate, etc.
    --name=N                     Name that will be passed to your bot's constructor. Does not influence in-game name.
    --team=T                     Team the bot is playing on, 0 for blue, 1 for orange. Will be passed to your bot's constructor.
    --spawn-id=S                 Spawn identifier used to confirm the right car in the packet.
    --matchcomms-url=M           A url that can be used to connect with the matchcomms system.
"""
from typing import List, Union

from docopt import docopt, DocoptExit, printable_usage
from urllib.parse import ParseResult, urlparse


class StandaloneBotConfig:

    def __init__(self, argv: List[str], strict_mode=True):
        arguments = docopt(__doc__, argv[1:])
        self.name = arguments['--name']
        self.team = self.int_or_none(arguments['--team'])
        self.player_index = self.int_or_none(arguments['--player-index'])
        self.spawn_id = self.int_or_none(arguments['--spawn-id'])
        self.config_file = arguments['--config-file']
        self.matchcomms_url = self.url_or_none(arguments['--matchcomms-url'])
        self.is_missing_args = False

        if self.name is None or self.team is None or self.player_index is None or self.spawn_id is None \
                or self.config_file is None or self.matchcomms_url is None:
            print('Standalone bot is missing required arguments!')
            print(printable_usage(__doc__))
            self.is_missing_args = True

    def int_or_none(self, val) -> Union[int, None]:
        if val:
            return int(val)
        return None

    def url_or_none(self, val) -> Union[ParseResult, None]:
        if val:
            return urlparse(val)
        return None
