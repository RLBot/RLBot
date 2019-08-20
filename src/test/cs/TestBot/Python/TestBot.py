import os

from rlbot.agents.base_agent import BOT_CONFIG_AGENT_HEADER
from rlbot.agents.base_dotnet_agent import BaseDotNetAgent
from rlbot.parsing.custom_config import ConfigHeader, ConfigObject


class DotNetBot(BaseDotNetAgent):
    def get_port_file_path(self):
        # Look for a port.cfg file in the same directory as THIS python file.
        return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'port.cfg'))

    def load_config(self, config_header: ConfigHeader):
        self.dotnet_executable_path = config_header.getpath('dotnet_executable_path')
        self.logger.info(".NET executable is configured as {}".format(self.dotnet_executable_path))

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('dotnet_executable_path', str, default=None,
                         description='Relative path to the executable that runs the .NET executable.')