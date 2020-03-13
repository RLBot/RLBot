# Store the version here so:
# 1) we don't load dependencies by storing it in __init__.py
# 2) we can import it in setup.py for the same reason
# 3) we can import it into your module module
# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package

__version__ = '1.37.2'

release_notes = {
    '1.37.2': """
    - Better on screen performance measurement for RLBot (hit home key).
    - Bots can now draw when the game is paused, and still move after goal explosions.
    """,
    '1.36.8': """
    Proper appearances for Psyonix bots thanks to Marvin, with an assist from r0bbi3!

    Also:
    - Improved error messages. - Will
    - Fixing bug when trying to spawn tons of cars. - tare
    - Starting on hivemind support classes. Stay tuned! - Will
    - Improving C# documentation. - Redox
    - Feature for loading RLBot-specific game settings (e.g. framerate cap). - L0laapk3
    - Fixed game_tick_packet.game_info.is_match_ended always false - Skyborg
    - Fixed human spawning. - tare
    - Making lockstep work smoother in Python. - tare
    - Lockstep option in old GUI. - Redox
    """,
    '1.35.8': """
    - Adding the Forbidden Temple stadium and a few others.
    - Adding a few custom quick chats.
    - Better support for loading levels that have no goals. - Skyborg
    - Reducing the frequency of python hot reload checks. - Marvin
    - Performance improvement related to logger. - Marvin
    - C# documentation improvements. - Redox
    - Providing a way to get autocomplete on the game tick packet.
    - Trying again to fix inconsistencies with has_wheel_contact.
    - Fixed bug that led to WrongProcessArgs error. - Will
    - Adding a flag to control agent reloads for training. - Marvin
    """,
    '1.34.5': """
    Mac support is here! https://github.com/RLBot/RLBot/wiki/Operating-System-Support

    Also:
    - Improving Remote RLBot so that multiple client computers can connect from behind
      the same IP address.
    - Fixing bug where bots would take a very long time to start if a human was in the
      match config.
    - Fixing input percentages and lockstep feature.
    - Fix inconsistencies with has_wheel_contact. - Kipje13
    """,
    '1.33.1': """
    Remote TCP functionality, primarily for classroom use.
    See https://github.com/RLBot/RLBot/wiki/Remote-RLBot for details!

    Minor updates:
     - Fixing a bug that makes RLBot stutter unpredictably.
    """,
    '1.32.1': """
    - You can specify your car's primary and secondary color swatches by the nearest
      RGB value instead of looking up the color id's on our wiki. You're still constrained
      to the normal color choices, don't get too excited!
      See https://github.com/RLBot/RLBot/wiki/Bot-Customization#colors for details.
    - The lockstep feature should be more reliable now.
    """,
    '1.31.1': """
    Hitbox offsets are now available in the GameTickPacket.
    This should make it possible to use hitboxes without hardcoding any values.

    - Fixes hitboxes issues after RL update.
    """,
    '1.30.2': """
    Kipje13 has a major speedup for rendering in python! You'll get the benefits
    automatically, but ask him for the details if you're curious.

    Also delivering fresher packets to python bots, for improved latency and
    consistency. This may affect bot behavior slightly, check your kickoffs!
    """,
    '1.29.0': """
    Python bots will now be able to specify their preferred tick rate. Do you like running at 120Hz?
    You'll need to add "maximum_tick_rate_preference = 120" to your config file! Example:
    https://github.com/RLBot/RLBot/blob/add379ab700d26f66ee31119a3b4e718a736f7aa/src/test/python/agents/atba/atba.cfg#L9
    The default will be for python bots to run at 60, since that's how most bots have been developed and tested.
    """,
    '1.28.3': """
    Linux Support!

    Kipje13 has really done it, you can run RLBot in Linux now :D
    - Tested in Ubuntu 18.04 with basic python bots, it works great.
    - All the latest features like lockstep are present.
    - This is early days, so many bots and languages won't work yet. Please think of this
      as an alpha and help us find the bugs. Most of the remaining work will be in the
      open source area of RLBot, so drop by #framework-dev if you want to contribute!

    More info at https://github.com/RLBot/RLBot/wiki/Operating-System-Support

    Additional fixes:
    - Open RL using Popen on Linux - cominixo
    - Fixed bug in Scratch manager and switched it to use structs.
    - Ability to save scratch bots over the websocket.
    """,
    '1.27.1': """
    Introducing lockstep mode--if you set enable_lockstep = True in rlbot.cfg, the
    framework will wait for outputs from all bots before advancing to the next frame.

    This feature brought to you by Redox!

    Other features:
    - No longer trying to configure Rocket League with .ini files, which was error-prone.
    """,
    '1.26.4': """
    Adding the ability to execute arbitrary console commands in Rocket League.
    See https://github.com/RLBot/RLBot/wiki/Console-Commands for details!

    Other features:
    - Adding a built-in version of the Scratch bot manager so we can push updates.
    - Adding an early-start system you can opt into if your bot is very slow to start.
      See https://github.com/RLBot/RLBot/wiki/Config-File-Documentation#early-start-system
    - Scratch bots can optionally open a browser-per-bot and pretend to be player 1 on the
      blue team. Good for tournaments!
    - Adding back gravity and game speed setting. - Redox
    """,
    '1.25.5': """
    - Added DummyRenderer, allowing its users to swallow all draw calls. - DomNomNom
    - Fixed a bug where player names with special characters would cause crashes.
    - Giving 'independent' bots more time to shut down.
    - Fixed performance problem with python hot reload for large directories. - RamenAndVitamins
    """,
    '1.24.0': """
    - Car hitbox data is now available for bots.
    - The ball info now includes the shape (sphere, cube, etc.) and size of the ball.
    - Hopefully reduces the amount of crashes when shutting down bot processes.
    """,
    '1.23.2': """
    - Added goal dimensions to field info. - Kipje13
    - Fixed bug where 'restart if different' doesn't start a match once the postgame timer expires.
    - Setting current working directory to the executable location for java and .net bots.
    - Bots can now include a logo! Either put a file called logo.png in the same folder as
      your bot cfg, OR specify logo_file = ... in your bot cfg in the same section as python_file.
      Dimensions of 400x300 are preferred. It will appear soon in RLBotGUI, and maybe on stream!
    """,
    '1.22.2': """
    Fixed the bug that stopped many bots from working after the 1.22.1 update.
    """,
    '1.22.1': """
    Bots can now retrieve the settings object used to launch the current match,
    which can tell you the map, mode, mutator settings, etc.

    Additional fixes:
    - Waiting longer for rlbot to connect.
    - Don't halt forever while waiting for valid packets.
    - Python hot reload watches all your files.
    """,
    '1.21.0': """
    - Latest ball touch now includes a player index value.
    - Fixed blue team colors.
    - Fixed loadout bug that caused incorrect antennas, etc.
    """,
    '1.20.1': """
    Added support for the awesome new game mode Spike Rush!

    To try it, set your mutators:
    Rumble = Spike Rush
    Respawn Time = 1 Second

    To retract your spikes, you have use_item available in your controls output!

    Additional fixes:
    - Will try harder to find an open port, to avoid 'std exception: listen' error.
    - Fixed a bug that prevented multiple .net bots from auto-starting. - Kipje13
    - Fixed a bug that prevented multiple java bots from auto-starting.
    """,
    '1.19.1': """
    Bots can now press the 'use item' button from Rumble mode!
    They don't know what item they have yet...
    """,
    '1.18.1': """
    Created a cleaner option for starting Java bots. Also:
    - seconds_elapsed will pause when the game is paused.
    - game_time_remaining has regained float precision.
    - unlimited_time will be 'true' when using that mutator.
    """,
    '1.17.3': """
    Quickchat is back!

    Kipje13 added quickchat support deep in the framework so bots will be able to
    read it across languages! Everything works exactly the same as before from the
    bot maker's perspective. Stay tuned for instructions on how to read quick
    chat for languages like C# and Java. https://github.com/RLBot/RLBot/wiki/Quickchat

    For now, the chat will use hacky rendering since we don't have official support yet.

    For richer communication with coordinates etc, check out
    https://github.com/RLBot/RLBot/wiki/Matchcomms

    Latest ball touch is also back!
    """,
    '1.16.5': """
    Communication to and between bots is now possible!
    See: https://github.com/RLBot/RLBot/wiki/Matchcomms

    - Support match communication (matchcomms). - DomNomNom
    - Warning when Rocket League is not running in -rlbot mode. - tarehart
    - Fix Python 3.6 compatibility. - DomNomNom
    - Restoring support for rectangle rendering - tarehart
    - The world_gravity_z value will be reported correctly again - tarehart
    - Warnings when you try to use unsupported aspects of state setting - tarehart
    - Avoid needing to manually click Steam confirmation about -rlbot mode. - DomNomNom
    - Brought back the stall mechanic. - tarehart
    """,

    '1.15.10': """
    Read all about our integration with the new Psyonix API!
    https://github.com/RLBot/RLBot/wiki/Psyonix-API-Notes

    Big thanks to Jared Cone and the whole team over at Psyonix!

    New since 1.15.7:
    - Steering will no longer affect dodge angle.
    - You can now specify whether the match should restart via rlbot.cfg.
      This will allow us to experiment with LAN matches.
    """,

    '1.15.7': """
    Integrating with official Psyonix API! Read all about it at
    https://github.com/RLBot/RLBot/wiki/Psyonix-API-Notes

    Big thanks to Jared Cone and the whole team over at Psyonix!

    Post-release fixes:
    - Fixing dodge angle
    - Support for rigid body tick (now including frame counts)
    - Restoring boost pickup timers
    - Rendering turned on by default
    - Possible to launch dropshot / hoops / etc
    - is_bot flag now set correctly
    - Bot performance percentages are back
    - Support for partial values in state setting
    - Fixing the is_super_sonic flag
    - Upgrading to the latest ball prediction code (thanks chip and Kipje13!)
    - Allow a human to play
    - Auto join spectate when there is no human player
    """,

    '1.14.12': """
    - Adding a way of starting matches using a flatbuffer message. - tarehart
    - More accurate get_output call frequency for python bots. - Marvin and chip
    - Fixing compilation of RLBotDotNet project with a breaking change. - tarehart
    - Pinning the psutil package to 5.5.0 to fix 'access denied', 'OSError'. - tarehart
    - Fixed for the friends update. - ccman32
    - Fix for psyonix bots never using boost. - tarehart
    - Avoid killing the parent process, e.g. the GUI, when subprocess agents retire. - tarehart
    - Make the GUI allow non-vital cfg sections to be missing. - tarehart
    - Max 64 bots / players. Be patient while the match is loading :) - skyborg
    - Fix quickchats creating more polling threads each reload. - DomNomNom and SauceTheBoss
    - Fix bot processes not ending when training ends. - DomNomNom
    """,

    '1.13.2': """
    - Fix accidental publishing of pypi package 1.13.1 - DomNomNom
    - Show MIT license in `pip show rlbot`. - DomNomNom
    """,

    '1.12.8': """
    - Support for passing an options dict to BotHelperProcesses. - tarehart
    - Python bots now wait until valid field info to call initialize_agent() - Marvin
    - Field info is no longer being updated each tick and is emptied out if we're not in a game. - Marvin and ccman32
    - Making the details section of bot config files more visible to python GUIs. - tarehart
    - Improved stability of the SetupManager. - DomNomNom
    - Added rendering capability to training exercises. - DomNomNom
    - Allow reading/writing of MatchConfig's including all its depenencies. - DomNomNom
    - Clear the screen when bots retire. - DomNomNom
    - Clear bot inputs when they retire. - DomNomNom
    - Improvements to the controller pass-through agent. - Kipje13 and chip
    - Fix for serialization of multiline values in config files. - tarehart
    """,

    '1.11.1': """
    - Added a new field called 'teams' to packet, which contains goals scored. - Marvin
    - Added team info to latest touch. - Marvin
    - Fix mistake that stopped C# bots from starting. Kipje13
    - GUI now saves relative paths. - Eastvillage
    """,

    '1.10.2': """
    - Bots can now see the match configuration using the new init_match_config method. - tarehart
    - Improved default loadout for bots. - Marvin
    """,

    '1.9.6': """
    - *Much* faster core dll initialization! - ccman32
    - Adding support for a training mode! Check out https://github.com/RLBot/RLBotTraining - DomNomNom
    - Allow the user to change the appearance of human and party-member bot agents via the GUI - r0bbi3
    - Added game speed info to game tick packet and the ability to modify it via state setting - Marvin
    - Make the game stop capturing the mouse cursor if only bots are playing - whatisaphone
    - Various quality-of-life improvements - DomNomNom
    - Match configuration refactoring to make new GUIs easier - tarehart
    """,

    '1.8.3': """
    - Allow SimpleControllerState initialization. - Marvin
    - Passing more params to subprocess agents. - whatisaphone
    - Made game data structs support comparison and repr in python. - DomNomNom
    - Fixing double-logging bug. - Marvin

    For whatisaphone's mouse cursor freedom, roll back to 1.8.2.
    """,

    '1.8.1': """
    - Ability to modify gravity via state setting. Ball prediction reacts properly, and bots are
      informed of the gravity in the game tick packet! - Marvin
    - Sorting the customization items in the GUI. - hallo-doei
    - Making logging more configurable. - Marvin
    - Fixing custom quick chats. - Marvin
    """,

    '1.7.0': """
    The big news: We now support painted items thanks to ccman32!
    See https://github.com/RLBot/RLBot/wiki/Bot-Customization for details.

    Other stuff:
    - Fix for tradeable items not displaying correctly after December update. - ccman32
    - Sending invalid controller inputs will no longer make your bot freeze,
      plus you'll get friendly warnings. - tarehart
    """,

    '1.6.5': """
    Support all subscriptable types for rendering. - Marvin
    """,

    '1.6.4': """
    Fixed compatibility with December update - ccman32
    Added a friendly warning about unsupported python versions - DomNomNom
    Stopped scaring people with statements about locked files - tarehart
    """,

    '1.6.1': """
    Fixed GUI crash when loading certain RLBot config files with relative paths for agents.
    Fixed agent preset loading to allow multiple agents to saved/loaded correctly if they have the same name. - ima9rd
    """,

    '1.6.0': """
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
    print(f"Version {__version__}")
    print(get_current_release_notes())
    print(get_help_text())
    print("")
