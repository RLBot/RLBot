import importlib
import inspect
import os
import sys

from RLBotFramework.agents.base_agent import BaseAgent


class AgentLoadData:
    def __init__(self, python_file, base_class):
        self.python_file = python_file
        self.base_class = base_class
        self.agent_class = None
        self.agent_module = None
        self.reload()

    def reload(self):
        dir_name = os.path.dirname(self.python_file)
        module_name = os.path.splitext(os.path.basename(self.python_file))[0]
        keys_before = set(sys.modules.keys())

        # Temporarily modify the sys.path while we load the module so that bots can use import statements naturally
        sys.path.insert(0, dir_name)
        self.agent_module = importlib.import_module(module_name)

        # Clean up the changes to sys.path and sys.modules to avoid collisions between bots and to
        # prepare for the next reload.
        added = set(sys.modules.keys()).difference(keys_before)
        del sys.path[0]
        for key in added:
            del sys.modules[key]

        # Find and return the bot class
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

    return AgentLoadData(python_file, base_class)


def extract_agent_class(agent_module, base_class):
    valid_classes = [agent[1] for agent in inspect.getmembers(agent_module, inspect.isclass)
                     if issubclass(agent[1], base_class) and agent[1].__module__ == agent_module.__name__]

    if len(valid_classes) == 0:
        raise ValueError('Could not locate a suitable bot class')

    return valid_classes[0]


def get_base_repo_path():
    """Gets the path of the RLBot directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
