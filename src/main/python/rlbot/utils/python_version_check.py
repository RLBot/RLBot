import sys

# This module exists to give users an indication that they need to have
# a version of python compatible with the RLBot framework.
# Otherwise people might find out by in-the-guts error messages
# after quite a while of the runner launching.
minimum_python_version = (3, 6)
recommended_python_version = (3, 7)

# Deliberately using old string formatting for compatibility.
error_string = "You appear to be using an old version of Python: %s\n RLBot requires Python %d.%d or later. Python %d.%d is recommended.\n After installing, ensure your environment point to the new Python version, then run setup.bat" % ((sys.version,) + minimum_python_version + recommended_python_version)

assert sys.version_info >= minimum_python_version, error_string
