# Store the version here so:
# 1) we don't load dependencies by storing it in __init__.py
# 2) we can import it in setup.py for the same reason
# 3) we can import it into your module module
# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
__version__ = '1.6.0'

release_notes = {
    '1.6.0':"""
    Add support for auto starting .NET executables.
    """,
    '1.5.1': """
    Fixed crash with GUI when no default RLBot.cfg file was found.
    Updated GUI to launch Rocket League when clicking run if no Rocket League process is found. - ima9rd 
    """,
    '1.5.0': """
    Adding a have_internet helper function to help streamline upgrade checks. - ima9rd
    """,
    '1.4.2': """
    Adding support for auto-running java bots during tournaments. To take advantage of this
    in your bot, see https://github.com/RLBot/RLBotJavaExample/wiki/Auto-Launching-Java
    
    Plus bug fixes:
    - Fixed a bug where auto-run executables would crash when trying to write to stderr.
    - Dragging bots to another team in the GUI no longer breaks the config.
    """,
    '1.3.0': """
    Accurate ball prediction for Hoops and Dropshot modes!
      - Kipje13, Marvin, NeverCast, et. al.
    """,
    '1.2.6': """
    Fixed a bug where field info was not extracted properly during dropshot mode.
    It was reporting 2 goals rather than the expected 140.
    """,
    '1.2.5': """
    ***************************************************
    *  Fix for dodge cancels / half flips! - ccman32  *
    ***************************************************
    
    Plus:
    - Changing the rendering strategy for 3D lines that go past the camera. Formerly it was
      "draw it, even though it's crazy sometimes", now it will be "don't draw it".
    - Showing the rate that inputs are received for each player index when you press the
      [home] key. Toggle back off with the [end] key.
    - Fixed a bug where party_member_bot could get influenced by real controller input.
    - Creating new presets in the GUI works better now.
    - Got rid of the libpng warning seen when using the GUI.
    - Giving specific error messages when cfg files are messed up.
    """,
    '1.2.2': """
    - Rearranged the GUI a bit, and made it load and track appearance configs more effectively.
    - Fixed bug where RUN button behavior in the GUI would not work after killing bots.
    """,
    '1.2.0': """
    - We now offer a 'RigidBodyTick' thanks to whatisaphone! It's a lower-level representation of
    physics data which updates at 120Hz and is not subject to interpolation. You can still make a 
    great bot without it, but this feature is quite nice for the scientists among us.
    
    See https://github.com/RLBot/RLBotPythonExample/wiki/Rigid-Body-Tick for more details!
    
    - Faster way to access ball prediction data in python. - Skyborg
    """,
    '1.1.3': """
    - Faster way to access ball prediction data in python. - Skyborg
    - Java bots will now shut down when the python framework quits. This has been necessary recently
    to avoid buggy situations.
    - Shutting down the python framework will no longer attempt to kill bots twice in a row.
    - Clicking on the "Run" button twice in a row in the GUI will no longer spawn duplicate processes.
    """,
    '1.1.2': """
    Faster way to access ball prediction data in python. - Skyborg
    """,
    '1.1.1': """
    You can now get information about the ball's status in Dropshot mode thanks to hallo_doei!
    Read all about it at https://github.com/RLBot/RLBot/wiki/Dropshot

    Other changes:
    - The loadout config for orange team is now respected again. - ccman32
    - Fixed a bug where the GUI would crash with a "KeyError". - hallo_doei
    - Avoiding and suppressing some game crashes, and also restoring the
      ability to get game tick data during replays and the postgame. - tarehart
    - Fixed a bug where bots would dodge when they intended to double jump. -tarehart
    """,
    '1.0.6': """
    The latest Rocket League patch broke dodges for our bots; this update fixes it.
    """,
    '1.0.5': """
    Maximum size for a render message has been decreased again because many people experienced
    errors related to memory access. The limit is now only double the original.
    """,
    '1.0.4': """
    - Maximum size for a render message has been increased by a factor of 100. This means you can
      draw a lot of lines at once without getting errors.
    - Boost amount for cars will now round up to the nearest integer, so 0.3% boost will now appear
      as 1 instead of 0.
    - Fixed a crash that would commonly happen after a match ends. As a side effect, you can no longer
      see up-to-date player data during instant replays.
    """,
    '1.0.3': """
    Time for the big 1.0 release! We actually left "beta" a long time ago so this isn't as big
    a milestone as the number implies, but we DO have two great new features!

    1. Setting game state. You can manipulate the position, velocity, etc of the ball and the cars!
    This can be a great help during bot development, and you can also get creative with it. Visit
    the wiki for details and documentation - https://github.com/RLBot/RLBot/wiki/Manipulating-Game-State
    Code written by hallo_doei, ccman32, and tarehart

    2. Ball prediction. We now provide a list of future ball positions based on chip's excellent
    physics modeling. Take advantage of this to do next-level wall reads, catches, and dribbles! You can
    read about the math involved here: https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/
    Note: currently the wall bounces are only accurate on the standard arena, not hoops or dropshot.
    Documentation and examples can be found here: https://github.com/RLBot/RLBot/wiki/Ball-Path-Prediction
    Code written by chip and tarehart

    Bonus:
     - You can now play on Salty Shores thanks to hallo_doei
     - Bug fix for people with spaces in their file path by Zaptive
     - Subprocess agent for future Rust support by whatisaphone
    """,
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
