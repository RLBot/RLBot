from rlbot.parsing.custom_config import ConfigObject

LOCATIONS_HEADER = 'Locations'
DETAILS_HEADER = 'Details'
PYTHON_FILE_KEY = 'python_file'
REQUIREMENTS_FILE_KEY = 'requirements_file'
LOGO_FILE_KEY = 'logo_file'
NAME_KEY = "name"
SUPPORTS_EARLY_START_KEY = "supports_early_start"
REQUIRES_TKINTER = "requires_tkinter"
USE_VIRTUAL_ENVIRONMENT_KEY = "use_virtual_environment"
REQUIRED_PYTHON_37 = "requires_py37"


class RLBotRunnable:
    name = None

    def __init__(self, name):
        self.name = name

    def init_match_config(self, match_config: 'MatchConfig'):
        """
        Override this method if you would like to be informed of what config was used to start the match.
        Useful for knowing what map you're on, mutators, etc.
        """
        pass

    def initialize_agent(self):
        """
        Called for all heaver initialization that needs to happen.
        The config is fully loaded at this point
        """
        pass

    def retire(self):
        """Called after the game ends"""
        pass

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        """
        If your bot needs to add custom configurations, you may override this and use the `config` object.
        :param config: A ConfigObject instance.
        """
        pass

    def is_hot_reload_enabled(self):
        """
        If true, the framework will watch all your python files for modifications and instantly reload your bot
        so that the logic changes take effect. You may wish to disable this if you're concerned about performance.
        """
        return True

    # Information about @classmethod: https://docs.python.org/3/library/functions.html#classmethod
    @classmethod
    def base_create_agent_configurations(cls) -> ConfigObject:
        """
        This is used when initializing agent config via builder pattern.
        It also calls `create_agent_configurations` that can be used by BaseAgent subclasses for custom configs.
        :return: Returns an instance of a ConfigObject object.
        """
        config = ConfigObject()
        location_config = config.add_header_name(LOCATIONS_HEADER)
        location_config.add_value(PYTHON_FILE_KEY, str,
                                  description="Bot's python file.\nOnly need this if RLBot controlled")
        location_config.add_value(REQUIREMENTS_FILE_KEY, str,
                                  description="Python requirements.txt file listing needed dependencies.")
        location_config.add_value(NAME_KEY, str, default='nameless',
                                  description='The name that will be displayed in game')
        location_config.add_value(LOGO_FILE_KEY, str,
                                  description="Location of an image file to use as your bot's logo")
        location_config.add_value(SUPPORTS_EARLY_START_KEY, bool,
                                  description="True if this bot can be started before the Rocket League match begins.")
        location_config.add_value(REQUIRES_TKINTER, bool,
                                  description="True if the tkinter library is needed.")
        location_config.add_value(USE_VIRTUAL_ENVIRONMENT_KEY, bool,
                                  description="True if the runnable wants to run in a virtual environment.")
        location_config.add_value(REQUIRED_PYTHON_37, bool,
                                  description="True if the runnable requires Python 3.7.")

        details_config = config.add_header_name(DETAILS_HEADER)
        details_config.add_value('developer', str, description="Name of the bot's creator/developer")
        details_config.add_value('description', str, description="Short description of the bot")
        details_config.add_value('fun_fact', str, description="Fun fact about the bot")
        details_config.add_value('github', str, description="Link to github repository")
        details_config.add_value('language', str, description="Programming language")
        details_config.add_value('tags', str, description="Comma separated list of tags, used by RLBotGUI")

        cls.create_agent_configurations(config)

        return config
