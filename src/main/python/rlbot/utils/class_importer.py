import importlib
import inspect
import os
import sys

from rlbot.agents.base_agent import BaseAgent


class ExternalClassWrapper:
    """
    Given the absolute path of a python file, this can load the associated module and find a class inside it
    that extends the base class. The module in the target file may assume that its current directory is on
    sys.path and expect import statements to work accordingly.

    Will throw an exception during construction if the module cannot be loaded or the class cannot be located.
    """

    def __init__(self, python_file, base_class):
        self.python_file = python_file
        self.base_class = base_class
        self.loaded_class, self.loaded_module = load_external_class(self.python_file, self.base_class)

    def get_loaded_class(self):
        """
        Guaranteed to return a valid class that extends base_class.
        """
        return self.loaded_class

    def reload(self):
        self.loaded_class, self.loaded_module = load_external_class(self.python_file, self.base_class)


def import_agent(python_file) -> ExternalClassWrapper:
    """
    Imports the first class that extends BaseAgent.

    :param python_file: The absolute path of the bot's main python file
    :return: The agent requested or BaseAgent if there are any problems.
    """
    return import_class_with_base(python_file, BaseAgent)


def import_class_with_base(python_file, base_class) -> ExternalClassWrapper:
    """
    Imports the first class that extends base_class.

    :param python_file: The absolute path of the bot's main python file
    :param base_class: The class that we look for the extension for
    :return: The agent requested or BaseAgent if there are any problems.
    """

    return ExternalClassWrapper(python_file, base_class)


def load_external_class(python_file, base_class):
    """
    Returns a tuple: (subclass of base_class, module)
    """
    loaded_module = load_external_module(python_file)

    # Find a class that extends base_class
    loaded_class = extract_class(loaded_module, base_class)
    return loaded_class, loaded_module

def load_external_module(python_file):
    """
    Returns the loaded module.
    All of its newly added dependencies are removed from sys.path after load.
    """

    # There's a special case where python_file may be pointing at the base agent definition here in the framework.
    # This is sometimes done as a default and we want to allow it. Short-circuit the logic because
    # loading it as if it's an external class is a real mess.
    if os.path.abspath(python_file) == os.path.abspath(inspect.getfile(BaseAgent)):
        return BaseAgent, BaseAgent.__module__

    if not os.path.isfile(python_file):
        raise FileNotFoundError(f"Could not find file {python_file}!")

    dir_name = os.path.dirname(python_file)
    module_name = os.path.splitext(os.path.basename(python_file))[0]
    keys_before = set(sys.modules.keys())

    # Temporarily modify the sys.path while we load the module so that the module can use import statements naturally
    sys.path.insert(0, dir_name)
    loaded_module = importlib.import_module(module_name)

    # Clean up the changes to sys.path and sys.modules to avoid collisions with other external classes and to
    # prepare for the next reload.
    added = set(sys.modules.keys()).difference(keys_before)
    del sys.path[0]
    for key in added:
        del sys.modules[key]

    return loaded_module

def extract_class(containing_module, base_class):
    valid_classes = [agent[1] for agent in inspect.getmembers(containing_module, inspect.isclass)
                     if issubclass(agent[1], base_class) and agent[1].__module__ == containing_module.__name__]

    if len(valid_classes) == 0:
        raise ModuleNotFoundError(f"Could not locate a suitable bot class in module {containing_module.__file__}")

    return valid_classes[0]
