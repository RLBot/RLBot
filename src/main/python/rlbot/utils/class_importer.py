import importlib
import inspect
import os
import sys
from pathlib import Path

from rlbot.agents.base_agent import BaseAgent
from rlbot.utils.logging_utils import get_logger


def is_file_under_path(file, path):
    try:
        Path(file).relative_to(path)
        return True
    except ValueError:
        return False


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
        self.logger = get_logger('class_importer')
        self.owned_module_keys = set()
        self._load_external_class_and_record_module_changes()

    def _load_external_class_and_record_module_changes(self):
        keys_before = set(sys.modules.keys())
        self.loaded_class, self.loaded_module = load_external_class(self.python_file, self.base_class)
        # Compute the set of modules which were loaded recursively and had not been seen before
        added_module_keys = set(sys.modules.keys()).difference(keys_before)
        self.owned_module_keys = self.owned_module_keys.union(added_module_keys)

    def get_loaded_class(self):
        """
        Guaranteed to return a valid class that extends base_class.
        """
        return self.loaded_class

    def _reload_owned_modules(self):
        """
        A module is eligible for reload if:
        - It has a python file associated with it that lives under the same directory as the main python_file
        - It's present in self.owned_module_keys, i.e. the main python file appears to have been responsible for its
          insertion into the system module list.

        We do the path check because otherwise we try to reload various low-level modules that have nothing to do with
        the bot logic, and reloading those modules sometimes throws an exception. The owned_module_keys is less
        critical, but it feels safer / faster than doing path checks on the entirety of sys.modules. E.g. what if you
        have two bots in the same folder and only want to reload one of them.
        """
        for module_key in self.owned_module_keys:
            if module_key in sys.modules:
                try:
                    mod = sys.modules[module_key]
                    if hasattr(mod, '__file__') and mod.__file__ and is_file_under_path(mod.__file__, Path(self.python_file).parent):
                        importlib.reload(sys.modules[module_key])
                except Exception as e:
                    self.logger.warning(f"Suppressed error when hot reloading {module_key}: {e}")

    def reload(self):
        dir_name = os.path.dirname(self.python_file)
        sys.path.insert(0, dir_name)
        # Why call this twice? Because the modules would need to be loaded from bottom-up
        # in terms of their dependency tree in order for all changes to manifest in one attempt.
        # That's hard, it's much easier to just repeat it.
        self._reload_owned_modules()
        self._reload_owned_modules()
        del sys.path[0]
        self._load_external_class_and_record_module_changes()


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

    # Temporarily modify the sys.path while we load the module so that the module can use import statements naturally
    sys.path.insert(0, dir_name)
    loaded_module = importlib.import_module(module_name)
    del sys.path[0]

    return loaded_module


def extract_class(containing_module, base_class):
    valid_classes = [agent[1] for agent in inspect.getmembers(containing_module, inspect.isclass)
                     if issubclass(agent[1], base_class) and agent[1].__module__ == containing_module.__name__]

    if len(valid_classes) == 0:
        raise ModuleNotFoundError(f"Could not locate a suitable bot class in module {containing_module.__file__}")

    return valid_classes[0]
