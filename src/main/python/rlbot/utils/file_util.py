import os


def get_python_root() -> str:
    """Gets the path of the python root directory that rlbot lives in."""
    return os.path.dirname(get_rlbot_directory())


def get_rlbot_directory() -> str:
    """Gets the path of the rlbot package directory"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def contains_locked_file(directory: str):
    """
    Avoid moving or renaming this! It is considered part of the API of this package.
    :return: True if any of the files in the directory are in use. For example, if the dll is injected
    into the game, this will definitely return true.
    """
    for root, subdirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'a'):
                    pass
            except IOError:
                print(file_path)
                return True
    return False
