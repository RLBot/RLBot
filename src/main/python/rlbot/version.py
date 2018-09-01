# Store the version here so:
# 1) we don't load dependencies by storing it in __init__.py
# 2) we can import it in setup.py for the same reason
# 3) we can import it into your module module
# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
__version__ = '0.0.32'

release_notes = {
    '0.0.32': """
    More comprehensive fix for Rocket League patch 1.50. Compared to previous version:
    - Dropshot tile data is fixed
    - Boost pad data is fixed
    - Loadout configuration is fixed
    
    Thanks to ccman32 and dtracers for delivering this fix quickly!
    """,
    '0.0.31': """
    Rapid response to Rocket League patch 1.50 with the following known issues:
    - Dropshot tile data is missing
    - Boost pad data is missing
    - Loadout configuration is broken
    
    Thanks to ccman32 and dtracers for delivering this short-term fix quickly.

    We will follow this up with a proper fix as soon as possible. You may also choose to stay on
    Rocket League 1.49 and RLBot 0.0.30, ask for instructions on discord.
    """,
    '0.0.30': """
    - New core dll that is less likely to break when Rocket League is patched - ccman32 and hallo-doei
    - Fixed bug resulting in incorrect quickchat - dtracers
    - Added more built-in colors to the python rendering manager - Eastvillage
    - Fix for items with a ':' not showing up in the GUI - hallo-doei
    - Fix for GUI not saving correct path - hallo-doei
    - Fix for GUI crash when saving preset then canceling - hallo-doei
    - Adding file checking before injection (Resolves #167) - Redox
    - Fixed typo in rlbot.cfg - Redox
    - Fancy release notes - tarehart and Skyborg
    """
}

release_banner = """

           ______ _     ______       _
     10100 | ___ \ |    | ___ \     | |   00101
    110011 | |_/ / |    | |_/ / ___ | |_  110011
  00110110 |    /| |    | ___ \/ _ \| __| 01101100
    010010 | |\ \| |____| |_/ / (_) | |_  010010
     10010 \_| \_\_____/\____/ \___/ \__| 01001


"""


def get_current_release_notes():
    if __version__ in release_notes:
        return release_notes[__version__]
    return ''


def get_help_text():
    return "Trouble? Ask on Discord at https://discord.gg/5cNbXgG " \
           "or report an issue at https://github.com/RLBot/RLBot/issues"


def print_current_release_notes():
    print(release_banner)
    print("Version {}".format(__version__))
    print(get_current_release_notes())
    print(get_help_text())
    print("")
