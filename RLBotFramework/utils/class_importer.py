import importlib
import inspect

import os

from RLBotFramework.agents.base_agent import BaseAgent
from RLBotFramework.utils.logging_utils import log_warn


def is_extends_base_class(module, base_class):
    super_classes = module.__bases__
    for super_class in super_classes:
        if super_class == base_class:
            return True
    return False


def import_agent(module_name):
    """
    Imports the first class that extends BaseAgent.

    :param module_name: A string formatted like a normal python import
    :return: The agent requested or BaseAgent if there are any problems.
    """
    return import_class_with_base(module_name, BaseAgent)


def import_class_with_base(module_name, base_class):
    """
    Imports the first class that extends base_class.

    :param module_name: A string formatted like a normal python import
    :param base_class: The class that we look for the extension for also is returned if no matching module is found
    :return: The agent requested or BaseAgent if there are any problems.
    """
    try:
        module = importlib.import_module(module_name)
        agent_class = [agent[1] for agent in inspect.getmembers(module, inspect.isclass)
                       if is_extends_base_class(agent[1], base_class)]

        agent = agent_class[0]
        # grabs only the first one
        return agent
    except ModuleNotFoundError as e:
        log_warn('ModuleNotFoundError: %s\nsub module %s not found using %s instead', [str(e), str(module_name),
                                                                                       str(base_class)])
    except Exception as e:
        log_warn('Error: %s\n%s not found using %s instead', [str(e), str(module_name), str(base_class)])
    finally:
        return base_class


def get_base_import_package(config_file_path):
    """
    Returns a string that is the base import path of the config file.
    :param config_file_path:
    :return:
    """
    original_path = get_base_repo_path()
    config_file_path = os.path.realpath(config_file_path)
    module = config_file_path.replace(original_path, "", 1).replace(os.sep, ".")
    remove_ending = '.' in config_file_path
    if remove_ending:
        return module[1:module.rfind(".")]
    else:
        return module[1:]


def get_base_repo_path():
    """Gets the path of the RLBot directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def get_agent_class_location(input_class):
    return inspect.getfile(input_class)
