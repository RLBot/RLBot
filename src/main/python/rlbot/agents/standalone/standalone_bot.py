import inspect
import multiprocessing as mp
import sys
from pathlib import Path
from typing import Type

from rlbot.agents.standalone.test_spawner import TestSpawner
from rlbot.agents.base_agent import BaseAgent
from rlbot.agents.standalone.standalone_bot_config import StandaloneBotConfig
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.utils.class_importer import ExternalClassWrapper


class StandaloneBot(BaseAgent):
    """
    This is intended to be a base class for python bots. Your bot file would be something like this:

    from rlbot.agents.standalone.standalone_bot import StandaloneBot, run_bot

    class MyCoolBot(StandaloneBot):
        def get_output(self, packet: GameTickPacket):
            ...

    if __name__ == '__main__':
        run_bot(MyCoolBot)


    And also you would need your config file to have supports_standalone = True

    See rlbot.agents.standalone.standalone_bot_config for how to use command line arguments
    to set more options.
    """

    def __init__(self, name, team, index):
        super().__init__(name, team, index)


def run_bot(agent_class: Type[StandaloneBot]):
    config = StandaloneBotConfig(sys.argv)
    python_file = inspect.getfile(agent_class)

    config_obj = agent_class.base_create_agent_configurations()
    bundle = None
    if config.config_file is not None:
        # If the config file was not passed, then the bot will miss out on any custom configuration,
        # tick rate preference, etc.
        bundle = get_bot_config_bundle(Path(python_file).parent / config.config_file)
        config_obj.parse_file(bundle.config_obj, config_directory=bundle.config_directory)

    spawn_id = config.spawn_id
    player_index = config.player_index
    team = config.team
    name = config.name

    if config.is_missing_args:
        # This process must not have been created by the RLBot framework, so this is probably
        # a developer doing some testing who did not pass all the params. Take it upon ourselves
        # to fire up the game if necessary.
        print(f'############################################################################################')
        print(f'Args are missing, so we will assume this is a dev workflow and insert the bot into the game!')
        print(f'############################################################################################')
        test_spawner = TestSpawner(Path(python_file), config, bundle)
        test_spawner.spawn_bot()
        spawn_id = test_spawner.spawn_id
        player_index = test_spawner.player_index
        team = test_spawner.team
        name = test_spawner.name


    agent_class_wrapper = ExternalClassWrapper(python_file, StandaloneBot)

    # Pass in dummy objects for mp.Event, mp.Queue. We will not support that
    # functionality for standalone bots; it's generally unused anyway.
    bot_manager = BotManagerStruct(terminate_request_event=mp.Event(),
                                  termination_complete_event=mp.Event(),
                                  reload_request_event=mp.Event(),
                                  bot_configuration=config_obj,
                                  name=name,
                                  team=team,
                                  index=player_index,
                                  agent_class_wrapper=agent_class_wrapper,
                                  agent_metadata_queue=mp.Queue(),
                                  match_config=None,
                                  matchcomms_root=config.matchcomms_url,
                                  spawn_id=spawn_id)
    bot_manager.run()
