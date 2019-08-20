"""
External code is encouraged to use these functions directly. It is part of our public API.

Avoid moving this file or changing any of the function signatures!
"""
from rlbot.utils.file_util import contains_locked_file, get_rlbot_directory
try:
    import httplib
except:
    import http.client as httplib


def is_safe_to_upgrade():
    """
    Reports whether it's currently safe to upgrade the rlbot package, e.g. via pip. An example of when it's
    unsafe is when one of the dlls is in use, which can cause the upgrade to fail half way through.
    See https://github.com/RLBot/RLBot/issues/130
    """
    return not contains_locked_file(get_rlbot_directory())

# https://stackoverflow.com/questions/3764291/checking-network-connection


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except:
        return False
    finally:
        conn.close()
