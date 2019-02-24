import sys

# This module exists to give users an indication that they need to have
# a version of python compatible with the RLBot framework.
# Otherwise people might find out by in-the-guts error messages
# after quite a while of the runner launching.
minimum_python_version = (3, 6)

# Deliberately using old string formatting for compatibility.
error_string = """You appear to be using an old version of Python: %s
 RLBot requires Python %d.%d or later.
 After installing, ensure your environment point to the new Python version, then run setup.bat""" % (
    (sys.version,) + minimum_python_version)


def check_python_version():
    assert sys.version_info >= minimum_python_version, error_string
