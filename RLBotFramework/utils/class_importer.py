import importlib
import inspect

import os

from RLBotFramework.agents.base_agent import BaseAgent
from RLBotFramework.utils.logging_utils import log_warn


class AgentLoadData:
    def __init__(self, module_spec, base_class):
        self.module_spec = module_spec
        self.base_class = base_class
        self.agent_class = None
        self.agent_module = None
        self.reload()

    def reload(self):
        self.agent_module = importlib.util.module_from_spec(self.module_spec)
        self.module_spec.loader.exec_module(self.agent_module)
        self.agent_class = extract_agent_class(self.agent_module, self.base_class)


def import_agent(python_file):
    """
    Imports the first class that extends BaseAgent.

    :param python_file: The absolute path of the bot's main python file
    :return: The agent requested or BaseAgent if there are any problems.
    """
    return import_class_with_base(python_file, BaseAgent)


def import_class_with_base(python_file, base_class):
    """
    Imports the first class that extends base_class.

    :param python_file: The absolute path of the bot's main python file
    :param base_class: The class that we look for the extension for
    :return: The agent requested or BaseAgent if there are any problems.
    """
    module_name = os.path.splitext(os.path.basename(python_file))[0]
    module_spec = importlib.util.spec_from_file_location(module_name, python_file)

    return AgentLoadData(module_spec, base_class)


def extract_agent_class(agent_module, base_class):
    valid_classes = [agent[1] for agent in inspect.getmembers(agent_module, inspect.isclass)
                     if issubclass(agent[1], base_class) and agent[1].__module__ == agent_module.__name__]

    if len(valid_classes) == 0:
        raise ValueError('Could not locate a suitable bot class')

    return valid_classes[0]


def get_base_repo_path():
    """Gets the path of the RLBot directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

